# -*- coding: utf-8 -*-
"""Información educativa sobre impuestos para un inversor uruguayo que
invierte en el exterior (vía Interactive Brokers u otro broker).

⚠️ Esto es información GENERAL para entender el concepto de "ingreso neto vs.
nominal". No es asesoramiento tributario ni reemplaza a un contador: la
normativa tiene excepciones, cambia con el tiempo y depende de tu situación
personal (montos, tipo de cuenta, si declarás bienes en el exterior, etc.).

Cómo funciona el IRPF uruguayo sobre esto (resumen):
Los rendimientos de capital mobiliario (dividendos, intereses) que un
residente uruguayo obtiene en el exterior tributan IRPF Categoría I al 12%.
Uruguay permite acreditar el impuesto ya pagado en el exterior (la retención
en origen), pero con un TOPE del 12%: no se puede descontar más que la
propia tasa uruguaya, aunque en el exterior se haya pagado más. Como
consecuencia, cuando la retención de origen ya es del 12% o más (por ejemplo
el 30% de EE.UU. sobre dividendos), Uruguay no cobra nada adicional — pero
tampoco devuelve el excedente. La carga total termina siendo la MAYOR entre
la retención de origen y el 12% uruguayo, nunca la suma de ambas.
⚠️ PENDIENTE DE CONFIRMAR: la ganancia de capital (vender más caro de lo
que compraste) venía considerándose renta de fuente extranjera, en general
no gravada. Hubo un cambio normativo que la haría tributar ahora — falta
confirmar la tasa exacta, desde cuándo rige y si hay crédito fiscal. Hasta
confirmarlo, NO se calcula un número: se avisa que puede haber impuesto.
"""

TOPE_CREDITO_URUGUAY = 0.12  # tasa de IRPF Categoría I sobre rendimientos de
                              # capital mobiliario, y tope del crédito fiscal


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
            "reinvierte solo dentro del fondo, sin que llegue a tu cuenta ni "
            "generes un hecho gravable individual cada año."
        ),
    },
    "bonos": {
        "tasa": 0.0,
        "motivo": (
            "Los intereses de bonos del Tesoro de EE.UU. (y la mayoría de "
            "bonos 'de cartera') pagados a inversores extranjeros están, en "
            "general, exentos de retención en origen ('portfolio interest "
            "exemption'). A diferencia de los dividendos, casi no se retiene "
            "nada acá — lo que después importa para el cálculo en Uruguay."
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


def resumen(ticker: str, categoria_catalogo: str | None,
           quote_type: str | None) -> dict:
    """Calcula la carga fiscal combinada (origen + Uruguay) para un activo.

    Devuelve, entre otras cosas:
    - aplica_irpf_12: si esta renta cae dentro del IRPF 12% de rendimientos
      de capital mobiliario (dividendos/intereses efectivamente distribuidos).
    - uy_adicional: lo que Uruguay cobra DE MÁS sobre la retención de origen
      (0 si la retención de origen ya iguala o supera el 12%).
    - carga_total: la carga combinada real = max(retención origen, 12%).
    """
    clase = clasificar(ticker, categoria_catalogo, quote_type)
    origen = RETENCION_ORIGEN[clase]
    tasa_origen = origen["tasa"]

    base = {
        "clase": clase,
        "origen_tasa": tasa_origen,
        "origen_motivo": origen["motivo"],
    }

    if clase == "cripto":
        return {
            **base,
            "aplica_irpf_12": False,
            "uy_adicional": None,
            "carga_total": None,
            "uy_nota": (
                "No hay dividendos ni intereses, así que no aplica el IRPF "
                "del 12% sobre rendimientos de capital mobiliario. La "
                "ganancia (o pérdida) al vender es un área todavía poco "
                "desarrollada en la normativa uruguaya: consultá "
                "específicamente este punto con un contador."
            ),
        }

    if clase == "ucits":
        return {
            **base,
            "aplica_irpf_12": False,
            "uy_adicional": 0.0,
            "carga_total": tasa_origen,
            "uy_nota": (
                "Al ser un fondo de acumulación, no recibís un dividendo en "
                "efectivo: no hay 'rendimiento de capital mobiliario' que "
                "declarar cada año. La retención del 15% ya ocurrió *dentro* "
                "del fondo y quedó reflejada en su precio; cuando vendas tus "
                "unidades con ganancia, eso es ganancia de capital de fuente "
                "extranjera. ⚠️ Este punto está cambiando: hasta hace poco "
                "en general no tributaba, pero hay una modificación "
                "normativa reciente que la haría gravar — confirmá la tasa "
                "vigente con un contador antes de asumir que no paga nada."
            ),
        }

    # acciones_eeuu (si reparte dividendo) y bonos (interés): esto SÍ es
    # "rendimiento de capital mobiliario" — tributa 12% en Uruguay, con
    # crédito por el impuesto ya pagado en el exterior, tope 12%.
    uy_adicional = max(TOPE_CREDITO_URUGUAY - (tasa_origen or 0), 0)
    carga_total = max(tasa_origen or 0, TOPE_CREDITO_URUGUAY)
    if (tasa_origen or 0) >= TOPE_CREDITO_URUGUAY:
        nota_extra = (
            f"Como EE.UU. ya te retuvo {tasa_origen*100:.0f}% (más que el "
            "12% uruguayo), el crédito cubre el 100% del IRPF: Uruguay no "
            "te cobra nada adicional. Pero **tampoco te devuelve** el "
            f"{(tasa_origen - TOPE_CREDITO_URUGUAY)*100:.0f}% de diferencia: "
            f"tu carga total termina siendo el {tasa_origen*100:.0f}% que "
            "ya pagaste en origen, no un 12% aparte."
        )
    else:
        nota_extra = (
            f"Como en origen retuvieron {(tasa_origen or 0)*100:.0f}% (menos "
            f"del 12%), en Uruguay pagás la diferencia hasta completar el "
            f"12%: {uy_adicional*100:.0f}% adicional. Tu carga total "
            f"combinada queda en {carga_total*100:.0f}%."
        )
    return {
        **base,
        "aplica_irpf_12": True,
        "uy_adicional": uy_adicional,
        "carga_total": carga_total,
        "uy_nota": (
            "Los dividendos e intereses son 'rendimiento de capital "
            "mobiliario': tributan IRPF Categoría I al **12%** en Uruguay. "
            "Se acredita el impuesto ya pagado en el exterior, pero con un "
            "**tope del 12%** — no se puede descontar más que eso, aunque "
            "en el exterior se haya pagado más. " + nota_extra
        ),
    }


ADVERTENCIA = (
    "⚠️ **Esto es información educativa general, no asesoramiento "
    "tributario.** La normativa uruguaya tiene excepciones, cambia con el "
    "tiempo y depende de tu situación personal (montos, si operás como "
    "persona física, si tenés que presentar la Declaración de Bienes en el "
    "Exterior, etc.). Antes de declarar impuestos, confirmá esto con un "
    "contador o asesor tributario en Uruguay."
)
