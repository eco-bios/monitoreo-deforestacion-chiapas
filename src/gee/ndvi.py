import ee
import logging

logger = logging.getLogger(__name__)


def _mask_clouds(image: ee.Image) -> ee.Image:
    """
    Aplica cloud-masking a nivel de pixel usando la banda SCL de Sentinel-2.
    Clases enmascaradas: 3=sombra, 8=nube media, 9=nube alta, 10=cirrus
    """
    scl = image.select('SCL')
    mask = (scl.neq(3)
              .And(scl.neq(8))
              .And(scl.neq(9))
              .And(scl.neq(10)))
    return image.updateMask(mask)


def _get_coleccion(region: ee.Geometry, fecha_inicio: str, fecha_fin: str) -> ee.Image:
    """Obtiene mosaico Sentinel-2 con cloud-masking por pixel."""
    return (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(fecha_inicio, fecha_fin)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
        .map(_mask_clouds)
        .median())


def _calcular_indices(mosaico: ee.Image, region: ee.Geometry) -> dict:
    """
    Calcula todos los indices espectrales de un mosaico.
    Retorna dict con valores medios por zona.
    """
    # NDVI — Salud vegetal general
    ndvi = mosaico.normalizedDifference(['B8', 'B4']).rename('ndvi')

    # EVI — Vegetacion densa, no se satura en selva
    evi = mosaico.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
        {'NIR': mosaico.select('B8'),
         'RED': mosaico.select('B4'),
         'BLUE': mosaico.select('B2')}
    ).rename('evi')

    # NBR — Estado post-incendio
    nbr = mosaico.normalizedDifference(['B8', 'B12']).rename('nbr')

    # NDWI — Contenido de agua en vegetacion (selva madura vs pasto)
    ndwi = mosaico.normalizedDifference(['B3', 'B8']).rename('ndwi')

    # BSI — Indice de suelo desnudo (detecta deforestacion)
    bsi = mosaico.expression(
        '((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))',
        {'SWIR': mosaico.select('B11'),
         'RED': mosaico.select('B4'),
         'NIR': mosaico.select('B8'),
         'BLUE': mosaico.select('B2')}
    ).rename('bsi')

    imagen_indices = ndvi.addBands(evi).addBands(nbr).addBands(ndwi).addBands(bsi)

    stats = imagen_indices.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=10
    ).getInfo()

    return {
        'ndvi': round(stats.get('ndvi', 0) or 0, 3),
        'evi':  round(stats.get('evi', 0) or 0, 3),
        'nbr':  round(stats.get('nbr', 0) or 0, 3),
        'ndwi': round(stats.get('ndwi', 0) or 0, 3),
        'bsi':  round(stats.get('bsi', 0) or 0, 3),
    }


def _clasificar_vegetacion(indices: dict) -> str:
    """
    Clasifica el tipo de cobertura vegetal basado en combinacion de indices.

    Logica:
    - Selva/bosque maduro: NDVI alto + NDWI alto + BSI bajo
    - Pasto/cultivo:       NDVI medio + NDWI bajo + BSI medio
    - Suelo desnudo:       NDVI bajo  + BSI alto
    - Area quemada:        NBR bajo   + BSI alto
    """
    ndvi = indices['ndvi']
    ndwi = indices['ndwi']
    bsi  = indices['bsi']
    nbr  = indices['nbr']

    if nbr < 0.1 and bsi > 0.1:
        return "Area quemada o perturbada"
    elif bsi > 0.2:
        return "Suelo desnudo o deforestacion reciente"
    elif ndvi > 0.5 and ndwi > -0.1:
        return "Selva o bosque maduro"
    elif ndvi > 0.4 and ndwi < -0.1:
        return "Vegetacion secundaria o pasto denso"
    elif ndvi > 0.2:
        return "Vegetacion dispersa o cultivos"
    else:
        return "Suelo desnudo o vegetacion muy escasa"


def analizar_salud_vegetal(geometria: ee.Geometry, nombre_sitio: str, anio_base: int = 2024, anio_actual: int = 2026) -> dict:
    """
    Analiza todos los indices espectrales comparando dos años.
    Incluye clasificacion de tipo de vegetacion.
    """
    tipo_geo = geometria.type().getInfo()
    region = geometria.buffer(1000) if tipo_geo == 'Point' else geometria

    fecha_base_ini = f'{anio_base}-01-01'
    fecha_base_fin = f'{anio_base}-03-31'
    fecha_actual_ini = f'{anio_actual}-01-01'
    fecha_actual_fin = f'{anio_actual}-03-31'

    mosaico_base   = _get_coleccion(region, fecha_base_ini, fecha_base_fin)
    mosaico_actual = _get_coleccion(region, fecha_actual_ini, fecha_actual_fin)

    indices_base   = _calcular_indices(mosaico_base, region)
    indices_actual = _calcular_indices(mosaico_actual, region)

    indices = {}
    for key in indices_base:
        indices[key] = {
            str(anio_base):   indices_base[key],
            str(anio_actual): indices_actual[key],
            'delta': round(indices_actual[key] - indices_base[key], 3)
        }

    clasificacion_base   = _clasificar_vegetacion(indices_base)
    clasificacion_actual = _clasificar_vegetacion(indices_actual)

    logger.info("Analisis completado: %s (%s vs %s)", nombre_sitio, anio_base, anio_actual)

    return {
        "sitio": nombre_sitio,
        "anio_base": anio_base,
        "anio_actual": anio_actual,
        "indices": indices,
        "clasificacion": {
            str(anio_base):   clasificacion_base,
            str(anio_actual): clasificacion_actual
        }
    }


def analizar_poligono(vertices: list, nombre_sitio: str, anio_base: int = 2024, anio_actual: int = 2026) -> dict:
    """Analiza salud vegetal de un poligono definido por vertices."""
    if len(vertices) < 3:
        raise ValueError("Un poligono necesita minimo 3 vertices")

    geometria = ee.Geometry.Polygon([vertices]).simplify(maxError=10)
    return analizar_salud_vegetal(geometria, nombre_sitio, anio_base, anio_actual)