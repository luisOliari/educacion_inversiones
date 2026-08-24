# -*- coding: utf-8 -*-
"""Catálogo curado de activos con contenido educativo para principiantes."""

CATEGORIAS = {
    "Acciones": {
        "emoji": "📈",
        "intro": (
            "Una **acción** es una pequeña parte de la propiedad de una empresa. "
            "Cuando comprás una acción de Apple, sos dueño de un pedacito de Apple: "
            "si a la empresa le va bien, tu parte vale más; si le va mal, vale menos. "
            "Algunas empresas además reparten parte de sus ganancias en efectivo (dividendos). "
            "Las acciones individuales tienen más riesgo que los fondos porque dependés "
            "de la suerte de una sola empresa."
        ),
    },
    "ETFs (EE.UU.)": {
        "emoji": "🧺",
        "intro": (
            "Un **ETF** (fondo cotizado) es una canasta que agrupa muchas acciones o bonos "
            "en un solo producto que se compra y vende como una acción. En vez de elegir "
            "una empresa, comprás cientos de una sola vez: eso se llama **diversificación** "
            "y reduce el riesgo de que una sola empresa te arruine la inversión. "
            "Los ETFs listados en EE.UU. son los más conocidos, pero ojo: para residentes "
            "fuera de EE.UU. pueden tener desventajas impositivas (retención de dividendos "
            "del 30% y posible impuesto a la herencia de EE.UU. sobre montos grandes)."
        ),
    },
    "ETFs UCITS (Europa)": {
        "emoji": "🇪🇺",
        "intro": (
            "Los **ETFs UCITS** son fondos regulados en Europa (Irlanda o Luxemburgo) que "
            "invierten en las mismas empresas que los ETFs americanos, pero con ventajas "
            "para inversores de América Latina que usan Interactive Brokers: la retención "
            "sobre dividendos de acciones de EE.UU. baja del 30% al 15% dentro del fondo, "
            "no aplica el impuesto a la herencia de EE.UU., y muchos son de **acumulación** "
            "(reinvierten los dividendos automáticamente, sin que tengas que hacer nada). "
            "Cotizan en la bolsa de Londres en dólares. Suelen ser la opción recomendada "
            "para inversores de largo plazo desde Uruguay y la región."
        ),
    },
    "Bonos / Renta fija": {
        "emoji": "🏦",
        "intro": (
            "Un **bono** es un préstamo: le prestás plata a un gobierno o empresa y a cambio "
            "te pagan intereses y te devuelven el capital al vencimiento. Son en general "
            "menos riesgosos que las acciones, pero también rinden menos a largo plazo. "
            "La forma más práctica de invertir en bonos es a través de ETFs de bonos. "
            "Regla clave: cuando las tasas de interés **suben**, el precio de los bonos "
            "existentes **baja** (y viceversa). Cuanto más largo el plazo del bono, más "
            "sensible es a las tasas."
        ),
    },
    "Criptomonedas": {
        "emoji": "🪙",
        "intro": (
            "Las **criptomonedas** son activos digitales que funcionan sobre redes "
            "descentralizadas (blockchain), sin un banco central detrás. Su precio depende "
            "puramente de la oferta y la demanda: no generan ganancias ni pagan dividendos, "
            "por lo que su valor es más especulativo. Son **extremadamente volátiles**: "
            "caídas del 50-80% han ocurrido varias veces. Si invertís, que sea solo un "
            "porcentaje chico de tu cartera que estés dispuesto a perder por completo."
        ),
    },
}

# Cada activo: nombre, qué es, cómo funciona, riesgos, para quién
ACTIVOS = {
    # ── Acciones ──────────────────────────────────────────────────────────
    "AAPL": {
        "categoria": "Acciones",
        "nombre": "Apple",
        "que_es": "La empresa del iPhone, Mac y servicios digitales. Una de las compañías más valiosas del mundo.",
        "como_funciona": "Gana dinero vendiendo hardware (iPhone ~50% de ingresos) y cada vez más por servicios (App Store, iCloud, Apple Music) que dejan márgenes altos y recurrentes.",
        "riesgos": "Depende mucho del iPhone; tensiones con China (donde fabrica y vende mucho); regulación sobre la App Store.",
        "perfil": "Quien busca una empresa grande, estable y rentable, aceptando el riesgo de concentrarse en una sola compañía.",
    },
    "MSFT": {
        "categoria": "Acciones",
        "nombre": "Microsoft",
        "que_es": "Gigante del software: Windows, Office, la nube Azure y fuerte apuesta en inteligencia artificial.",
        "como_funciona": "Ingresos por suscripciones (Office 365) y por la nube Azure, que crece con la demanda de IA. Modelo muy recurrente y predecible.",
        "riesgos": "Competencia en la nube (Amazon, Google); si la inversión gigante en IA no genera retorno, el mercado puede castigarla.",
        "perfil": "Similar a Apple: empresa dominante y diversificada dentro de la tecnología.",
    },
    "GOOGL": {
        "categoria": "Acciones",
        "nombre": "Alphabet (Google)",
        "que_es": "Dueña de Google, YouTube, Android y la nube Google Cloud.",
        "como_funciona": "Casi el 80% de sus ingresos viene de publicidad (búsquedas y YouTube). La nube y otras apuestas (Waymo) complementan.",
        "riesgos": "La IA puede cambiar cómo la gente busca información; juicios antimonopolio en EE.UU. y Europa.",
        "perfil": "Quien cree que Google seguirá dominando la publicidad digital y la IA.",
    },
    "AMZN": {
        "categoria": "Acciones",
        "nombre": "Amazon",
        "que_es": "El mayor comercio electrónico de Occidente y dueña de AWS, la nube más grande del mundo.",
        "como_funciona": "El e-commerce mueve mucho volumen con poco margen; la ganancia real viene de AWS (nube) y publicidad.",
        "riesgos": "Márgenes finos en retail; competencia fuerte en nube; muy sensible al ciclo económico del consumidor.",
        "perfil": "Quien busca exposición al consumo online y a la infraestructura de internet.",
    },
    "NVDA": {
        "categoria": "Acciones",
        "nombre": "NVIDIA",
        "que_es": "Diseña los chips (GPUs) que entrenan y ejecutan la inteligencia artificial. La gran ganadora del boom de IA.",
        "como_funciona": "Vende chips y sistemas para centros de datos de IA con márgenes altísimos. Su demanda depende de cuánto inviertan las tecnológicas en IA.",
        "riesgos": "Muy volátil: si la inversión en IA se frena, puede caer fuerte. Valuación exigente. Competencia de AMD y chips propios de Google/Amazon.",
        "perfil": "Quien quiere apostar directo al crecimiento de la IA, tolerando subidas y bajadas grandes.",
    },
    "KO": {
        "categoria": "Acciones",
        "nombre": "Coca-Cola",
        "que_es": "La marca de bebidas más conocida del mundo. Ejemplo clásico de empresa 'defensiva'.",
        "como_funciona": "Vende concentrado y licencias a embotelladoras en todo el mundo. Negocio estable que crece poco pero genera mucho efectivo y paga dividendos hace más de 60 años seguidos.",
        "riesgos": "Crecimiento lento; tendencia mundial a consumir menos azúcar; sensible al dólar fuerte.",
        "perfil": "Quien prioriza estabilidad y dividendos sobre crecimiento. Suele caer menos en las crisis.",
    },
    "JNJ": {
        "categoria": "Acciones",
        "nombre": "Johnson & Johnson",
        "que_es": "Gigante de la salud: medicamentos y dispositivos médicos.",
        "como_funciona": "La gente se enferma en cualquier economía, por eso sus ingresos son muy estables. Aumenta su dividendo hace más de 60 años.",
        "riesgos": "Juicios (talco, opioides); vencimiento de patentes de medicamentos clave.",
        "perfil": "Perfil conservador que busca el sector salud con dividendos crecientes.",
    },
    "JPM": {
        "categoria": "Acciones",
        "nombre": "JPMorgan Chase",
        "que_es": "El banco más grande de EE.UU.",
        "como_funciona": "Gana por la diferencia entre lo que paga por depósitos y lo que cobra por préstamos, más comisiones de banca de inversión y gestión de patrimonio.",
        "riesgos": "Los bancos sufren mucho en las recesiones (impagos de préstamos); sensible a las tasas de interés.",
        "perfil": "Quien quiere exposición al sector financiero con el jugador dominante.",
    },
    "TSLA": {
        "categoria": "Acciones",
        "nombre": "Tesla",
        "que_es": "Fabricante líder de autos eléctricos, con apuestas en robotaxis, robots y energía.",
        "como_funciona": "Vende autos eléctricos con la marca más fuerte del sector. Gran parte de su precio de mercado descuenta éxitos futuros en conducción autónoma y robótica que todavía no son negocio.",
        "riesgos": "Altísima volatilidad; competencia china (BYD); su valuación depende de promesas a futuro; muy ligada a la figura de Elon Musk.",
        "perfil": "Solo para quien tolera oscilaciones enormes y cree en la visión de largo plazo.",
    },
    "V": {
        "categoria": "Acciones",
        "nombre": "Visa",
        "que_es": "La red de pagos más grande del mundo. No presta plata: cobra un peaje por cada transacción.",
        "como_funciona": "Cada vez que alguien paga con Visa, la empresa cobra una comisión mínima. Miles de millones de transacciones = negocio de márgenes enormes que crece con el abandono del efectivo.",
        "riesgos": "Regulación de comisiones; competencia de nuevos métodos de pago (billeteras, cripto, pagos instantáneos).",
        "perfil": "Quien busca un negocio de alta calidad que crece de forma constante.",
    },
    # ── ETFs EE.UU. ───────────────────────────────────────────────────────
    "VOO": {
        "categoria": "ETFs (EE.UU.)",
        "nombre": "Vanguard S&P 500",
        "que_es": "Replica el índice S&P 500: las 500 empresas más grandes de EE.UU. en un solo producto. Costo anual bajísimo (0,03%).",
        "como_funciona": "Comprás VOO y automáticamente sos dueño de un pedacito de Apple, Microsoft, Amazon y 497 más, ponderadas por tamaño. Es la forma clásica de 'comprar el mercado americano'.",
        "riesgos": "Cae cuando cae el mercado (en 2008 el S&P 500 cayó ~50%). Concentrado en EE.UU. y cada vez más en pocas tecnológicas gigantes.",
        "perfil": "La base de la mayoría de las carteras de largo plazo. Warren Buffett lo recomienda para el inversor común.",
    },
    "QQQ": {
        "categoria": "ETFs (EE.UU.)",
        "nombre": "Invesco QQQ (Nasdaq-100)",
        "que_es": "Replica el Nasdaq-100: las 100 mayores empresas no financieras del Nasdaq, dominado por tecnología.",
        "como_funciona": "Concentra la apuesta en tecnología: Apple, Microsoft, NVIDIA, Amazon, Meta... Históricamente rindió más que el S&P 500, pero con caídas más profundas.",
        "riesgos": "En el 2000-2002 el Nasdaq cayó ~80%. Más volátil que el mercado general.",
        "perfil": "Quien quiere más exposición a tecnología aceptando más vaivenes.",
    },
    "VTI": {
        "categoria": "ETFs (EE.UU.)",
        "nombre": "Vanguard Total Stock Market",
        "que_es": "Todo el mercado de acciones de EE.UU.: unas 3.500 empresas grandes, medianas y chicas.",
        "como_funciona": "Similar a VOO pero incluye también empresas medianas y pequeñas. En la práctica se mueve casi igual que el S&P 500.",
        "riesgos": "Los mismos del mercado americano en general.",
        "perfil": "Quien quiere la máxima diversificación dentro de EE.UU. en un solo fondo.",
    },
    "VXUS": {
        "categoria": "ETFs (EE.UU.)",
        "nombre": "Vanguard Total International",
        "que_es": "Acciones de todo el mundo EXCEPTO EE.UU.: Europa, Japón, mercados emergentes.",
        "como_funciona": "Complementa a VOO/VTI para no depender solo de EE.UU. Una cartera global típica combina ambos.",
        "riesgos": "Riesgo cambiario; los mercados internacionales rindieron menos que EE.UU. en la última década (aunque eso puede cambiar).",
        "perfil": "Quien quiere diversificar geográficamente su cartera.",
    },
    "SCHD": {
        "categoria": "ETFs (EE.UU.)",
        "nombre": "Schwab US Dividend Equity",
        "que_es": "ETF de ~100 empresas americanas de calidad que pagan dividendos crecientes.",
        "como_funciona": "Selecciona empresas con historial de dividendos sólidos y finanzas sanas (Coca-Cola, Pepsi, Home Depot...). Paga un dividendo mayor al del mercado.",
        "riesgos": "Suele quedarse atrás cuando la tecnología lidera; los dividendos a extranjeros sufren retención del 30% (15% vía UCITS).",
        "perfil": "Quien prioriza ingresos por dividendos y empresas 'aburridas pero sólidas'.",
    },
    # ── ETFs UCITS ────────────────────────────────────────────────────────
    "VUAA.L": {
        "categoria": "ETFs UCITS (Europa)",
        "nombre": "Vanguard S&P 500 UCITS (Acum.)",
        "que_es": "El equivalente europeo de VOO: el S&P 500, pero domiciliado en Irlanda y de acumulación (reinvierte dividendos solo). Cotiza en Londres en dólares.",
        "como_funciona": "Mismo índice que VOO. Al ser UCITS irlandés: retención de dividendos del 15% en vez de 30%, sin impuesto a la herencia de EE.UU., y no te llegan dividendos que tengas que declarar/reinvertir: el fondo lo hace por vos.",
        "riesgos": "Los mismos del S&P 500. Algo menos de liquidez que VOO (irrelevante para el inversor minorista de largo plazo).",
        "perfil": "Probablemente la opción más eficiente para invertir en el S&P 500 desde Uruguay/Latinoamérica vía Interactive Brokers.",
    },
    "CSPX.L": {
        "categoria": "ETFs UCITS (Europa)",
        "nombre": "iShares Core S&P 500 UCITS (Acum.)",
        "que_es": "Igual que VUAA pero de iShares (BlackRock). El ETF UCITS del S&P 500 más grande.",
        "como_funciona": "Idéntico concepto: S&P 500, acumulación, domicilio irlandés. Elegir entre CSPX y VUAA es casi indiferente.",
        "riesgos": "Los mismos del S&P 500.",
        "perfil": "Alternativa a VUAA; el más líquido de los UCITS del S&P 500.",
    },
    "IWDA.L": {
        "categoria": "ETFs UCITS (Europa)",
        "nombre": "iShares Core MSCI World UCITS (Acum.)",
        "que_es": "Unas 1.400 empresas de 23 países desarrollados en un solo fondo: EE.UU. (~70%), Japón, Europa...",
        "como_funciona": "Diversificación global automática con reinversión de dividendos. Si EE.UU. algún día rinde menos, el fondo se rebalancea solo hacia lo que crezca.",
        "riesgos": "Cae con el mercado global; no incluye países emergentes (para eso existe EIMI).",
        "perfil": "Quien quiere 'comprar el mundo desarrollado' con una sola compra mensual y olvidarse.",
    },
    "VWRA.L": {
        "categoria": "ETFs UCITS (Europa)",
        "nombre": "Vanguard FTSE All-World UCITS (Acum.)",
        "que_es": "Todo el mundo en un fondo: ~3.600 empresas de países desarrollados Y emergentes.",
        "como_funciona": "La máxima diversificación posible en un solo producto. 'Un fondo para toda la vida': muchos inversores de largo plazo usan solo este.",
        "riesgos": "Cae con el mercado global (aunque menos concentrado que el S&P 500).",
        "perfil": "La opción más simple y completa para quien quiere una cartera de un solo fondo.",
    },
    "EIMI.L": {
        "categoria": "ETFs UCITS (Europa)",
        "nombre": "iShares Core MSCI EM UCITS (Acum.)",
        "que_es": "Mercados emergentes: China, India, Taiwán, Brasil... unas 3.000 empresas.",
        "como_funciona": "Complementa a IWDA para tener el mundo completo. Los emergentes crecen más rápido pero con más sobresaltos.",
        "riesgos": "Riesgo político y regulatorio (ej: intervenciones de China); alta volatilidad; décadas enteras de bajo rendimiento son posibles.",
        "perfil": "Como complemento (10-20% de cartera) para quien ya tiene la base en desarrollados.",
    },
    # ── Bonos ─────────────────────────────────────────────────────────────
    "SHY": {
        "categoria": "Bonos / Renta fija",
        "nombre": "iShares 1-3 Year Treasury",
        "que_es": "Bonos del Tesoro de EE.UU. de corto plazo (1 a 3 años). Lo más parecido a 'efectivo que rinde'.",
        "como_funciona": "Presta al gobierno americano a corto plazo. Casi no se mueve de precio y paga el interés de las tasas cortas.",
        "riesgos": "Riesgo mínimo, pero rinde poco. Puede perder contra la inflación.",
        "perfil": "Para estacionar dinero que podés necesitar pronto, o la parte más conservadora de la cartera.",
    },
    "IEF": {
        "categoria": "Bonos / Renta fija",
        "nombre": "iShares 7-10 Year Treasury",
        "que_es": "Bonos del Tesoro de EE.UU. de plazo medio (7 a 10 años).",
        "como_funciona": "Punto medio entre riesgo y retorno dentro de los bonos. Suele subir cuando las acciones caen en crisis (aunque no siempre: en 2022 cayeron los dos).",
        "riesgos": "Si las tasas suben, su precio baja. En 2022 perdió ~15%.",
        "perfil": "La parte de bonos de una cartera balanceada clásica.",
    },
    "TLT": {
        "categoria": "Bonos / Renta fija",
        "nombre": "iShares 20+ Year Treasury",
        "que_es": "Bonos del Tesoro de EE.UU. de muy largo plazo (más de 20 años).",
        "como_funciona": "Muy sensible a las tasas: si las tasas bajan fuerte, TLT sube fuerte (y al revés). Se usa casi como apuesta sobre las tasas de interés.",
        "riesgos": "Volatilidad de acción, no de bono: entre 2020 y 2023 cayó ~50%. No es un activo 'tranquilo' a pesar de ser bonos del tesoro.",
        "perfil": "Solo para quien entiende la relación tasas-precio y quiere apostar a bajas de tasas.",
    },
    "BND": {
        "categoria": "Bonos / Renta fija",
        "nombre": "Vanguard Total Bond Market",
        "que_es": "Todo el mercado de bonos de EE.UU.: tesoro, hipotecarios y corporativos de buena calidad.",
        "como_funciona": "Diversificación total en renta fija americana con un costo mínimo. El complemento clásico de VTI/VOO en la cartera '60/40'.",
        "riesgos": "Sensibilidad media a tasas; en 2022 tuvo su peor año (-13%).",
        "perfil": "La opción simple para la porción de bonos de cualquier cartera.",
    },
    # ── Cripto ────────────────────────────────────────────────────────────
    "BTC-USD": {
        "categoria": "Criptomonedas",
        "nombre": "Bitcoin",
        "que_es": "La primera y mayor criptomoneda. Oferta limitada a 21 millones de unidades: sus defensores la ven como 'oro digital'.",
        "como_funciona": "Red descentralizada donde nadie puede emitir más monedas ni censurar transacciones. Su valor depende de la adopción y la confianza; no genera flujo de dinero por sí mismo.",
        "riesgos": "Caídas del 50-80% varias veces en su historia; riesgo regulatorio; riesgo de custodia (si perdés las claves o el exchange quiebra).",
        "perfil": "Solo como porcentaje chico (ej: 1-5%) de una cartera, con horizonte largo y estómago fuerte.",
    },
    "ETH-USD": {
        "categoria": "Criptomonedas",
        "nombre": "Ethereum",
        "que_es": "La segunda cripto más grande. Más que una moneda: una plataforma para aplicaciones descentralizadas (contratos inteligentes, DeFi, NFTs).",
        "como_funciona": "Los desarrolladores construyen aplicaciones sobre Ethereum y pagan comisiones en ETH por usar la red. Su valor depende del uso real de la plataforma.",
        "riesgos": "Todo lo de Bitcoin más la competencia de otras plataformas (Solana, etc.) y mayor complejidad técnica.",
        "perfil": "Quien ya entiende Bitcoin y quiere exposición al ecosistema de aplicaciones cripto.",
    },
}


def activos_de(categoria: str) -> dict:
    return {t: a for t, a in ACTIVOS.items() if a["categoria"] == categoria}
