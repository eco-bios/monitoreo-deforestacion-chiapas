import ee
import logging

logger = logging.getLogger(__name__)


def exportar_a_drive(
    imagen: ee.Image,
    nombre: str,
    region: ee.Geometry,
    carpeta: str = 'Proyecto_Monitoreo_Chiapas'
) -> ee.batch.Task:
    """
    Exporta una imagen GEE a Google Drive.

    Args:
        imagen: Imagen de Earth Engine a exportar
        nombre: Nombre del archivo de salida
        region: Área geográfica a exportar
        carpeta: Carpeta destino en Google Drive

    Returns:
        Tarea de exportación iniciada
    """
    area_exportar = region.buffer(2000).bounds()

    tarea = ee.batch.Export.image.toDrive(
        image=imagen,
        description=nombre,
        folder=carpeta,
        scale=10,
        region=area_exportar,
        fileFormat='GeoTIFF',
        formatOptions={'cloudOptimized': True}
    )

    tarea.start()
    logger.info("Exportación iniciada: %s → %s", nombre, carpeta)
    return tarea