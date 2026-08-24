# -*- coding: utf-8 -*-
"""Cálculos de la cartera personal.

La cartera vive solo en la sesión del navegador de cada persona (st.session_state),
NUNCA en un archivo del servidor: así, si esta app se publica y varias personas
la usan a la vez desde el mismo link, la cartera de cada una queda privada y
nadie ve ni pisa la de otra. Para que persista entre visitas, cada persona la
descarga como CSV y la vuelve a subir la próxima vez (ver parsear_csv / a_csv).
"""

import io
import unicodedata

import pandas as pd

COLUMNAS = {
    "ticker": "Ticker",
    "cantidad": "Cantidad",
    "precio_compra": "Precio de compra (USD)",
}


def vacia() -> pd.DataFrame:
    return pd.DataFrame(columns=list(COLUMNAS))


def _a_numero(serie: pd.Series) -> pd.Series:
    """Convierte a número aceptando decimales con coma ('58,5' o '1.234,56')."""
    if serie.dtype == object:
        s = serie.astype(str).str.strip()
        con_coma = s.str.contains(",", na=False)
        # '1.234,56' -> quitar puntos de miles; '58,5' -> coma decimal
        s = s.where(~con_coma, s.str.replace(".", "", regex=False))
        s = s.str.replace(",", ".", regex=False)
        serie = s
    return pd.to_numeric(serie, errors="coerce")


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Quita filas vacías o inválidas y normaliza tickers."""
    df = df.copy()
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df = df[df["ticker"].ne("") & df["ticker"].ne("NONE") & df["ticker"].ne("NAN")]
    df["cantidad"] = _a_numero(df["cantidad"])
    df["precio_compra"] = _a_numero(df["precio_compra"])
    df = df[df["cantidad"] > 0]
    # si el mismo ticker aparece dos veces, combinar (promedio ponderado de compra)
    if df["ticker"].duplicated().any():
        def combinar(g):
            cant = g["cantidad"].sum()
            costo = (g["cantidad"] * g["precio_compra"].fillna(0)).sum()
            precio = costo / cant if costo > 0 else None
            return pd.Series({"cantidad": cant, "precio_compra": precio})
        df = df.groupby("ticker", as_index=False).apply(combinar, include_groups=False)
    return df.reset_index(drop=True)


# ── Importar / exportar CSV ───────────────────────────────────────────────

# nombres de columna aceptados (en minúsculas y sin tildes)
ALIAS = {
    "ticker": ["ticker", "symbol", "simbolo", "instrumento",
               "financial instrument", "financial instrument description"],
    "cantidad": ["cantidad", "quantity", "position", "posicion", "shares",
                 "qty", "units", "unidades"],
    "precio_compra": ["precio_compra", "precio de compra", "precio promedio",
                      "costo promedio", "avg price", "average price",
                      "avg cost", "average cost", "cost price", "cost basis price",
                      "avgprice", "purchase price"],
    "exchange": ["exchange", "listing exchange", "mercado", "bolsa"],
}

# mercados cuyo sufijo Yahoo se puede deducir del CSV de Interactive Brokers
SUFIJOS_YAHOO = {"LSE": ".L", "LSEETF": ".L"}


def _normalizar(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in s if not unicodedata.combining(c)).strip().lower()


def _buscar_columna(columnas: list[str], destino: str) -> str | None:
    normales = {_normalizar(c): c for c in columnas}
    for alias in ALIAS[destino]:
        if alias in normales:
            return normales[alias]
    return None


def parsear_csv(contenido: bytes) -> tuple[pd.DataFrame | None, str]:
    """Lee un CSV de posiciones (propio o exportado de un broker).

    Detecta separador, codificación y nombres de columna flexibles.
    Devuelve (DataFrame limpio | None, mensaje de error si falló).
    """
    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = contenido.decode("latin-1")

    # algunos exports traen líneas de encabezado antes de la tabla:
    # buscar la primera línea que parezca el encabezado real
    lineas = texto.splitlines()
    inicio = 0
    for i, linea in enumerate(lineas[:30]):
        campos = [_normalizar(x.strip('"')) for x in
                  linea.replace(";", ",").split(",")]
        if any(a in campos for a in ALIAS["ticker"]) and \
           any(a in campos for a in ALIAS["cantidad"]):
            inicio = i
            break

    try:
        df = pd.read_csv(io.StringIO("\n".join(lineas[inicio:])),
                         sep=None, engine="python")
    except Exception as e:
        return None, f"No pude leer el archivo como CSV ({e})."

    col_t = _buscar_columna(list(df.columns), "ticker")
    col_c = _buscar_columna(list(df.columns), "cantidad")
    col_p = _buscar_columna(list(df.columns), "precio_compra")
    col_e = _buscar_columna(list(df.columns), "exchange")

    if not col_t or not col_c:
        return None, (
            "No encontré las columnas necesarias. El CSV debe tener al menos "
            "una columna de ticker/símbolo y una de cantidad/posición "
            f"(encontré: {', '.join(df.columns.astype(str))})."
        )

    salida = pd.DataFrame({
        "ticker": df[col_t],
        "cantidad": df[col_c],
        "precio_compra": df[col_p] if col_p else None,
    })

    # sufijo de Yahoo para tickers de Londres si el CSV trae el mercado
    if col_e is not None:
        sufijos = df[col_e].astype(str).str.upper().map(SUFIJOS_YAHOO).fillna("")
        salida["ticker"] = salida["ticker"].astype(str).str.strip() + sufijos.values

    limpio = limpiar(salida)
    if limpio.empty:
        return None, "El archivo se leyó pero no quedó ninguna posición válida."
    return limpio, ""


def a_csv(df: pd.DataFrame) -> bytes:
    """Exporta la cartera al CSV propio de la app (re-importable)."""
    return df.to_csv(index=False).encode("utf-8-sig")


def curva_portafolio(precios_por_ticker: dict[str, pd.Series],
                     cantidades: dict[str, float]) -> pd.Series:
    """Valor histórico de la cartera actual (tenencias de hoy a precios de cada día).

    Alinea calendarios distintos (cripto opera fines de semana, Londres tiene
    otros feriados) usando la fecha y rellenando hacia adelante.
    """
    series = {}
    for t, p in precios_por_ticker.items():
        if p is None or p.empty:
            continue
        s = p.copy()
        s.index = pd.to_datetime([d.date() for d in s.index])
        s = s[~s.index.duplicated(keep="last")]
        series[t] = s * cantidades[t]
    if not series:
        return pd.Series(dtype=float)
    juntos = pd.concat(series, axis=1).sort_index().ffill()
    juntos = juntos.dropna()  # arranca cuando TODOS los activos tienen datos
    return juntos.sum(axis=1)
