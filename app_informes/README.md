# 📄 Informe de Activos

App educativa que genera un **informe detallado de cualquier activo**
(acción, ETF, bono o cripto) a partir de su ticker: qué es, cómo funciona,
cuánto rindió este año, su evolución histórica, indicadores clave e
impuestos estimados para un inversor uruguayo — descargable como **Word
(.docx)**.

> ⚠️ Herramienta educativa. No es asesoramiento financiero ni tributario.

## Fuentes de datos (no solo Yahoo Finance)

- **Yahoo Finance** (`yfinance`) — precios históricos, dividendos, datos
  fundamentales.
- **Wikipedia** — descripción independiente de la empresa o activo, en
  español (con respaldo en inglés).
- **SEC EDGAR** (sec.gov) — ingresos y ganancia neta oficiales, tal como los
  presenta la propia empresa ante el regulador de EE.UU. (solo para
  acciones que cotizan allí). Es la fuente primaria, independiente de
  Yahoo Finance, para "cuánto gana la empresa".

## Cómo ejecutarla localmente

```
pip install -r requirements.txt
streamlit run app.py
```

Vive como subcarpeta del repo principal y reutiliza su catálogo educativo,
indicadores e info de impuestos (`catalogo.py`, `indicadores.py`,
`impuestos.py`, un nivel arriba) — si clonaste el repositorio completo, ya
está.

## Cómo publicarla en Streamlit Community Cloud

Es el mismo repositorio que la app de cartera, así que no hace falta
subir nada nuevo a GitHub aparte. En
[share.streamlit.io](https://share.streamlit.io) creá una **segunda** app
apuntando al mismo repositorio, pero con archivo principal
`app_informes/app.py`. Vas a tener las dos apps (cartera e informes)
publicadas al mismo tiempo, cada una con su propio link.

## Estructura

- `app.py` — interfaz Streamlit
- `fuentes.py` — recolección de datos (Yahoo Finance, Wikipedia, SEC EDGAR)
- `informe.py` — arma el contenido del informe combinando las fuentes con
  el catálogo educativo de `app_inversiones`
- `exportar_docx.py` — genera el archivo Word con gráfica incluida
