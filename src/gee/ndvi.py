import ee
import logging

logger = logging.getLogger(__name__)


def _mask_clouds(image: ee.Image) -> ee.Image:
    """
    Aplica cloud-masking a nivel de pixel usando la banda SCL de Sentinel-2.
    
    Clases SCL que se enmascaran:
    - 3: Sombra de nube
    - 8: Nube de probabilidad media
    - 9: Nube de probabilidad alta
    - 10: Cirrus
    """
    scl = image.select('SCL')
    mask = (scl.neq(3)
              .And(scl.neq(8))
              .And(scl.neq(9))
              .And(scl.neq(10)))
    return image.updateMask(mask)


def _get_coleccion(region: ee.Geometry, fecha_inicio: str, fecha_fin: str) -> ee.Image:
    """
    Obtiene mosaico Sentinel-2 con cloud-masking por pixel aplicado.
    """
    return (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(fecha_inicio, fecha_fin)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
        .map(_mask_clouds)
        .median())


def _get_ndvi(region: ee.Geometry, fecha_inicio: str, fecha_fin: str) -> ee.Image:
    """Obtiene imagen NDVI con cloud-masking aplicado."""
    return _get_coleccion(region, fecha_inicio, fecha_fin).normalizedDifference(['B8', 'B4']).rename('ndvi')


def _get_evi(region: ee.Geometry, fecha_inicio: str, fecha_fin: str) -> ee.Image:
    """Obtiene imagen EVI con cloud-masking aplicado."""
    mosaico = _get_coleccion(region, fecha_inicio, fecha_fin)
    return mosaico.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
        {'NIR': mosaico.select('B8'),
         'RED': mosaico.select('B4'),
         'BLUE': mosaico.select('B2')}
    ).rename('evi')


def _get_nbr(region: ee.Geometry, fecha_inicio: str, fecha_fin: str) -> ee.Image:
    """Obtiene imagen NBR con cloud-masking aplicado."""
    return _get_coleccion(region, fecha_inicio, fecha_fin).normalizedDifference(['B8', 'B12']).rename('nbr')


def analizar_salud_vegetal(geometria: ee.Geometry, nombre_sitio: str, anio_base: int = 2024, anio_actual: int = 2026) -> dict:
    """
    Analiza NDVI, EVI y NBR comparando dos años con cloud-masking por pixel.

    Args:
        geometria: Punto o poligono de Earth Engine
        nombre_sitio: Nombre descriptivo del sitio
        anio_base: Año de referencia (default 2024)
        anio_actual: Año actual (default 2026)

    Returns:
        dict con indices de ambos años y sus deltas
    """
    tipo_geo = geometria.type().getInfo()
    region = geometria.buffer(1000) if tipo_geo == 'Point' else geometria

    fecha_base_ini = f'{anio_base}-01-01'
    fecha_base_fin = f'{anio_base}-03-31'
    fecha_actual_ini = f'{anio_actual}-01-01'
    fecha_actual_fin = f'{anio_actual}-03-31'

    stats = {}
    for indice, func in [('ndvi', _get_ndvi), ('evi', _get_evi), ('nbr', _get_nbr)]:
        img_base = func(region, fecha_base_ini, fecha_base_fin)
        img_actual = func(region, fecha_actual_ini, fecha_actual_fin)

        val_base = img_base.reduceRegion(ee.Reducer.mean(), region, 10).get(indice).getInfo()
        val_actual = img_actual.reduceRegion(ee.Reducer.mean(), region, 10).get(indice).getInfo()

        if not val_base or not val_actual:
            raise ValueError(f"Datos insuficientes para {nombre_sitio} - indice {indice}")

        stats[indice] = {
            str(anio_base): round(val_base, 3),
            str(anio_actual): round(val_actual, 3),
            "delta": round(val_actual - val_base, 3)
        }

    logger.info("Analisis completado para %s (%s vs %s)", nombre_sitio, anio_base, anio_actual)
    return {
        "sitio": nombre_sitio,
        "anio_base": anio_base,
        "anio_actual": anio_actual,
        "indices": stats
    }


def analizar_poligono(vertices: list, nombre_sitio: str, anio_base: int = 2024, anio_actual: int = 2026) -> dict:
    """
    Analiza salud vegetal de un poligono definido por vertices.
    """
    if len(vertices) < 3:
        raise ValueError("Un poligono necesita minimo 3 vertices")

    geometria = ee.Geometry.Polygon([vertices]).simplify(maxError=10)
    return analizar_salud_vegetal(geometria, nombre_sitio, anio_base, anio_actual)