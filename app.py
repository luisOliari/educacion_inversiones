# -*- coding: utf-8 -*-
"""Mi Guía de Inversiones — app educativa para explorar activos antes de invertir.

Ejecutar con:  streamlit run app.py
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

import cartera
import catalogo
import impuestos
import indicadores as ind

# ── Paleta (validada para accesibilidad, modo claro) ──────────────────────
AZUL = "#2a78d6"      # serie principal
NARANJA = "#eb6834"   # serie secundaria / SMA 50
AQUA = "#1baf7a"      # SMA 200
ROJO = "#e34948"      # caídas / drawdown
GRIS_GRILLA = "#e1e0d9"
TINTA = "#0b0b0b"
TINTA_SEC = "#52514e"
# orden categórico fijo (paleta validada): las posiciones de la cartera
# toman siempre estos colores en este orden
PALETA_CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
              "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

st.set_page_config(page_title="Mi Guía de Inversiones", page_icon="📈", layout="wide")

PERIODOS = {
    "1 año": "1y",
    "3 años": "3y",
    "5 años": "5y",
    "10 años": "10y",
    "Máximo disponible": "max",
}


@st.cache_data(ttl=3600, show_spinner=False)
def bajar_historia(ticker: str, periodo: str) -> pd.DataFrame:
    t = yf.Ticker(ticker)
    df = t.history(period=periodo, auto_adjust=True)
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def bajar_info(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info or {}
    except Exception:
        info = {}
    return {
        "nombre": info.get("longName") or info.get("shortName"),
        "pe": info.get("trailingPE"),
        "beta": info.get("beta"),
        "moneda": info.get("currency"),
        "tipo": info.get("quoteType"),
        "resumen_sector": info.get("sector"),
    }


@st.cache_data(ttl=3600, show_spinner=False)
def dividendos_12m(ticker: str) -> float:
    """Suma de dividendos de los últimos 12 meses (en moneda del activo)."""
    try:
        divs = yf.Ticker(ticker).dividends
        if divs is None or divs.empty:
            return 0.0
        corte = divs.index[-1] - pd.Timedelta(days=365)
        return float(divs[divs.index > corte].sum())
    except Exception:
        return 0.0


def base_grafica(fig: go.Figure, titulo_y: str = "") -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        font=dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif",
                  color=TINTA_SEC),
        yaxis=dict(title=titulo_y, gridcolor=GRIS_GRILLA, zerolinecolor=GRIS_GRILLA),
        xaxis=dict(gridcolor=GRIS_GRILLA, showgrid=False),
        plot_bgcolor="#fcfcfb",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def pct(x: float | None, dec: int = 1) -> str:
    return "—" if x is None or pd.isna(x) else f"{x * 100:.{dec}f}%"


# ═══════════════════ Barra lateral: elegir la inversión ═══════════════════
with st.sidebar:
    st.title("📈 Mi Guía de Inversiones")
    st.caption("Aprendé sobre cada activo antes de invertir desde Interactive Brokers.")

    modo = st.radio("¿Cómo querés elegir?",
                    ["Explorar el catálogo", "Buscar por ticker"],
                    label_visibility="collapsed")

    if modo == "Explorar el catálogo":
        cat = st.selectbox(
            "Tipo de inversión",
            list(catalogo.CATEGORIAS.keys()),
            format_func=lambda c: f"{catalogo.CATEGORIAS[c]['emoji']} {c}",
        )
        activos_cat = catalogo.activos_de(cat)
        ticker = st.selectbox(
            "Activo",
            list(activos_cat.keys()),
            format_func=lambda t: f"{activos_cat[t]['nombre']} ({t})",
        )
    else:
        ticker = st.text_input(
            "Ticker (símbolo de Yahoo Finance)",
            value="AAPL",
            help="Ejemplos: AAPL, VOO, VUAA.L (UCITS Londres), BTC-USD",
        ).strip().upper()

    periodo_nombre = st.select_slider("Período histórico",
                                      list(PERIODOS.keys()), value="5 años")
    periodo = PERIODOS[periodo_nombre]

    st.divider()
    st.caption(
        "⚠️ **Esta app es educativa.** No es asesoramiento financiero ni una "
        "recomendación de compra o venta. Investigá y decidí por tu cuenta."
    )

# ═══════════════════ Descarga de datos ═══════════════════
if not ticker:
    st.info("Elegí un activo en la barra lateral para empezar.")
    st.stop()

with st.spinner(f"Bajando datos de {ticker}..."):
    df = bajar_historia(ticker, periodo)

if df.empty:
    st.error(
        f"No encontré datos para **{ticker}**. Verificá el símbolo "
        "(los UCITS de Londres llevan `.L`, las cripto `-USD`)."
    )
    st.stop()

precios = df["Close"].dropna()
info = bajar_info(ticker)
ficha = catalogo.ACTIVOS.get(ticker)

nombre = (ficha["nombre"] if ficha else info["nombre"]) or ticker
moneda = info["moneda"] or "USD"

# ═══════════════════ Encabezado ═══════════════════
precio_actual = precios.iloc[-1]
var_dia = precios.iloc[-1] / precios.iloc[-2] - 1 if len(precios) > 1 else 0

c1, c2, c3 = st.columns([3, 1, 1])
with c1:
    st.title(f"{nombre}")
    st.caption(f"Ticker: **{ticker}** · Moneda: {moneda} · Período mostrado: {periodo_nombre}")
with c2:
    st.metric("Último precio", f"{precio_actual:,.2f} {moneda}", pct(var_dia, 2))
with c3:
    st.metric(f"Rendimiento ({periodo_nombre})",
              pct(ind.rendimiento_total(precios)))

tab_inicio, tab_conocer, tab_grafica, tab_indicadores, tab_comparar, tab_cartera, tab_aprender = st.tabs(
    ["🏠 Inicio", "📖 Conocé el activo", "📊 Evolución histórica", "🔍 Indicadores",
     "⚖️ Comparar con el S&P 500", "💼 Mi cartera", "🎓 Aprender a invertir"]
)

# ═══════════════════ Tab 0: Inicio ═══════════════════
with tab_inicio:
    st.subheader("👋 Bienvenido/a a Mi Guía de Inversiones")
    st.markdown(
        "¿Alguna vez quisiste invertir pero no sabías **por dónde empezar**, o "
        "escuchaste nombres como *ETF*, *S&P 500* o *volatilidad* y sentiste que "
        "era otro idioma? Esta app existe para eso: **aprender de inversiones "
        "mientras las analizás con datos reales**, en lenguaje simple y sin "
        "necesidad de saber nada previo."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            "#### 🎓 Aprendé\n"
            "Cada activo viene explicado desde cero: **qué es, cómo gana "
            "dinero, qué riesgos tiene y para qué perfil sirve**. También hay "
            "una pestaña con los principios básicos para invertir bien."
        )
    with c2:
        st.markdown(
            "#### 🔍 Analizá\n"
            "Gráficas históricas reales, comparación contra el S&P 500 y los "
            "**indicadores que usan los profesionales** (rendimiento, riesgo, "
            "caídas máximas...), cada uno con su explicación en criollo."
        )
    with c3:
        st.markdown(
            "#### 💼 Seguí tu cartera\n"
            "Cargá tus posiciones a mano **o subí el CSV de tu broker** y la "
            "app te arma sola el valor actual, tus ganancias y pérdidas, y te "
            "avisa si estás poco diversificado."
        )

    st.divider()
    st.markdown(
        "#### 🚀 ¿Cómo empiezo? Tres pasos\n"
        "1. **Elegí un activo** en la barra lateral de la izquierda "
        "(si no la ves, tocá la flechita ↗ arriba a la izquierda). Podés "
        "explorar el catálogo por categorías o buscar cualquier ticker.\n"
        "2. **Recorré las pestañas de arriba**: primero *Conocé el activo* "
        "para entender qué es, después las gráficas y los indicadores.\n"
        "3. Cuando ya invertiste, **cargá tu cartera** en la pestaña "
        "*Mi cartera* para seguirla en un solo lugar.\n"
    )
    st.info(
        "🔒 **Tus datos son tuyos**: tu cartera se guarda solo en tu navegador "
        "durante la visita, nunca en un archivo compartido con otras personas "
        "que usen la app. Para no perderla al cerrar la pestaña, descargala "
        "como CSV y volvela a subir la próxima vez (pestaña *Mi cartera*)."
    )
    st.caption(
        "⚠️ Esta herramienta es educativa: te ayuda a entender antes de "
        "decidir, pero no es asesoramiento financiero ni recomienda comprar o "
        "vender."
    )

# ═══════════════════ Tab 1: Conocé el activo ═══════════════════
with tab_conocer:
    if ficha:
        cat = ficha["categoria"]
        st.info(f"**Sobre esta categoría — {catalogo.CATEGORIAS[cat]['emoji']} {cat}:** "
                + catalogo.CATEGORIAS[cat]["intro"])
        a, b = st.columns(2)
        with a:
            st.subheader("¿Qué es?")
            st.write(ficha["que_es"])
            st.subheader("¿Cómo funciona / cómo gana dinero?")
            st.write(ficha["como_funciona"])
        with b:
            st.subheader("Principales riesgos")
            st.write(ficha["riesgos"])
            st.subheader("¿Para qué perfil de inversor?")
            st.write(ficha["perfil"])
    else:
        st.write(
            f"**{nombre}** no está en el catálogo curado, pero acá tenés sus "
            "datos históricos e indicadores igual. "
            + (f"Sector: {info['resumen_sector']}." if info["resumen_sector"] else "")
        )
        st.info(
            "💡 Consejo: antes de invertir en algo que no conocés, asegurate de "
            "poder responder tres preguntas: ¿cómo gana dinero este activo?, "
            "¿por qué debería valer más en el futuro?, y ¿cuánto estoy "
            "dispuesto a verlo caer sin vender?"
        )

    # Lectura educativa del momento actual
    st.divider()
    st.subheader("🧭 Lectura del momento (educativa, no es una recomendación)")

    sma200 = precios.rolling(200).mean()
    tiene_sma = len(precios) >= 200 and not pd.isna(sma200.iloc[-1])
    valor_rsi = ind.rsi(precios) if len(precios) > 30 else None
    dd_actual = ind.serie_drawdown(precios).iloc[-1]

    lecturas = []
    if tiene_sma:
        if precio_actual > sma200.iloc[-1]:
            lecturas.append(
                "✅ El precio está **por encima** de su media de 200 días: la "
                "tendencia de fondo del último año es **alcista**.")
        else:
            lecturas.append(
                "⚠️ El precio está **por debajo** de su media de 200 días: la "
                "tendencia de fondo del último año es **bajista**. No significa "
                "que no se pueda invertir, pero conviene entender por qué cae.")
    if valor_rsi is not None and not pd.isna(valor_rsi):
        if valor_rsi > 70:
            lecturas.append(
                f"🔥 RSI en {valor_rsi:.0f}: subió muy rápido últimamente "
                "('sobrecomprado'). A corto plazo podría corregir; si invertís "
                "de a poco todos los meses, esto importa menos.")
        elif valor_rsi < 30:
            lecturas.append(
                f"🧊 RSI en {valor_rsi:.0f}: cayó muy rápido últimamente "
                "('sobrevendido'). A veces rebota, pero una caída fuerte también "
                "puede tener motivos de fondo: investigá antes.")
        else:
            lecturas.append(f"➖ RSI en {valor_rsi:.0f}: zona neutral, sin "
                            "excesos de corto plazo.")
    if dd_actual < -0.15:
        lecturas.append(
            f"📉 Hoy está un **{abs(dd_actual)*100:.0f}% por debajo** de su "
            "máximo del período. Para algunos es 'oportunidad de descuento', "
            "para otros una señal de problemas: depende de si el negocio de "
            "fondo sigue sano.")
    else:
        lecturas.append(
            f"📈 Está cerca de sus máximos del período (a {abs(dd_actual)*100:.0f}%). "
            "Comprar en máximos asusta, pero históricamente los índices pasan "
            "mucho tiempo marcando máximos nuevos.")

    for l in lecturas:
        st.markdown(l)

# ═══════════════════ Tab 2: Evolución histórica ═══════════════════
with tab_grafica:
    ver_medias = st.checkbox("Mostrar medias móviles (50 y 200 días)", value=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=precios.index, y=precios, name=nombre,
        line=dict(color=AZUL, width=2),
        hovertemplate="%{y:,.2f} " + moneda + "<extra></extra>",
    ))
    if ver_medias and len(precios) >= 50:
        sma50 = precios.rolling(50).mean()
        fig.add_trace(go.Scatter(
            x=sma50.index, y=sma50, name="Media 50 días",
            line=dict(color=NARANJA, width=2, dash="dot"),
            hovertemplate="%{y:,.2f}<extra></extra>",
        ))
    if ver_medias and len(precios) >= 200:
        sma200_g = precios.rolling(200).mean()
        fig.add_trace(go.Scatter(
            x=sma200_g.index, y=sma200_g, name="Media 200 días",
            line=dict(color=AQUA, width=2, dash="dash"),
            hovertemplate="%{y:,.2f}<extra></extra>",
        ))
    st.plotly_chart(base_grafica(fig, f"Precio ({moneda})"), use_container_width=True)

    with st.expander("📚 ¿Cómo leer esta gráfica?"):
        st.markdown(ind.EXPLICACIONES["sma"])

    st.subheader("Caídas desde máximos (drawdown)")
    dd = ind.serie_drawdown(precios) * 100
    fig_dd = go.Figure(go.Scatter(
        x=dd.index, y=dd, fill="tozeroy", name="Caída desde máximo",
        line=dict(color=ROJO, width=2),
        fillcolor="rgba(227,73,72,0.15)",
        hovertemplate="%{y:.1f}%<extra></extra>",
    ))
    st.plotly_chart(base_grafica(fig_dd, "Caída desde el máximo (%)"),
                    use_container_width=True)
    with st.expander("📚 ¿Qué me dice esta gráfica?"):
        st.markdown(
            "Muestra, en cada momento, cuánto estaba cayendo el activo respecto "
            "de su máximo anterior. Es la mejor forma de visualizar el 'dolor' "
            "que hubieras sentido invirtiendo: los pozos profundos son las "
            "crisis. " + ind.EXPLICACIONES["drawdown"])

    r_anuales = ind.retornos_anuales(precios)
    if len(r_anuales) >= 2:
        st.subheader("Rendimiento por año calendario")
        colores = [AZUL if v >= 0 else ROJO for v in r_anuales]
        fig_a = go.Figure(go.Bar(
            x=r_anuales.index.astype(str), y=r_anuales * 100,
            marker_color=colores, marker_line_width=0,
            hovertemplate="%{y:.1f}%<extra></extra>",
        ))
        st.plotly_chart(base_grafica(fig_a, "Rendimiento del año (%)"),
                        use_container_width=True)
        st.caption("Azul = año positivo · Rojo = año negativo. El primer y "
                   "último año pueden estar incompletos.")

# ═══════════════════ Tab 3: Indicadores ═══════════════════
with tab_indicadores:
    st.caption("Cada indicador tiene su explicación abajo. Los valores se "
               f"calculan sobre el período elegido ({periodo_nombre}).")

    v_cagr = ind.cagr(precios)
    v_vol = ind.volatilidad_anual(precios)
    v_dd = ind.max_drawdown(precios)
    v_sharpe = ind.sharpe(precios)
    v_rsi = ind.rsi(precios) if len(precios) > 30 else None
    divs = dividendos_12m(ticker)
    v_yield = divs / precio_actual if divs > 0 else None

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rendimiento anualizado (CAGR)", pct(v_cagr))
    m2.metric("Volatilidad anual", pct(v_vol))
    m3.metric("Peor caída del período", pct(v_dd))
    m4.metric("Ratio de Sharpe", "—" if pd.isna(v_sharpe) else f"{v_sharpe:.2f}")

    m5, m6, m7, m8 = st.columns(4)
    m5.metric("RSI (14 días)", "—" if v_rsi is None else f"{v_rsi:.0f}")
    m6.metric("Dividendo anual (yield)", pct(v_yield) if v_yield else "No paga")
    m7.metric("P/E (precio/ganancias)",
              f"{info['pe']:.1f}" if info["pe"] else "—")
    m8.metric("Beta (vs. mercado)",
              f"{info['beta']:.2f}" if info["beta"] else "—")

    st.divider()
    st.subheader("📚 ¿Qué significa cada indicador?")
    col_a, col_b = st.columns(2)
    items = [
        ("Rendimiento anualizado (CAGR)", "cagr"),
        ("Volatilidad", "volatilidad"),
        ("Peor caída (drawdown máximo)", "drawdown"),
        ("Ratio de Sharpe", "sharpe"),
        ("RSI", "rsi"),
        ("Dividendos (yield)", "dividendo"),
        ("P/E — precio/ganancias", "pe"),
        ("Beta", "beta"),
    ]
    for i, (titulo, clave) in enumerate(items):
        with (col_a if i % 2 == 0 else col_b):
            with st.expander(f"💡 {titulo}"):
                st.markdown(ind.EXPLICACIONES[clave])

    # ── impuestos: nominal vs. neto ──
    st.divider()
    st.subheader("💰 Ingreso nominal vs. neto (para un inversor en Uruguay)")
    st.caption(
        "El rendimiento de arriba es nominal. Acá se ve cuánto se descuenta "
        "en el camino: primero la retención de EE.UU. en origen, después el "
        "tratamiento en Uruguay."
    )

    imp = impuestos.resumen(ticker, ficha["categoria"] if ficha else None,
                            info["tipo"])

    ic1, ic2 = st.columns(2)
    with ic1:
        st.markdown("**1️⃣ Retención en origen (EE.UU.)**")
        tasa_o = imp["origen_tasa"]
        st.metric("Sobre los dividendos/intereses",
                  "No aplica" if tasa_o is None else pct(tasa_o))
        st.caption(imp["origen_motivo"])
    with ic2:
        st.markdown("**2️⃣ Impuesto en Uruguay (IRPF, con crédito tope 12%)**")
        carga_total = imp["carga_total"]
        st.metric("Carga fiscal total combinada",
                  "No definida" if carga_total is None else pct(carga_total))
        st.caption(imp["uy_nota"])

    if v_yield and carga_total is not None:
        bruto_pct = v_yield
        despues_origen_pct = bruto_pct * (1 - (tasa_o or 0))
        neto_final_pct = bruto_pct * (1 - carga_total)

        st.markdown("**Ejemplo con tu dividendo actual:**")
        f1, f2, f3 = st.columns(3)
        f1.metric("Dividendo nominal (bruto)", pct(bruto_pct))
        f2.metric("Te llega a la cuenta (después de EE.UU.)",
                  pct(despues_origen_pct),
                  pct(despues_origen_pct - bruto_pct, 2))
        f3.metric("Neto real (después de declarar en Uruguay)",
                  pct(neto_final_pct),
                  pct(neto_final_pct - despues_origen_pct, 2))
        st.caption(
            f"Sobre \\$10.000 invertidos, el dividendo nominal sería "
            f"\\${bruto_pct*10000:,.0f}/año; EE.UU. ya te retiene y te llega "
            f"\\${despues_origen_pct*10000:,.0f}, y lo que efectivamente te "
            f"queda una vez declarado en Uruguay ronda "
            f"\\${neto_final_pct*10000:,.0f}/año."
        )
    elif carga_total is not None:
        st.caption(f"{nombre} no reparte dividendos actualmente, así que no "
                   "hay retención que calcular sobre ingresos periódicos — "
                   "solo aplicaría si vendés con ganancia (ver nota abajo).")

    st.markdown("**3️⃣ Ganancia de capital al vender (distinto de los dividendos)**")
    gc1, gc2 = st.columns([1, 2])
    with gc1:
        st.metric("IRPF sobre la ganancia de capital",
                  "No definido" if imp["gc_tasa"] is None else pct(imp["gc_tasa"]))
    with gc2:
        st.caption(imp["gc_nota"])
    if imp["gc_tasa"]:
        st.caption(
            f"Ejemplo: si comprás a \\$1.000 y vendés a \\$1.500 (ganancia de "
            f"\\$500), en Uruguay pagarías \\${500*imp['gc_tasa']:,.0f} de "
            f"IRPF sobre esa ganancia (el {pct(imp['gc_tasa'])} completo, sin "
            "descuento por lo retenido en origen, porque en origen no te "
            "retuvieron nada sobre esta ganancia)."
        )

    st.warning(impuestos.ADVERTENCIA)

# ═══════════════════ Tab 4: Comparar con el S&P 500 ═══════════════════
with tab_comparar:
    st.caption(
        "El S&P 500 (las 500 mayores empresas de EE.UU.) es la vara de "
        "referencia: si una inversión rinde menos que el índice asumiendo más "
        "riesgo, probablemente convenga el índice."
    )
    if ticker in ("VOO", "SPY", "VUAA.L", "CSPX.L"):
        st.success("Este activo **es** el S&P 500 🙂 — compará otro activo "
                   "contra él desde la barra lateral.")
    else:
        spy = bajar_historia("VOO", periodo)["Close"].dropna()
        comunes = precios.index.intersection(spy.index)
        if len(comunes) < 30:
            # activos con calendarios distintos (cripto, Londres): alinear por fecha
            p1 = precios.copy(); p1.index = p1.index.date
            p2 = spy.copy(); p2.index = p2.index.date
            comunes = p1.index.intersection(p2.index)
            serie_a, serie_b = p1.loc[comunes], p2.loc[comunes]
        else:
            serie_a, serie_b = precios.loc[comunes], spy.loc[comunes]

        base_a = serie_a / serie_a.iloc[0] * 10000
        base_b = serie_b / serie_b.iloc[0] * 10000

        fig_c = go.Figure()
        fig_c.add_trace(go.Scatter(
            x=list(base_a.index), y=base_a, name=nombre,
            line=dict(color=AZUL, width=2),
            hovertemplate="$%{y:,.0f}<extra></extra>"))
        fig_c.add_trace(go.Scatter(
            x=list(base_b.index), y=base_b, name="S&P 500 (VOO)",
            line=dict(color=NARANJA, width=2),
            hovertemplate="$%{y:,.0f}<extra></extra>"))
        st.plotly_chart(
            base_grafica(fig_c, "Valor de $10.000 invertidos (USD)"),
            use_container_width=True)

        fin_a, fin_b = base_a.iloc[-1], base_b.iloc[-1]
        st.markdown(
            f"**\\$10.000 invertidos hace {periodo_nombre.lower()}** hoy serían "
            f"**\\${fin_a:,.0f}** en {nombre} y **\\${fin_b:,.0f}** en el S&P 500."
        )

        t1, t2 = st.columns(2)
        with t1:
            st.metric(f"CAGR de {nombre}", pct(ind.cagr(serie_a)))
            st.metric(f"Volatilidad de {nombre}", pct(ind.volatilidad_anual(serie_a)))
            st.metric(f"Peor caída de {nombre}", pct(ind.max_drawdown(serie_a)))
        with t2:
            st.metric("CAGR del S&P 500", pct(ind.cagr(serie_b)))
            st.metric("Volatilidad del S&P 500", pct(ind.volatilidad_anual(serie_b)))
            st.metric("Peor caída del S&P 500", pct(ind.max_drawdown(serie_b)))

        with st.expander("📚 ¿Cómo interpreto esta comparación?"):
            st.markdown(
                "- Si el activo **rindió más** que el índice pero con **mucha más "
                "volatilidad y caídas**, el rendimiento extra fue el 'pago' por "
                "aguantar más riesgo.\n"
                "- Si **rindió menos con más riesgo**, fue objetivamente peor "
                "inversión en ese período.\n"
                "- La mayoría de los profesionales no le gana al S&P 500 a 10 "
                "años. Por eso la estrategia base más recomendada para "
                "principiantes es comprar el índice todos los meses y dejar que "
                "el interés compuesto trabaje."
            )

# ═══════════════════ Tab 5: Mi cartera ═══════════════════
with tab_cartera:
    st.subheader("💼 Mis posiciones")
    st.caption(
        "Cargá lo que tenés en Interactive Brokers: ticker, cantidad de "
        "unidades y tu precio de compra promedio en USD. Se admiten "
        "fracciones (ej: 0.5 acciones). Agregá filas con el ➕ de la tabla. "
        "Los cambios quedan guardados mientras tengas esta pestaña abierta; "
        "para no perderlos al cerrarla, descargala como CSV (abajo) y la "
        "próxima vez la volvés a subir."
    )

    st.session_state.setdefault("cartera_df", cartera.vacia())
    st.session_state.setdefault("version_editor", 0)

    with st.expander("📥 Importar desde CSV (Interactive Brokers u otro)"):
        st.markdown(
            "Subí un CSV con tus posiciones y la app arma la cartera sola. "
            "Sirve el export de **Interactive Brokers** (Portfolio → exportar) "
            "o cualquier CSV con una columna de *ticker/símbolo*, una de "
            "*cantidad/posición* y, opcionalmente, el *precio promedio de "
            "compra*. Detecta los nombres de columna automáticamente.\n\n"
            "💡 Ojo con los símbolos: los ETFs de Londres necesitan el sufijo "
            "`.L` (VUAA → VUAA.L) y las cripto `-USD`. Si el CSV trae la "
            "columna del mercado (exchange), el sufijo de Londres se agrega solo."
        )
        archivo = st.file_uploader("Elegí el archivo", type=["csv", "txt"],
                                   label_visibility="collapsed")
        if archivo is not None:
            importada, error_csv = cartera.parsear_csv(archivo.getvalue())
            if importada is None:
                st.error(error_csv)
            else:
                st.markdown(f"Encontré **{len(importada)} posiciones**:")
                st.dataframe(importada, use_container_width=True,
                             hide_index=True)
                if st.button("✅ Usar esta cartera (reemplaza la actual)"):
                    st.session_state["cartera_df"] = importada
                    st.session_state["version_editor"] += 1
                    st.rerun()

    editada = st.data_editor(
        st.session_state["cartera_df"],
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_cartera_{st.session_state['version_editor']}",
        column_config={
            "ticker": st.column_config.TextColumn(
                "Ticker", help="Símbolo de Yahoo Finance: AAPL, VUAA.L, BTC-USD..."),
            "cantidad": st.column_config.NumberColumn(
                "Cantidad", min_value=0.0, format="%.4f"),
            "precio_compra": st.column_config.NumberColumn(
                "Precio de compra (USD)", min_value=0.0, format="%.2f",
                help="Tu precio promedio de compra por unidad. Opcional: "
                     "sin él no se calcula tu ganancia, pero sí el valor actual."),
        },
    )
    st.session_state["cartera_df"] = editada
    posiciones = cartera.limpiar(editada)

    if not posiciones.empty:
        st.download_button(
            "⬇️ Descargar mi cartera en CSV",
            data=cartera.a_csv(posiciones),
            file_name="mi_cartera.csv",
            mime="text/csv",
            help="Para no perderla al cerrar la pestaña: la volvés a subir "
                 "la próxima vez con 'Importar desde CSV'.",
        )

    if posiciones.empty:
        st.info(
            "Todavía no cargaste posiciones. Ejemplo: ticker `VUAA.L`, "
            "cantidad `10`, precio de compra `95.50`."
        )
    else:
        # ── precios actuales y valor de cada posición ──
        filas = []
        historias = {}
        errores = []
        with st.spinner("Bajando precios de tu cartera..."):
            for _, pos in posiciones.iterrows():
                t = pos["ticker"]
                h = bajar_historia(t, periodo)
                if h.empty:
                    errores.append(t)
                    continue
                cierre = h["Close"].dropna()
                historias[t] = cierre
                precio_hoy = cierre.iloc[-1]
                valor = precio_hoy * pos["cantidad"]
                costo = (pos["precio_compra"] * pos["cantidad"]
                         if pd.notna(pos["precio_compra"]) else None)
                ficha_pos = catalogo.ACTIVOS.get(t)
                filas.append({
                    "Ticker": t,
                    "Nombre": ficha_pos["nombre"] if ficha_pos else t,
                    "Categoría": ficha_pos["categoria"] if ficha_pos else "Otros",
                    "Cantidad": pos["cantidad"],
                    "Precio hoy": precio_hoy,
                    "Valor actual": valor,
                    "Costo": costo,
                    "Ganancia": valor - costo if costo else None,
                    "Ganancia %": (valor / costo - 1) if costo else None,
                })
        if errores:
            st.warning("No encontré datos para: " + ", ".join(errores)
                       + ". Revisá esos tickers.")

        if filas:
            tabla = pd.DataFrame(filas)
            valor_total = tabla["Valor actual"].sum()
            costo_total = tabla["Costo"].dropna().sum()
            tabla["Peso %"] = tabla["Valor actual"] / valor_total

            r1, r2, r3 = st.columns(3)
            r1.metric("Valor total de la cartera", f"US$ {valor_total:,.0f}")
            if costo_total > 0:
                gan_total = tabla["Ganancia"].dropna().sum()
                r2.metric("Ganancia / pérdida total", f"US$ {gan_total:,.0f}",
                          pct(gan_total / costo_total, 1))
            r3.metric("Cantidad de posiciones", f"{len(tabla)}")

            st.dataframe(
                tabla[["Ticker", "Nombre", "Categoría", "Cantidad",
                       "Precio hoy", "Valor actual", "Ganancia",
                       "Ganancia %", "Peso %"]],
                use_container_width=True, hide_index=True,
                column_config={
                    "Cantidad": st.column_config.NumberColumn(format="%.4f"),
                    "Precio hoy": st.column_config.NumberColumn(format="$%.2f"),
                    "Valor actual": st.column_config.NumberColumn(format="$%.0f"),
                    "Ganancia": st.column_config.NumberColumn(format="$%.0f"),
                    "Ganancia %": st.column_config.NumberColumn(format="percent"),
                    "Peso %": st.column_config.NumberColumn(format="percent"),
                },
            )

            # ── composición ──
            st.subheader("¿Cómo está repartida mi cartera?")
            orden = tabla.sort_values("Valor actual", ascending=True)
            colores_pos = {t: PALETA_CAT[i % len(PALETA_CAT)]
                           for i, t in enumerate(tabla["Ticker"])}
            g1, g2 = st.columns(2)
            with g1:
                fig_p = go.Figure(go.Bar(
                    x=orden["Peso %"] * 100, y=orden["Ticker"],
                    orientation="h",
                    marker_color=[colores_pos[t] for t in orden["Ticker"]],
                    marker_line_width=0,
                    text=[f"{v*100:.1f}%" for v in orden["Peso %"]],
                    textposition="outside",
                    hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
                ))
                fig_p.update_layout(title="Por activo",
                                    xaxis_title="Peso en la cartera (%)")
                st.plotly_chart(base_grafica(fig_p), use_container_width=True)
            with g2:
                por_cat = (tabla.groupby("Categoría")["Valor actual"].sum()
                           .sort_values())
                fig_cat = go.Figure(go.Bar(
                    x=por_cat / valor_total * 100, y=por_cat.index,
                    orientation="h", marker_color=AZUL, marker_line_width=0,
                    text=[f"{v/valor_total*100:.1f}%" for v in por_cat],
                    textposition="outside",
                    hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
                ))
                fig_cat.update_layout(title="Por tipo de inversión",
                                      xaxis_title="Peso en la cartera (%)")
                st.plotly_chart(base_grafica(fig_cat), use_container_width=True)

            # ── evolución histórica de la cartera ──
            st.subheader(f"Evolución de mi cartera ({periodo_nombre})")
            cantidades = dict(zip(posiciones["ticker"], posiciones["cantidad"]))
            curva = cartera.curva_portafolio(historias, cantidades)
            if len(curva) > 30:
                spy_c = bajar_historia("VOO", periodo)["Close"].dropna()
                spy_c.index = pd.to_datetime([d.date() for d in spy_c.index])
                spy_alineado = spy_c.reindex(curva.index).ffill().dropna()
                spy_norm = (spy_alineado / spy_alineado.iloc[0]
                            * curva.loc[spy_alineado.index[0]])

                fig_ev = go.Figure()
                fig_ev.add_trace(go.Scatter(
                    x=curva.index, y=curva, name="Mi cartera",
                    line=dict(color=AZUL, width=2),
                    hovertemplate="US$ %{y:,.0f}<extra></extra>"))
                fig_ev.add_trace(go.Scatter(
                    x=spy_norm.index, y=spy_norm,
                    name="Si hubiera sido todo S&P 500",
                    line=dict(color=NARANJA, width=2, dash="dot"),
                    hovertemplate="US$ %{y:,.0f}<extra></extra>"))
                st.plotly_chart(base_grafica(fig_ev, "Valor (USD)"),
                                use_container_width=True)
                st.caption(
                    "⚠️ La curva supone que tus tenencias **actuales** se "
                    "mantuvieron todo el período (no considera cuándo compraste "
                    "cada una). Sirve para ver cómo se habría comportado tu mezcla "
                    "actual, no tu rendimiento real histórico. La línea punteada "
                    "muestra el mismo capital inicial invertido solo en el índice."
                )

                e1, e2, e3 = st.columns(3)
                e1.metric("CAGR de la mezcla", pct(ind.cagr(curva)))
                e2.metric("Volatilidad de la mezcla", pct(ind.volatilidad_anual(curva)))
                e3.metric("Peor caída de la mezcla", pct(ind.max_drawdown(curva)))

            # ── lectura educativa de diversificación ──
            st.subheader("🧭 Lectura de tu diversificación (educativa)")
            avisos = []
            peso_max = tabla["Peso %"].max()
            pos_max = tabla.loc[tabla["Peso %"].idxmax(), "Ticker"]
            es_indice = tabla.loc[tabla["Peso %"].idxmax(), "Categoría"].startswith("ETF")
            if peso_max > 0.30 and not es_indice:
                avisos.append(
                    f"⚠️ **{pos_max}** pesa el {peso_max*100:.0f}% de tu cartera. "
                    "Concentrar tanto en un solo activo (que no sea un fondo "
                    "diversificado) hace que tu resultado dependa de una sola "
                    "apuesta.")
            peso_cripto = tabla.loc[tabla["Categoría"] == "Criptomonedas",
                                    "Valor actual"].sum() / valor_total
            if peso_cripto > 0.10:
                avisos.append(
                    f"⚠️ Las criptomonedas son el {peso_cripto*100:.0f}% de tu "
                    "cartera. Por su volatilidad extrema, la sugerencia educativa "
                    "habitual es mantenerlas por debajo del 5-10%.")
            n_cats = tabla["Categoría"].nunique()
            if n_cats == 1 and len(tabla) <= 2 and not es_indice:
                avisos.append(
                    "⚠️ Toda tu cartera está en un solo tipo de activo y pocas "
                    "posiciones. Un ETF diversificado como base reduciría mucho "
                    "el riesgo.")
            if not avisos:
                avisos.append(
                    "✅ No veo señales evidentes de concentración excesiva. "
                    "Recordá revisar también los solapamientos: VOO, VUAA y CSPX "
                    "son el mismo índice, tenerlos juntos no diversifica.")
            for a in avisos:
                st.markdown(a)
            st.caption("Esto es una lectura automática con reglas generales de "
                       "educación financiera, no un análisis personalizado.")

            # ── impuestos de la cartera: dividendos nominales vs. netos ──
            st.subheader("💰 Dividendos de tu cartera: nominal vs. neto estimado")
            filas_div = []
            for _, pos in posiciones.iterrows():
                t = pos["ticker"]
                if t not in historias:
                    continue
                div_unit = dividendos_12m(t)
                if div_unit <= 0:
                    continue
                ficha_pos = catalogo.ACTIVOS.get(t)
                info_pos = bajar_info(t)
                imp_pos = impuestos.resumen(
                    t, ficha_pos["categoria"] if ficha_pos else None,
                    info_pos["tipo"])
                bruto = div_unit * pos["cantidad"]
                carga = imp_pos["carga_total"]
                neto = bruto * (1 - (carga or 0))
                filas_div.append({"Ticker": t, "Bruto anual (US$)": bruto,
                                  "Neto estimado anual (US$)": neto})

            if filas_div:
                tabla_div = pd.DataFrame(filas_div)
                total_bruto = tabla_div["Bruto anual (US$)"].sum()
                total_neto = tabla_div["Neto estimado anual (US$)"].sum()
                d1, d2, d3 = st.columns(3)
                d1.metric("Dividendos nominales/año", f"US$ {total_bruto:,.0f}")
                d2.metric("Neto estimado/año", f"US$ {total_neto:,.0f}")
                d3.metric("Se va en el camino",
                          f"US$ {total_bruto - total_neto:,.0f}",
                          pct(-(total_bruto - total_neto) / total_bruto
                              if total_bruto else 0, 0))
                st.dataframe(tabla_div, use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Bruto anual (US$)": st.column_config.NumberColumn(format="$%.0f"),
                                "Neto estimado anual (US$)": st.column_config.NumberColumn(format="$%.0f"),
                            })
                st.caption(
                    "Efecto combinado de la retención de origen y el IRPF "
                    "uruguayo (12% con crédito, tope 12%) sobre "
                    "dividendos/intereses únicamente. La ganancia de "
                    "capital al vender se calcula aparte, abajo."
                )
            else:
                st.caption("Ninguna de tus posiciones reparte dividendos "
                          "actualmente, así que no hay retención que estimar "
                          "sobre ingresos periódicos.")

            # ── impuesto sobre la ganancia de capital no realizada ──
            st.subheader("💰 Si vendieras hoy: impuesto sobre la ganancia de capital")
            con_costo = tabla.dropna(subset=["Costo"]).copy()
            con_ganancia = con_costo[con_costo["Ganancia"] > 0]
            if con_ganancia.empty:
                st.caption(
                    "Ninguna posición con precio de compra cargado tiene "
                    "ganancia hoy, así que no habría IRPF que pagar si "
                    "vendieras en este momento."
                )
            else:
                filas_gc = []
                for _, fila in con_ganancia.iterrows():
                    t = fila["Ticker"]
                    ficha_pos = catalogo.ACTIVOS.get(t)
                    info_pos = bajar_info(t)
                    imp_pos = impuestos.resumen(
                        t, ficha_pos["categoria"] if ficha_pos else None,
                        info_pos["tipo"])
                    tasa_gc = imp_pos["gc_tasa"]
                    if not tasa_gc:
                        continue
                    filas_gc.append({
                        "Ticker": t, "Ganancia no realizada (US$)": fila["Ganancia"],
                        "IRPF si vendés (12%, US$)": fila["Ganancia"] * tasa_gc,
                    })
                if filas_gc:
                    tabla_gc = pd.DataFrame(filas_gc)
                    total_gan = tabla_gc["Ganancia no realizada (US$)"].sum()
                    total_irpf = tabla_gc["IRPF si vendés (12%, US$)"].sum()
                    g1, g2 = st.columns(2)
                    g1.metric("Ganancia no realizada (posiciones en verde)",
                              f"US$ {total_gan:,.0f}")
                    g2.metric("IRPF si vendieras todo hoy (12%)",
                              f"US$ {total_irpf:,.0f}")
                    st.dataframe(tabla_gc, use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Ganancia no realizada (US$)": st.column_config.NumberColumn(format="$%.0f"),
                                    "IRPF si vendés (12%, US$)": st.column_config.NumberColumn(format="$%.0f"),
                                })
                st.caption(
                    "Esto **no es un impuesto que debas hoy** — recién se "
                    "genera si vendés y realizás la ganancia. Se paga "
                    "completo (12%, sin descuento) porque en origen no hay "
                    "retención sobre la ganancia de capital que acreditar. "
                    "No incluye pérdidas de otras posiciones ni posibles "
                    "compensaciones entre ganancias y pérdidas del año. "
                    + impuestos.ADVERTENCIA
                )

# ═══════════════════ Tab 6: Aprender ═══════════════════
with tab_aprender:
    st.subheader("Los 7 principios que más importan (antes que cualquier indicador)")
    principios = [
        ("1. El interés compuesto es tu superpoder",
         "Invertir \\$300 por mes al 8% anual da ~\\$45.000 en 10 años, ~\\$150.000 en "
         "20 y ~\\$450.000 en 30. La variable más importante no es elegir la acción "
         "perfecta: es **empezar temprano y ser constante**."),
        ("2. Diversificar es lo único gratis",
         "Ninguna empresa es segura (pregúntale a los accionistas de Kodak o "
         "Nokia). Un ETF de índice te da cientos de empresas de una vez: si una "
         "quiebra, casi ni lo notás. Concentrar en 1-2 acciones es especular, "
         "no invertir."),
        ("3. El tiempo en el mercado le gana al timing",
         "Nadie sabe si mañana sube o baja, ni los profesionales. Los días de "
         "mayor subida suelen venir pegados a los de mayor caída: quien sale y "
         "entra suele perderse lo mejor. Comprar todos los meses un monto fijo "
         "(DCA) elimina la necesidad de adivinar."),
        ("4. Los costos e impuestos importan muchísimo",
         "Un 1% anual de comisiones parece poco, pero a 30 años se come ~25% de "
         "tu patrimonio final. Por eso los ETFs de bajo costo (0,03-0,20%) son la "
         "base. Y desde Uruguay, los UCITS de acumulación evitan la retención "
         "del 30% sobre dividendos de EE.UU. (mirá la sección 💰 en la "
         "pestaña *Indicadores* de cada activo para el detalle nominal vs. neto)."),
        ("5. Tu peor enemigo sos vos en pánico",
         "El mercado cae 30-50% una o dos veces por década. Es normal y siempre "
         "pasó. El error que arruina inversores no es la caída: es **vender "
         "durante** la caída. Invertí solo plata que no necesites por años."),
        ("6. Si no lo entendés, no lo compres",
         "Regla de Warren Buffett. Si no podés explicar en dos frases cómo gana "
         "dinero el activo, todavía no es para vos. Esta app existe justamente "
         "para eso."),
        ("7. Primero el orden: fondo de emergencia y deudas",
         "Antes de invertir: tené 3-6 meses de gastos en efectivo disponible y "
         "cancelá deudas caras (tarjetas). Invertir con deudas al 40% anual no "
         "tiene sentido matemático."),
    ]
    for titulo, texto in principios:
        with st.expander(f"**{titulo}**"):
            st.markdown(texto)

    st.divider()
    st.subheader("¿Cómo armar una primera cartera? (ejemplos educativos)")
    st.markdown(
        "Estos son **modelos clásicos de referencia** que se estudian en "
        "finanzas personales — no una recomendación para tu caso:\n\n"
        "| Perfil | Ejemplo clásico | Idea |\n"
        "|---|---|---|\n"
        "| Simple total | 100% VWRA (todo el mundo) | Un solo fondo, máxima diversificación |\n"
        "| Clásico crecimiento | 80% acciones (VUAA/IWDA) + 20% bonos (BND/AGGU) | Crece fuerte, amortigua algo |\n"
        "| Balanceado 60/40 | 60% acciones + 40% bonos | El estándar histórico de riesgo medio |\n"
        "| Con 'picante' | 85% índice + 10% acciones elegidas + 5% cripto | La base indexada, el resto para aprender |\n\n"
        "La proporción de bonos suele subir con la edad o con la cercanía del "
        "objetivo (ej: comprar una casa en 5 años)."
    )

    st.divider()
    st.subheader("Errores típicos del principiante")
    st.markdown(
        "- Comprar lo que subió mucho ayer (perseguir modas)\n"
        "- Vender en pánico durante una caída\n"
        "- Revisar la cartera todos los días (más miradas = peores decisiones)\n"
        "- Poner todo en una sola acción 'segura'\n"
        "- Confundir suerte de corto plazo con habilidad\n"
        "- Invertir el fondo de emergencia\n"
        "- Copiar carteras de influencers sin entender qué compran"
    )
    st.caption(
        "⚠️ Recordatorio final: esta app es una herramienta de estudio. Ningún "
        "contenido constituye asesoramiento financiero personalizado."
    )
