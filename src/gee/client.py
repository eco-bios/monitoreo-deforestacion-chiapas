import ee
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def initialize_gee() -> bool:
    """
    Inicializa la conexión con Google Earth Engine.
    Usa variables de entorno en lugar de credenciales hardcodeadas.

    Returns:
        bool: True si la conexión fue exitosa

    Raises:
        EnvironmentError: Si GEE_PROJECT_ID no está configurado
        ee.EEException: Si falla la conexión con GEE
    """
    load_dotenv()

    project_id = os.getenv("GEE_PROJECT_ID")

    if not project_id:
        raise EnvironmentError(
            "GEE_PROJECT_ID no encontrado. "
            "Revisa tu archivo .env"
        )

    try:
        ee.Initialize(project=project_id)
        ee.Image("USGS/SRTMGL1_003").getInfo()
        logger.info("Conexión con GEE exitosa. Proyecto: %s", project_id)
        return True

    except ee.EEException as e:
        logger.error("Error de GEE: %s", str(e))
        raise