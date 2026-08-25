# -*- coding: utf-8 -*-
"""Información educativa sobre impuestos para un inversor uruguayo que
invierte en el exterior (vía Interactive Brokers u otro broker).

⚠️ Esto es información GENERAL para entender el concepto de "ingreso neto vs.
nominal". No es asesoramiento tributario ni reemplaza a un contador: la
normativa tiene excepciones, cambia con el tiempo y depende de tu situación
personal (montos, tipo de cuenta, si declarás bienes en el exterior, etc.).

Cómo funciona el IRPF uruguayo sobre esto (resumen, vigente):
Tanto los RENDIMIENTOS de capital mobiliario (dividendos, intereses) como
el INCREMENTO PATRIMONIAL (ganancia de capital al vender, ya sea de capital
mobiliario —acciones, ETFs, bonos— o inmobiliario) que un residente
uruguayo obtiene en el exterior tributan IRPF Categoría I al 12%. Uruguay
permite acreditar el impuesto ya pagado en el exterior sobre esa misma
renta, pero con un TOPE del 12%: no se puede descontar más que la propia
tasa uruguaya, aunque en el exterior se haya pagado más.
- Sobre DIVIDENDOS/INTERESES: como EE.UU. suele retener 30% (acciones
  directas) o 15% (UCITS) — ambos por encima del 12% — el crédito cubre
  todo el IRPF uruguayo y no se paga nada adicional (pero tampoco se
  devuelve el excedente ya pagado afuera).
- Sobre la GANANCIA DE CAPITAL al vender: EE.UU. (y los mercados donde se
  domicilian los ETFs, como Irlanda) NO retienen impuesto sobre la
  ganancia de capital de un inversor extranjero. Como no hay nada pagado
  en origen para acreditar, el crédito es $0 y en Uruguay se paga el 12%
  completo sobre la ganancia.
"""

TASA_IRPF_CAT_I = 0.12  # IRPF Categoría I: rendimientos de capital
                        # mobiliario E incremento patrimonial (ganancia de
                        # capital), con crédito fiscal tope 12%.


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
# Aplica solo a dividendos/intereses: la ganancia de capital NO tiene
# retención en origen para un inversor extranjero, en ninguna categoría.
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


def _ganancia_capital(clase: str) -> dict:
    """Impuesto uruguayo sobre el incremento patrimonial (ganancia de
    capital) al vender. EE.UU./Irlanda no retienen nada sobre esto, así que
    no hay crédito fiscal que aplicar: se paga el 12% completo."""
    if clase == "cripto":
        return {
            "gc_aplica": None,
            "gc_tasa": None,
            "gc_nota": (
                "El encuadre de las criptomonedas como 'capital mobiliario' "
                "a estos efectos no es tan claro como el de acciones o "
                "bonos: es un área gris de la normativa. Consultá "
                "específicamente este punto con un contador."
            ),
        }
    return {
        "gc_aplica": True,
        "gc_tasa": TASA_IRPF_CAT_I,
        "gc_nota": (
            "La ganancia de capital al vender (incremento patrimonial) "
            "también tributa IRPF Categoría I al **12%** en Uruguay. A "
            "diferencia de los dividendos, EE.UU. (o Irlanda, para los "
            "UCITS) **no retiene nada en origen** sobre la ganancia de "
            "capital de un inversor extranjero — así que no hay impuesto "
            "pagado afuera para acreditar, y el 12% se paga **completo**, "
            "sin descuento."
        ),
    }


def resumen(ticker: str, categoria_catalogo: str | None,
           quote_type: str | None) -> dict:
    """Calcula la carga fiscal para un activo: por un lado, dividendos e
    intereses (origen + Uruguay con crédito tope 12%); por otro, la
    ganancia de capital al vender (Uruguay 12%, sin crédito posible).

    Claves relevantes del resultado:
    - carga_total: carga combinada sobre DIVIDENDOS/INTERESES = máximo
      entre la retención de origen y el 12% uruguayo (nunca la suma).
    - gc_tasa: tasa uruguaya sobre la GANANCIA DE CAPITAL al vender (12%,
      sin crédito porque no hay retención en origen que acreditar).
    """
    clase = clasificar(ticker, categoria_catalogo, quote_type)
    origen = RETENCION_ORIGEN[clase]
    tasa_origen = origen["tasa"]

    base = {
        "clase": clase,
        "origen_tasa": tasa_origen,
        "origen_motivo": origen["motivo"],
        **_ganancia_capital(clase),
    }

    if clase == "cripto":
        return {
            **base,
            "aplica_irpf_12": False,
            "uy_adicional": None,
            "carga_total": None,
            "uy_nota": (
                "No hay dividendos ni intereses, así que no aplica el IRPF "
                "del 12% sobre rendimientos de capital mobiliario. Ver la "
                "nota sobre ganancia de capital más abajo."
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
                "del fondo y quedó reflejada en su precio. Ese valor "
                "reinvertido se realiza recién cuando vendés tus unidades — "
                "momento en el que pasa a tributar como ganancia de capital "
                "(ver nota abajo), no como dividendo."
            ),
        }

    # acciones_eeuu (si reparte dividendo) y bonos (interés): esto SÍ es
    # "rendimiento de capital mobiliario" — tributa 12% en Uruguay, con
    # crédito por el impuesto ya pagado en el exterior, tope 12%.
    uy_adicional = max(TASA_IRPF_CAT_I - (tasa_origen or 0), 0)
    carga_total = max(tasa_origen or 0, TASA_IRPF_CAT_I)
    if (tasa_origen or 0) >= TASA_IRPF_CAT_I:
        nota_extra = (
            f"Como EE.UU. ya te retuvo {tasa_origen*100:.0f}% (más que el "
            "12% uruguayo), el crédito cubre el 100% del IRPF: Uruguay no "
            "te cobra nada adicional. Pero **tampoco te devuelve** el "
            f"{(tasa_origen - TASA_IRPF_CAT_I)*100:.0f}% de diferencia: "
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
