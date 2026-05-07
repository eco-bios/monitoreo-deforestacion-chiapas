import pytest

def calcular_ndvi(nir, red):
    """
    Calcula el NDVI dado los valores de las bandas NIR y Red.
    NDVI = (NIR - Red) / (NIR + Red)
    """
    if nir + red == 0:
        raise ValueError("NIR y Red no pueden ser ambos cero")
    return (nir - red) / (nir + red)


def test_ndvi_vegetacion_saludable():
    """Vegetación saludable tiene NDVI cercano a 1"""
    resultado = calcular_ndvi(nir=0.8, red=0.1)
    assert resultado > 0.5


def test_ndvi_suelo_desnudo():
    """Suelo desnudo tiene NDVI cercano a 0"""
    resultado = calcular_ndvi(nir=0.3, red=0.3)
    assert -0.1 < resultado < 0.1


import pytest


# ── Tests matemáticos — no necesitan GEE ──────────────────────────────────────

def calcular_ndvi(nir, red):
    if nir + red == 0:
        raise ValueError("NIR y Red no pueden ser ambos cero")
    return (nir - red) / (nir + red)


def calcular_evi(nir, red, blue):
    denominador = nir + 6 * red - 7.5 * blue + 1
    if denominador == 0:
        raise ValueError("Denominador EVI no puede ser cero")
    return 2.5 * ((nir - red) / denominador)


def calcular_nbr(nir, swir):
    if nir + swir == 0:
        raise ValueError("NIR y SWIR no pueden ser ambos cero")
    return (nir - swir) / (nir + swir)


# ── NDVI ──────────────────────────────────────────────────────────────────────

def test_ndvi_vegetacion_saludable():
    assert calcular_ndvi(nir=0.8, red=0.1) > 0.5

def test_ndvi_suelo_desnudo():
    resultado = calcular_ndvi(nir=0.3, red=0.3)
    assert -0.1 < resultado < 0.1

def test_ndvi_rango_valido():
    resultado = calcular_ndvi(nir=0.6, red=0.2)
    assert -1 <= resultado <= 1

def test_ndvi_error_cero():
    with pytest.raises(ValueError):
        calcular_ndvi(nir=0, red=0)


# ── EVI ───────────────────────────────────────────────────────────────────────

def test_evi_vegetacion_densa():
    resultado = calcular_evi(nir=0.8, red=0.1, blue=0.05)
    assert resultado > 0.3

def test_evi_vegetacion_rango_positivo():
    """EVI positivo en vegetación con NIR alto"""
    resultado = calcular_evi(nir=0.8, red=0.1, blue=0.05)
    assert resultado > 0

def test_evi_suelo_desnudo():
    """EVI cercano a cero en suelo sin vegetación"""
    resultado = calcular_evi(nir=0.3, red=0.28, blue=0.25)
    assert -0.2 < resultado < 0.2

# ── NBR ───────────────────────────────────────────────────────────────────────

def test_nbr_bosque_sano():
    """Bosque sano tiene NBR alto — NIR alto, SWIR bajo"""
    resultado = calcular_nbr(nir=0.8, swir=0.1)
    assert resultado > 0.5

def test_nbr_area_quemada():
    """Área quemada tiene NBR negativo — NIR bajo, SWIR alto"""
    resultado = calcular_nbr(nir=0.1, swir=0.8)
    assert resultado < 0

def test_nbr_error_cero():
    with pytest.raises(ValueError):
        calcular_nbr(nir=0, swir=0)