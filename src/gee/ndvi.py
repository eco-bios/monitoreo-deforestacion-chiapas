import ee
import logging

logger = logging.getLogger(__name__)


def _get_ndvi(region: ee.Geometry, fecha_inicio: str, fecha_fin: str) -> ee.Image:
    """Obtiene imagen NDVI para un período específico."""
    coleccion = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(fecha_inicio, fecha_fin)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

    return coleccion.median().normalizedDifference(['B8', 'B4']).rename('ndvi')


def _get_evi(region: ee.Geometry, fecha_inicio: str, fecha_fin: str) -> ee.Image:
    """Obtiene imagen EVI para un período específico."""
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
    """Obtiene imagen NBR para detección de áreas quemadas."""
    coleccion = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(fecha_inicio, fecha_fin)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

    return coleccion.median().normalizedDifference(['B8', 'B12']).rename('nbr')


def analizar_salud_vegetal(geometria: ee.Geometry, nombre_sitio: str) -> dict:
    """
    Analiza NDVI, EVI y NBR comparando 2024 vs 2026.

    Args:
        geometria: Punto o polígono de Earth Engine
        nombre_sitio: Nombre descriptivo del sitio

    Returns:
        dict con índices de 2024 y 2026 y sus deltas

    Raises:
        ValueError: Si no hay imágenes disponibles
    """
    tipo_geo = geometria.type().getInfo()
    region = geometria.buffer(1000) if tipo_geo == 'Point' else geometria

    # Calcular índices para ambos períodos
    stats = {}
    for indice, func in [('ndvi', _get_ndvi), ('evi', _get_evi), ('nbr', _get_nbr)]:
        img_24 = func(region, '2024-01-01', '2024-01-31')
        img_26 = func(region, '2026-01-01', '2026-01-31')

        val_24 = img_24.reduceRegion(ee.Reducer.mean(), region, 10).get(indice).getInfo()
        val_26 = img_26.reduceRegion(ee.Reducer.mean(), region, 10).get(indice).getInfo()

        if not val_24 or not val_26:
            raise ValueError(f"Datos insuficientes para {nombre_sitio} — índice {indice}")

        stats[indice] = {
            "2024": round(val_24, 3),
            "2026": round(val_26, 3),
            "delta": round(val_26 - val_24, 3)
        }

    logger.info("Análisis completado para %s", nombre_sitio)
    return {"sitio": nombre_sitio, "indices": stats}