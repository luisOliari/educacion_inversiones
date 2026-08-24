# -*- coding: utf-8 -*-
"""Información educativa sobre impuestos para un inversor uruguayo que
invierte en el exterior (vía Interactive Brokers u otro broker).

⚠️ Esto es información GENERAL para entender el concepto de "ingreso neto vs.
nominal". No es asesoramiento tributario ni reemplaza a un contador: la
normativa tiene excepciones, cambia con el tiempo y depende de tu situación
personal (montos, tipo de cuenta, si declarás bienes en el exterior, etc.).
"""


def clasificar(ticker: str, categoria_catalogo: str | None,
               quote_type: str | None) -> str:
    """Determina la categoría impositiva relevante para un ticker."""
    if categoria_catalogo:
        if categoria_catalogo in ("Acciones", "ETFs (EE.UU.)"):
            return "acciones_eeuu"
        if categoria_catalogo == "ETFs UCITS (Europa)":
            return "ucits"
        if categoria_catalogo == "Bonos / Renta fija":
            return "bonos"
        if categoria_catalogo == "Criptomonedas":
            return "cripto"
    if str(ticker).upper().endswith(".L"):
        return "ucits"
    if quote_type == "CRYPTOCURRENCY":
        return "cripto"
    return "acciones_eeuu"


# Retención en origen (Estados Unidos) — dato objetivo, bien documentado.
RETENCION_ORIGEN = {
    "acciones_eeuu": {
        "tasa": 0.30,
        "motivo": (
            "EE.UU. retiene un 30% sobre los dividendos pagados a inversores "
            "extranjeros que no tienen un tratado de doble imposición con "
            "EE.UU. — y Uruguay no lo tiene. Esta retención es automática: "
            "Interactive Brokers ya te acredita el dividendo neto de ese 30%."
        ),
    },
    "ucits": {
        "tasa": 0.15,
        "motivo": (
            "Al estar domiciliado en Irlanda, el fondo accede al tratado "
            "fiscal Irlanda-EE.UU., que reduce la retención sobre dividendos "
            "de acciones de EE.UU. del 30% al 15% dentro del fondo. Como "
            "además suelen ser 'de acumulación', ese dividendo neto se "
            "reinvierte solo, sin que lo veas como efectivo."
        ),
    },
    "bonos": {
        "tasa": 0.0,
        "motivo": (
            "Los intereses de bonos del Tesoro de EE.UU. (y la mayoría de "
            "bonos 'de cartera') pagados a inversores extranjeros están, en "
            "general, exentos de retención en origen ('portfolio interest "
            "exemption'). A diferencia de los dividendos, casi no se retiene "
            "nada acá."
        ),
    },
    "cripto": {
        "tasa": None,
        "motivo": (
            "Las criptomonedas no reparten dividendos ni intereses: no hay "
            "retención en origen porque no hay pago periódico, solo "
            "ganancia (o pérdida) de capital al vender."
        ),
    },
}

# Tratamiento en Uruguay — territorial en general, con la excepción del
# artículo agregado por la Ley 19.438 (2017) para "colocaciones de capital"
# en el exterior (depósitos, préstamos, y rendimientos asimilables, como el
# interés de bonos). Se presenta como guía general, no como cálculo exacto.
URUGUAY_IRPF = {
    "acciones_eeuu": {
        "tasa": 0.0,
        "nota": (
            "Tanto los dividendos como la ganancia de capital al vender "
            "acciones o ETFs extranjeros son renta de **fuente extranjera**. "
            "Uruguay grava IRPF sobre un criterio territorial: en general, "
            "esta renta **no tributa** para una persona física residente."
        ),
    },
    "ucits": {
        "tasa": 0.0,
        "nota": (
            "Mismo criterio que las acciones: es renta de fuente extranjera "
            "y en general **no tributa** IRPF en Uruguay. Además, al ser "
            "fondos de acumulación, normalmente no hay un dividendo en "
            "efectivo que declarar — el valor se refleja en el precio del "
            "fondo al vender."
        ),
    },
    "bonos": {
        "tasa": 0.12,
        "nota": (
            "Acá está la excepción importante: desde la Ley 19.438 (2017), "
            "los rendimientos de **colocaciones de capital en el exterior** "
            "(depósitos, préstamos y, en general, instrumentos que generan "
            "interés, como los bonos) que reciba un residente uruguayo "
            "**sí tributan IRPF, a una tasa del 12%**. La ganancia de "
            "capital por vender el bono/ETF a mejor precio, en cambio, sigue "
            "el criterio territorial general."
        ),
    },
    "cripto": {
        "tasa": None,
        "nota": (
            "El tratamiento de las criptomonedas en la normativa uruguaya "
            "es un área todavía poco desarrollada y depende de cómo se "
            "clasifique la operación. No hay una respuesta simple: "
            "consultá específicamente este punto con un contador."
        ),
    },
}

ADVERTENCIA = (
    "⚠️ **Esto es información educativa general, no asesoramiento "
    "tributario.** La normativa uruguaya tiene excepciones, cambia con el "
    "tiempo y depende de tu situación personal (montos, si operás como "
    "persona física, si tenés que presentar la Declaración de Bienes en el "
    "Exterior, etc.). Antes de declarar impuestos, confirmá esto con un "
    "contador o asesor tributario en Uruguay."
)


def resumen(ticker: str, categoria_catalogo: str | None,
           quote_type: str | None) -> dict:
    clase = clasificar(ticker, categoria_catalogo, quote_type)
    return {
        "clase": clase,
        **{f"origen_{k}": v for k, v in RETENCION_ORIGEN[clase].items()},
        **{f"uy_{k}": v for k, v in URUGUAY_IRPF[clase].items()},
    }
