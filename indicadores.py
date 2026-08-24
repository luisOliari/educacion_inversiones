# -*- coding: utf-8 -*-
"""Cálculo de indicadores financieros y sus explicaciones educativas."""

import numpy as np
import pandas as pd

DIAS_BURSATILES = 252


def rendimiento_total(precios: pd.Series) -> float:
    """Rendimiento acumulado del período, en proporción (0.25 = +25%)."""
    return precios.iloc[-1] / precios.iloc[0] - 1


def cagr(precios: pd.Series) -> float | None:
    """Rendimiento anualizado compuesto. None si el período es menor a un año."""
    dias = (precios.index[-1] - precios.index[0]).days
    if dias < 365:
        return None
    anios = dias / 365.25
    return (precios.iloc[-1] / precios.iloc[0]) ** (1 / anios) - 1


def volatilidad_anual(precios: pd.Series) -> float:
    retornos = precios.pct_change().dropna()
    return retornos.std() * np.sqrt(DIAS_BURSATILES)


def max_drawdown(precios: pd.Series) -> float:
    """Peor caída desde un máximo histórico dentro del período (negativo)."""
    maximos = precios.cummax()
    return ((precios - maximos) / maximos).min()


def serie_drawdown(precios: pd.Series) -> pd.Series:
    maximos = precios.cummax()
    return (precios - maximos) / maximos


def sharpe(precios: pd.Series, tasa_libre_riesgo: float = 0.04) -> float:
    retornos = precios.pct_change().dropna()
    exceso = retornos.mean() * DIAS_BURSATILES - tasa_libre_riesgo
    vol = retornos.std() * np.sqrt(DIAS_BURSATILES)
    return exceso / vol if vol > 0 else np.nan


def rsi(precios: pd.Series, ventana: int = 14) -> float:
    delta = precios.diff()
    subidas = delta.clip(lower=0).rolling(ventana).mean()
    bajadas = (-delta.clip(upper=0)).rolling(ventana).mean()
    rs = subidas / bajadas
    serie = 100 - 100 / (1 + rs)
    return float(serie.iloc[-1])


def retornos_anuales(precios: pd.Series) -> pd.Series:
    """Rendimiento por año calendario (solo años con datos casi completos)."""
    anual = precios.resample("YE").last()
    primer = precios.resample("YE").first()
    r = anual / primer - 1
    r.index = r.index.year
    return r.dropna()


EXPLICACIONES = {
    "rendimiento": (
        "**¿Qué es?** Cuánto ganó (o perdió) la inversión en el período elegido, "
        "en porcentaje. Si invertías \\$1.000 y ves +50%, hoy tendrías \\$1.500.\n\n"
        "**¿Cómo leerlo?** El pasado no garantiza el futuro, pero muestra cómo se "
        "comportó el activo. Compará siempre contra el S&P 500: si un activo rinde "
        "menos que el índice con más riesgo, es una mala señal."
    ),
    "cagr": (
        "**¿Qué es?** El rendimiento anualizado: cuánto ganó *por año en promedio*, "
        "contando el interés compuesto. Es el número más honesto para comparar "
        "inversiones de distintos plazos.\n\n"
        "**Referencia:** el S&P 500 rindió históricamente ~10% anual antes de "
        "inflación (~7% real). Un activo que promete mucho más, casi siempre "
        "esconde mucho más riesgo."
    ),
    "volatilidad": (
        "**¿Qué es?** Cuánto se sacude el precio. Es la medida más usada de "
        "*riesgo*: a mayor volatilidad, más grandes son las subidas y bajadas "
        "que vas a ver en tu cuenta.\n\n"
        "**Referencia:** un ETF diversificado ronda 15-20% anual; una acción "
        "individual 25-40%; Bitcoin ha superado el 60-80%. Si un -30% en tu "
        "pantalla te haría vender asustado, elegí activos menos volátiles: el "
        "peor error del principiante es vender en pánico."
    ),
    "drawdown": (
        "**¿Qué es?** La peor caída desde un máximo dentro del período. Es el "
        "número que te dice: *'en el peor momento, ¿cuánto habría llegado a "
        "perder?'*\n\n"
        "**¿Por qué importa?** Es el mejor test de estómago. El S&P 500 cayó "
        "~50% en 2008 y ~34% en 2020; se recuperó, pero solo ganó quien no "
        "vendió abajo. Antes de invertir preguntate: si esto cae ese porcentaje, "
        "¿aguanto sin vender?"
    ),
    "sharpe": (
        "**¿Qué es?** Mide cuánto rendimiento obtuviste *por cada unidad de "
        "riesgo* que asumiste (usando 4% como tasa libre de riesgo). Dos activos "
        "pueden rendir 10%, pero el que lo logró con menos sacudones es mejor "
        "inversión.\n\n"
        "**Referencia rápida:** menor a 0 = perdió contra no hacer nada; "
        "0 a 0,5 = pobre; 0,5 a 1 = aceptable; mayor a 1 = muy bueno. "
        "Se calcula sobre el período elegido: cambia si cambiás el período."
    ),
    "sma": (
        "**¿Qué es?** La media móvil de 200 días es el precio promedio del último "
        "año aproximadamente. Suaviza el ruido diario y muestra la tendencia de "
        "fondo.\n\n"
        "**¿Cómo leerla?** Precio **por encima** de la media de 200 días = "
        "tendencia alcista; **por debajo** = tendencia bajista. Muchos "
        "inversores de largo plazo la usan solo como contexto, no como señal de "
        "compra/venta: los índices pasan la mayor parte del tiempo por encima."
    ),
    "rsi": (
        "**¿Qué es?** El RSI (índice de fuerza relativa, 0 a 100) mide si el "
        "precio subió o bajó demasiado rápido en las últimas ~2 semanas.\n\n"
        "**¿Cómo leerlo?** Arriba de 70 = 'sobrecomprado' (subió muy rápido, "
        "puede corregir); abajo de 30 = 'sobrevendido' (cayó muy rápido, puede "
        "rebotar). Es un indicador de corto plazo: para el inversor de largo "
        "plazo es solo contexto, no una orden de actuar."
    ),
    "pe": (
        "**¿Qué es?** El P/E (precio/ganancias) dice cuántos años de ganancias "
        "actuales estás pagando por la empresa. P/E de 20 = pagás 20 veces lo "
        "que gana por año.\n\n"
        "**Referencia:** el promedio histórico del mercado americano ronda "
        "15-20. Un P/E alto (30+) significa que el mercado espera mucho "
        "crecimiento: si no llega, la acción cae. Un P/E muy bajo puede ser "
        "ganga... o una empresa con problemas. Nunca uses el P/E solo."
    ),
    "dividendo": (
        "**¿Qué es?** El porcentaje del precio que la empresa reparte en "
        "efectivo cada año. Con yield de 3%, cada \\$1.000 invertidos te pagan "
        "~\\$30 al año.\n\n"
        "**Ojo:** un yield altísimo (7%+) suele ser una trampa: el precio cayó "
        "porque la empresa tiene problemas y el dividendo puede recortarse. "
        "Desde el exterior, los dividendos de EE.UU. sufren retención de "
        "impuestos (30% directo, 15% vía ETFs UCITS)."
    ),
    "beta": (
        "**¿Qué es?** Cuánto se mueve el activo cuando se mueve el mercado. "
        "Beta 1 = igual que el mercado; 1,5 = se mueve un 50% más (sube más y "
        "cae más); 0,5 = la mitad, más defensivo.\n\n"
        "**Uso práctico:** si tu cartera está llena de betas altos, vas a "
        "sentir las crisis con mucha más fuerza."
    ),
}
