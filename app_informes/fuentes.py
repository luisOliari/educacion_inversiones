# -*- coding: utf-8 -*-
"""Recolección de datos de un activo desde varias fuentes independientes:

- Yahoo Finance (yfinance): precios históricos, dividendos, datos fundamentales.
- Wikipedia: descripción independiente de la empresa/activo, en español (con
  fallback a inglés), para contexto que no depende de un broker financiero.
- SEC EDGAR (sec.gov): ingresos y ganancias oficiales presentados ante el
  regulador de EE.UU., para empresas que cotizan allí. Es la fuente primaria
  que reportan las propias compañías, independiente de Yahoo Finance.

Cada función devuelve None (o un dict con 'disponible': False) si la fuente
no tiene datos para ese ticker, para que el informe se arme igual con lo que
sí se consiguió.
"""

import time

import requests
import yfinance as yf

USER_AGENT = "AppInformeInversiones/1.0 (uso educativo; contacto: oliariluis@gmail.com)"


# ═══════════════════════ Yahoo Finance ═══════════════════════

def yahoo_historia(ticker: str, periodo: str = "5y"):
    return yf.Ticker(ticker).history(period=periodo, auto_adjust=True)


def yahoo_info(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info or {}
    except Exception:
        info = {}
    return info


def yahoo_dividendos(ticker: str):
    try:
        return yf.Ticker(ticker).dividends
    except Exception:
        return None


# ═══════════════════════ Wikipedia ═══════════════════════

def _wikipedia_buscar(idioma: str, consulta: str) -> str | None:
    try:
        r = requests.get(
            f"https://{idioma}.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": consulta,
                    "format": "json", "srlimit": 1},
            headers={"User-Agent": USER_AGENT}, timeout=8,
        )
        r.raise_for_status()
        resultados = r.json().get("query", {}).get("search", [])
        return resultados[0]["title"] if resultados else None
    except Exception:
        return None


def wikipedia_resumen(consulta: str) -> dict | None:
    """Busca el artículo más relevante (primero en español, luego inglés) y
    devuelve su resumen + URL. None si no encontró nada razonable."""
    for idioma in ("es", "en"):
        titulo = _wikipedia_buscar(idioma, consulta)
        if not titulo:
            continue
        try:
            r = requests.get(
                f"https://{idioma}.wikipedia.org/api/rest_v1/page/summary/"
                + requests.utils.quote(titulo),
                headers={"User-Agent": USER_AGENT}, timeout=8,
            )
            if r.status_code != 200:
                continue
            datos = r.json()
            extracto = datos.get("extract", "")
            if not extracto or len(extracto) < 40:
                continue
            return {
                "titulo": datos.get("title", titulo),
                "extracto": extracto,
                "url": datos.get("content_urls", {}).get("desktop", {}).get("page"),
                "idioma": idioma,
            }
        except Exception:
            continue
    return None


# ═══════════════════════ SEC EDGAR (solo empresas de EE.UU.) ═══════════════

_CACHE_TICKERS_SEC = {}


def _sec_mapa_tickers() -> dict:
    global _CACHE_TICKERS_SEC
    if _CACHE_TICKERS_SEC:
        return _CACHE_TICKERS_SEC
    try:
        r = requests.get("https://www.sec.gov/files/company_tickers.json",
                         headers={"User-Agent": USER_AGENT}, timeout=10)
        r.raise_for_status()
        datos = r.json()
        _CACHE_TICKERS_SEC = {
            v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in datos.values()
        }
    except Exception:
        _CACHE_TICKERS_SEC = {}
    return _CACHE_TICKERS_SEC


def _sec_concepto(cik10: str, concepto: str) -> dict | None:
    try:
        r = requests.get(
            f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik10}/us-gaap/{concepto}.json",
            headers={"User-Agent": USER_AGENT}, timeout=10,
        )
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def _mejor_anual(datos_concepto: dict) -> tuple | None:
    """De un JSON de companyconcept, devuelve (año_fiscal, valor) del último
    10-K anual (form 10-K, fp FY) disponible, o None."""
    if not datos_concepto:
        return None
    unidades = datos_concepto.get("units", {})
    usd = unidades.get("USD", [])
    anuales = [x for x in usd if x.get("form") == "10-K" and x.get("fp") == "FY"
              and x.get("start") and x.get("end")]
    if not anuales:
        return None
    anuales.sort(key=lambda x: x["end"], reverse=True)
    mejor = anuales[0]
    return mejor["fy"], mejor["val"], mejor["end"]


def sec_datos_financieros(ticker: str) -> dict | None:
    """Ingresos y ganancia neta anual más reciente reportados ante la SEC.
    Solo funciona para empresas que cotizan en EE.UU. y presentan 10-K."""
    mapa = _sec_mapa_tickers()
    cik10 = mapa.get(ticker.upper())
    if not cik10:
        return None

    # varias empresas cambiaron de etiqueta contable (XBRL) con los años
    # (ej: Apple pasó de "Revenues" a "RevenueFromContract..." en 2018), así
    # que se prueban todas y se queda con el dato de cierre más reciente.
    candidatos = []
    for concepto in ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                     "SalesRevenueNet"):
        datos = _sec_concepto(cik10, concepto)
        r = _mejor_anual(datos) if datos else None
        if r:
            candidatos.append(r)
        time.sleep(0.15)
    ingresos = max(candidatos, key=lambda x: x[2]) if candidatos else None

    ganancia = None
    datos_gn = _sec_concepto(cik10, "NetIncomeLoss")
    if datos_gn:
        ganancia = _mejor_anual(datos_gn)

    if ingresos is None and ganancia is None:
        return None

    return {
        "cik": cik10,
        "ingresos_anio_fiscal": ingresos[0] if ingresos else None,
        "ingresos_valor": ingresos[1] if ingresos else None,
        "ingresos_fecha_cierre": ingresos[2] if ingresos else None,
        "ganancia_anio_fiscal": ganancia[0] if ganancia else None,
        "ganancia_valor": ganancia[1] if ganancia else None,
        "ganancia_fecha_cierre": ganancia[2] if ganancia else None,
        "url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik10}",
    }
