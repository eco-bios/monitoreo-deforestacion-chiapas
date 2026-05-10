import ee
import logging

logger = logging.getLogger(__name__)


def _get_ndvi(region: ee.Geometry, fecha_inicio: str, fecha_fin: str) -> ee.Image:
    """Obtiene imagen NDVI para un periodo especifico."""
    coleccion = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(fecha_inicio, fecha_fin)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

    return coleccion.median().normalizedDifference(['B8', 'B4']).rename('ndvi')


def _get_evi(region: ee.Geometry, fecha_inicio: str, fecha_fin: str) -> ee.Image:
    """Obtiene imagen EVI para un periodo especifico."""
    coleccion = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(fecha_inicio, fecha_fin)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

    mosaico = coleccion.median()
    return mosaico.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
        {'NIR': mosaico.select('B8'),
         'RED': mosaico.select('B4'),
         'BLUE': mosaico.select('B2')}
    ).rename('evi')


def _get_nbr(region: ee.Geometry, fecha_inicio: str, fecha_fin: str) -> ee.Image:
    """Obtiene imagen NBR para deteccion de areas quemadas."""
    coleccion = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(fecha_inicio, fecha_fin)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

    return coleccion.median().normalizedDifference(['B8', 'B12']).rename('nbr')


def analizar_salud_vegetal(geometria: ee.Geometry, nombre_sitio: str) -> dict:
    """
    Analiza NDVI, EVI y NBR comparando 2024 vs 2026.
    """
    tipo_geo = geometria.type().getInfo()
    region = geometria.buffer(1000) if tipo_geo == 'Point' else geometria

    stats = {}
    for indice, func in [('ndvi', _get_ndvi), ('evi', _get_evi), ('nbr', _get_nbr)]:
        img_24 = func(region, '2024-01-01', '2024-01-31')
        img_26 = func(region, '2026-01-01', '2026-01-31')

        val_24 = img_24.reduceRegion(ee.Reducer.mean(), region, 10).get(indice).getInfo()
        val_26 = img_26.reduceRegion(ee.Reducer.mean(), region, 10).get(indice).getInfo()

        if not val_24 or not val_26:
            raise ValueError(f"Datos insuficientes para {nombre_sitio} - indice {indice}")

        stats[indice] = {
            "2024": round(val_24, 3),
            "2026": round(val_26, 3),
            "delta": round(val_26 - val_24, 3)
        }

    logger.info("Analisis completado para %s", nombre_sitio)
    return {"sitio": nombre_sitio, "indices": stats}


def analizar_poligono(vertices: list, nombre_sitio: str) -> dict:
    """
    Analiza salud vegetal de un poligono definido por vertices.
    """
    if len(vertices) < 3:
        raise ValueError("Un poligono necesita minimo 3 vertices")

    geometria = ee.Geometry.Polygon([vertices]).simplify(maxError=10)
    return analizar_salud_vegetal(geometria, nombre_sitio)