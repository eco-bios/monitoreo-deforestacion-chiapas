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


def test_ndvi_rango_valido():
    """NDVI siempre debe estar entre -1 y 1"""
    resultado = calcular_ndvi(nir=0.6, red=0.2)
    assert -1 <= resultado <= 1


def test_ndvi_error_cero():
    """Debe lanzar error si NIR y Red son ambos cero"""
    with pytest.raises(ValueError):
        calcular_ndvi(nir=0, red=0)