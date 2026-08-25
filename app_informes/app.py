# -*- coding: utf-8 -*-
"""Informe de Activos — escribí el nombre de un activo y generá un informe
educativo detallado, descargable en Word, con datos de Yahoo Finance,
Wikipedia y SEC EDGAR.

Ejecutar con:  streamlit run app.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
import catalogo  # noqa: E402
import indicadores as ind  # noqa: E402

import exportar_docx  # noqa: E402
import informe  # noqa: E402

st.set_page_config(page_title="Informe de Activos", page_icon="📄", layout="wide")

AZUL = "#2a78d6"
NARANJA = "#eb6834"

st.markdown("""
<style>
div[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #2a78d6 0%, #1c5cab 100%);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 0.9rem 1.4rem;
    font-size: 1.05rem;
    font-weight: 600;
    box-shadow: 0 3px 10px rgba(42, 120, 214, 0.35);
    transition: transform 0.12s ease, box-shadow 0.12s ease;
}
div[data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(135deg, #3987e5 0%, #2a78d6 100%);
    box-shadow: 0 5px 14px rgba(42, 120, 214, 0.45);
    transform: translateY(-1px);
    color: #ffffff;
}
div[data-testid="stDownloadButton"] button:active {
    transform: translateY(0);
}
div[data-testid="stDownloadButton"] button p {
    font-size: 1.05rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


def pct(x, dec=1):
    return "—" if x is None or pd.isna(x) else f"{x*100:.{dec}f}%"


def fmt_usd(v):
    if v is None:
        return "—"
    if abs(v) >= 1e9:
        return f"US$ {v/1e9:,.1f} mil millones"
    if abs(v) >= 1e6:
        return f"US$ {v/1e6:,.1f} millones"
    return f"US$ {v:,.0f}"


with st.sidebar:
    st.title("📄 Informe de Activos")
    st.caption(
        "Escribí el nombre o ticker de una acción, ETF, bono o cripto y "
        "generá un informe educativo completo — con datos de varias "
        "fuentes — que podés descargar como Word."
    )

    modo = st.radio("¿Cómo querés elegirlo?",
                    ["Escribir un ticker", "Elegir del catálogo"],
                    label_visibility="collapsed")
    if modo == "Elegir del catálogo":
        cat = st.selectbox("Tipo de inversión", list(catalogo.CATEGORIAS.keys()),
                           format_func=lambda c: f"{catalogo.CATEGORIAS[c]['emoji']} {c}")
        activos_cat = catalogo.activos_de(cat)
        ticker_input = st.selectbox(
            "Activo", list(activos_cat.keys()),
            format_func=lambda t: f"{activos_cat[t]['nombre']} ({t})")
    else:
        ticker_input = st.text_input(
            "Ticker (símbolo de Yahoo Finance)", value="AAPL",
            help="Ejemplos: AAPL, MSFT, VOO, VUAA.L (UCITS Londres), BTC-USD",
        ).strip().upper()

    generar = st.button("📄 Generar informe", type="primary",
                        use_container_width=True)

    st.divider()
    st.caption(
        "🔎 **Fuentes:** Yahoo Finance (precios y datos fundamentales), "
        "Wikipedia (contexto independiente) y SEC EDGAR (ganancias "
        "oficiales, para acciones de EE.UU.)."
    )
    st.caption(
        "⚠️ Herramienta educativa. No es asesoramiento financiero ni "
        "tributario."
    )

if "reporte" not in st.session_state:
    st.session_state["reporte"] = None

if generar and ticker_input:
    with st.spinner(f"Consultando Yahoo Finance, Wikipedia y SEC para {ticker_input}..."):
        st.session_state["reporte"] = informe.generar(ticker_input)

r = st.session_state["reporte"]

if r is None:
    st.title("📄 Informe de Activos")
    st.markdown(
        "Escribí un **ticker** en la barra lateral (por ejemplo `AAPL`, "
        "`VOO`, `VUAA.L`, `BTC-USD`) o elegí uno del catálogo, y tocá "
        "**Generar informe**."
    )
    st.markdown(
        "Vas a obtener un informe con:\n"
        "- Qué es el activo y cómo funciona, en lenguaje simple\n"
        "- Contexto independiente de **Wikipedia**\n"
        "- Cuánto rindió este año y su evolución histórica en gráfica\n"
        "- Para acciones de EE.UU.: ingresos y ganancias **oficiales de la "
        "SEC**, no solo de Yahoo Finance\n"
        "- Indicadores clave (volatilidad, caídas, P/E, dividendos...)\n"
        "- Impuestos estimados para un inversor uruguayo\n"
        "- **Descarga en Word** para guardar o compartir"
    )
    st.stop()

if "error" in r:
    st.error(r["error"])
    st.stop()

# ═══════════════════ Encabezado + descarga ═══════════════════
c1, c2 = st.columns([3, 1.3])
with c1:
    st.title(f"{r['nombre']} ({r['ticker']})")
    st.caption(f"{r['categoria'] or 'Sin categoría curada'} · "
              f"Precio actual: {r['precio_actual']:,.2f} {r['moneda']} · "
              f"Generado el {r['fecha_informe'].strftime('%d/%m/%Y')}")
with c2:
    st.write("")  # centra verticalmente el botón respecto al título
    docx_buf = exportar_docx.generar_docx(r)
    st.download_button(
        "📄⬇️  Descargar informe en Word", data=docx_buf,
        file_name=f"informe_{r['ticker']}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )
    st.caption("Archivo .docx listo para abrir en Word.")

st.warning(
    "⚠️ Este informe es una herramienta educativa. No constituye "
    "asesoramiento financiero ni una recomendación de compra o venta."
)

# ═══════════════════ 1. Qué es ═══════════════════
st.header("1. ¿Qué es y cómo funciona?")
edu = r["educativo"]
if edu["intro_categoria"]:
    st.info(edu["intro_categoria"])
st.write(edu["que_es"])
if edu["como_funciona"]:
    st.markdown("**Cómo gana dinero:**")
    st.write(edu["como_funciona"])

# ═══════════════════ 2. Wikipedia ═══════════════════
if r["wiki"]:
    st.header("2. Contexto independiente (Wikipedia)")
    st.write(r["wiki"]["extracto"])
    st.caption(f"Fuente: [Wikipedia — {r['wiki']['titulo']}]({r['wiki']['url']})")

# ═══════════════════ 3. Desempeño ═══════════════════
st.header("3. Desempeño de precio")
rend = r["rendimiento"]
d1, d2, d3 = st.columns(3)
d1.metric("En lo que va del año (YTD)", pct(rend["ytd"]))
d2.metric("Último año", pct(rend["un_anio"]))
d3.metric("Anualizado a 5 años (CAGR)", pct(rend["cagr_5y"]))

fig = go.Figure()
fig.add_trace(go.Scatter(x=r["precios"].index, y=r["precios"], name=r["nombre"],
                         line=dict(color=AZUL, width=2)))
if len(r["precios"]) >= 200:
    sma = r["precios"].rolling(200).mean()
    fig.add_trace(go.Scatter(x=sma.index, y=sma, name="Media 200 días",
                             line=dict(color=NARANJA, width=1.5, dash="dash")))
fig.update_layout(template="plotly_white", height=350,
                  margin=dict(l=10, r=10, t=30, b=10),
                  legend=dict(orientation="h", y=1.02))
st.plotly_chart(fig, use_container_width=True)

# ═══════════════════ 4. SEC ═══════════════════
if r["sec"]:
    st.header("4. Cuánto gana la empresa (fuente oficial: SEC EDGAR)")
    st.caption(
        "Estos son los datos que la propia empresa presentó ante el "
        "regulador bursátil de EE.UU. en su último balance anual (10-K) — "
        "una fuente independiente de Yahoo Finance."
    )
    sec = r["sec"]
    s1, s2 = st.columns(2)
    if sec["ingresos_valor"]:
        s1.metric(f"Ingresos (año fiscal {sec['ingresos_anio_fiscal']})",
                  fmt_usd(sec["ingresos_valor"]))
    if sec["ganancia_valor"]:
        s2.metric(f"Ganancia neta (año fiscal {sec['ganancia_anio_fiscal']})",
                  fmt_usd(sec["ganancia_valor"]))
    st.caption(f"Fuente: [SEC EDGAR]({sec['url']})")

# ═══════════════════ 5. Indicadores ═══════════════════
st.header("5. Indicadores clave")
ri, fu = r["riesgo"], r["fundamentales"]
i1, i2, i3, i4 = st.columns(4)
i1.metric("Volatilidad anual", pct(ri["volatilidad"]))
i2.metric("Peor caída (drawdown)", pct(ri["max_drawdown"]))
i3.metric("Ratio de Sharpe", "—" if ri["sharpe"] is None or pd.isna(ri["sharpe"]) else f"{ri['sharpe']:.2f}")
i4.metric("Dividendo (yield)", pct(fu["div_yield"]) if fu["div_yield"] else "No paga")
i5, i6, i7 = st.columns(3)
i5.metric("P/E", "—" if not fu["pe"] else f"{fu['pe']:.1f}")
i6.metric("Beta", "—" if not fu["beta"] else f"{fu['beta']:.2f}")
i7.metric("Capitalización de mercado", fmt_usd(fu["market_cap"]))

with st.expander("📚 ¿Qué significan estos indicadores?"):
    for clave, titulo in [("volatilidad", "Volatilidad"), ("drawdown", "Peor caída"),
                          ("sharpe", "Ratio de Sharpe"), ("dividendo", "Dividendo (yield)"),
                          ("pe", "P/E"), ("beta", "Beta")]:
        st.markdown(f"**{titulo}:** {ind.EXPLICACIONES[clave]}")

# ═══════════════════ 6. Impuestos ═══════════════════
st.header("6. Impuestos para un inversor uruguayo")
imp = r["impuesto"]
st.markdown("**Sobre dividendos/intereses:**")
t1, t2 = st.columns(2)
with t1:
    origen_tasa = imp.get("origen_tasa")
    st.metric("Retención en origen (EE.UU.)", pct(origen_tasa) if origen_tasa is not None else "No aplica")
    st.caption(imp.get("origen_motivo", "—"))
with t2:
    carga_total = imp.get("carga_total")
    st.metric("Carga fiscal total combinada", pct(carga_total) if carga_total is not None else "No definida")
    st.caption(imp.get("uy_nota", "—"))

gc_tasa = imp.get("gc_tasa")
st.markdown("**Sobre la ganancia de capital al vender:**")
st.metric("IRPF sobre la ganancia de capital",
          "No definido" if gc_tasa is None else pct(gc_tasa))
st.caption(imp.get("gc_nota", "—"))

# ═══════════════════ 7-8. Riesgos y perfil ═══════════════════
if edu["riesgos"] or edu["perfil"]:
    c1, c2 = st.columns(2)
    if edu["riesgos"]:
        with c1:
            st.header("7. Riesgos principales")
            st.write(edu["riesgos"])
    if edu["perfil"]:
        with c2:
            st.header("8. ¿Para qué perfil de inversor?")
            st.write(edu["perfil"])

st.divider()
fuentes_txt = ["Yahoo Finance — precios, dividendos y datos fundamentales"]
if r["wiki"]:
    fuentes_txt.append(f"Wikipedia — {r['wiki']['titulo']}")
if r["sec"]:
    fuentes_txt.append("SEC EDGAR — balance anual oficial (10-K)")
st.caption("**Fuentes consultadas:** " + " · ".join(fuentes_txt))
st.caption(
    "Este informe fue generado automáticamente con fines educativos. La "
    "información puede contener errores o estar desactualizada: verificá "
    "los datos antes de tomar una decisión de inversión."
)
