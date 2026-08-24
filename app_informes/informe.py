# -*- coding: utf-8 -*-
"""Arma el contenido estructurado del informe de un activo, combinando
Yahoo Finance, Wikipedia y SEC EDGAR con la lógica educativa ya construida
en app_inversiones (catálogo, indicadores, impuestos)."""

import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
import catalogo          # noqa: E402
import impuestos as imp  # noqa: E402
import indicadores as ind  # noqa: E402

import fuentes  # noqa: E402


def _fmt_usd(v) -> str:
    if v is None:
        return "—"
    if abs(v) >= 1e9:
        return f"US$ {v/1e9:,.1f} mil millones"
    if abs(v) >= 1e6:
        return f"US$ {v/1e6:,.1f} millones"
    return f"US$ {v:,.0f}"


def _fmt_pct(v, dec=1) -> str:
    return "—" if v is None or pd.isna(v) else f"{v*100:.{dec}f}%"


def generar(ticker: str) -> dict:
    """Devuelve un dict con todo el contenido del informe, listo para
    mostrarse en pantalla o exportarse a Word."""
    ticker = ticker.strip().upper()

    historia = fuentes.yahoo_historia(ticker, "5y")
    if historia.empty:
        return {"error": f"No encontré datos para '{ticker}' en Yahoo Finance. "
                         "Verificá el símbolo (ETFs de Londres llevan .L, "
                         "cripto lleva -USD)."}

    precios = historia["Close"].dropna()
    info = fuentes.yahoo_info(ticker)
    dividendos = fuentes.yahoo_dividendos(ticker)
    ficha = catalogo.ACTIVOS.get(ticker)
    nombre = (ficha["nombre"] if ficha else info.get("longName") or
             info.get("shortName")) or ticker
    moneda = info.get("currency", "USD")
    categoria = ficha["categoria"] if ficha else None

    # ── Wikipedia (fuente independiente) ──
    consulta_wiki = nombre if len(nombre) > 3 else f"{nombre} {ticker}"
    wiki = fuentes.wikipedia_resumen(consulta_wiki)

    # ── SEC EDGAR (solo acciones/ETFs de EE.UU., no UCITS/cripto/bonos) ──
    es_candidato_sec = categoria in ("Acciones", "ETFs (EE.UU.)", None)
    sec = fuentes.sec_datos_financieros(ticker) if es_candidato_sec else None

    # ── rendimiento de precio ──
    precio_actual = precios.iloc[-1]
    inicio_anio = precios[precios.index.year == precios.index[-1].year]
    ytd = (precio_actual / inicio_anio.iloc[0] - 1) if len(inicio_anio) > 1 else None
    r_1y = precios.iloc[-1] / precios.iloc[max(0, len(precios) - 253)] - 1 \
        if len(precios) > 253 else None
    cagr_5y = ind.cagr(precios)

    # ── indicadores ──
    vol = ind.volatilidad_anual(precios)
    dd = ind.max_drawdown(precios)
    sharpe = ind.sharpe(precios)
    rsi = ind.rsi(precios) if len(precios) > 30 else None
    div_12m = (dividendos[dividendos.index > dividendos.index[-1] - pd.Timedelta(days=365)].sum()
              if dividendos is not None and not dividendos.empty else 0.0)
    div_yield = div_12m / precio_actual if div_12m > 0 else None

    # ── impuestos (para un inversor uruguayo) ──
    impuesto = imp.resumen(ticker, categoria, info.get("quoteType"))

    # ── contenido educativo curado, o genérico si no está en el catálogo ──
    if ficha:
        educativo = {
            "que_es": ficha["que_es"],
            "como_funciona": ficha["como_funciona"],
            "riesgos": ficha["riesgos"],
            "perfil": ficha["perfil"],
            "intro_categoria": catalogo.CATEGORIAS[categoria]["intro"],
        }
    else:
        resumen_yahoo = info.get("longBusinessSummary")
        educativo = {
            "que_es": resumen_yahoo or (wiki["extracto"] if wiki else
                      "No encontré una descripción curada para este activo."),
            "como_funciona": None,
            "riesgos": None,
            "perfil": None,
            "intro_categoria": None,
        }

    return {
        "ticker": ticker, "nombre": nombre, "moneda": moneda,
        "categoria": categoria, "fecha_informe": date.today(),
        "precio_actual": precio_actual, "precios": precios,
        "info": info, "educativo": educativo, "wiki": wiki, "sec": sec,
        "rendimiento": {"ytd": ytd, "un_anio": r_1y, "cagr_5y": cagr_5y},
        "riesgo": {"volatilidad": vol, "max_drawdown": dd, "sharpe": sharpe,
                   "rsi": rsi},
        "fundamentales": {
            "pe": info.get("trailingPE"), "beta": info.get("beta"),
            "market_cap": info.get("marketCap"),
            "div_yield": div_yield, "div_12m": div_12m,
        },
        "impuesto": impuesto,
        "fecha_consulta": date.today().isoformat(),
    }
