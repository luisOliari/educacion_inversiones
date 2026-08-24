# 📈 Mi Guía de Inversiones

App educativa para explorar activos (acciones, ETFs, ETFs UCITS, bonos y cripto)
antes de invertir desde Interactive Brokers: qué es cada activo, cómo funciona,
su evolución histórica en gráficas y los indicadores clave explicados desde cero.

> ⚠️ Herramienta de estudio. No es asesoramiento financiero.

## Cómo ejecutarla localmente

```
pip install -r requirements.txt
streamlit run app.py
```

Se abre sola en el navegador en http://localhost:8501

## Cómo publicarla en Streamlit Community Cloud (gratis, con link propio)

1. Subí esta carpeta a un repositorio de GitHub.
2. Entrá a [share.streamlit.io](https://share.streamlit.io), iniciá sesión con
   tu cuenta de GitHub y tocá **New app**.
3. Elegí el repositorio, la rama (`main`) y como archivo principal `app.py`.
4. Deploy. En 1-2 minutos te da un link público (tipo
   `tu-usuario-app-inversiones.streamlit.app`) que podés compartir con
   cualquiera — no necesitan instalar nada.

Cada visitante ve la app desde cero, sin tu cartera ni la de nadie más: la
cartera vive solo en la sesión de cada navegador (ver más abajo), nunca en un
archivo del servidor.

## Estructura

- `app.py` — la aplicación (pestañas: inicio, conocé el activo, gráficas, indicadores, comparación con S&P 500, mi cartera, aprender)
- `catalogo.py` — catálogo curado de activos con textos educativos
- `indicadores.py` — cálculo de indicadores (CAGR, volatilidad, drawdown, Sharpe, RSI...) y sus explicaciones
- `cartera.py` — cálculos de la cartera personal (composición, curva histórica) e importación/exportación de CSV

Los datos se bajan gratis de Yahoo Finance (`yfinance`) y se cachean 1 hora.

## Sobre "Mi cartera" y la privacidad

La cartera **no se guarda en ningún archivo del servidor** — vive solo en la
sesión del navegador de cada persona mientras tiene la pestaña abierta. Esto es
importante porque, a diferencia de correrla en tu propia compu, en Streamlit
Cloud **todas las visitas al mismo link comparten el mismo servidor**: si la
cartera se guardara en un archivo, cualquier visitante podría ver o pisar la
tuya.

Para no perder tu cartera al cerrar la pestaña: descargala como CSV (botón
"⬇️ Descargar mi cartera en CSV") y la próxima vez subila de nuevo con
"📥 Importar desde CSV". Ese CSV queda solo en tu computadora.

## Para compartir el link con otras personas

Una vez publicada en Streamlit Cloud, compartí el link tal cual — cada persona
arranca con una cartera vacía, nunca ve la tuya. La app arranca en la pestaña
**🏠 Inicio**, que explica todo desde cero, sin necesitar conocimientos previos.

Cada persona puede cargar su cartera a mano o **subir el CSV exportado de su
broker** (pestaña Mi cartera → Importar desde CSV): la app detecta las columnas
automáticamente y arma las posiciones con sus ganancias y pérdidas.
