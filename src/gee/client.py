import ee
import logging
import os
import json
import base64
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def initialize_gee() -> bool:
    """
    Inicializa la conexión con Google Earth Engine.
    Soporta dos modos:
    - Local: usa Application Default Credentials
    - Producción: usa GOOGLE_APPLICATION_CREDENTIALS_JSON (base64)
    
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
        # Modo producción — credenciales en base64
        credentials_b64 = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        
        if credentials_b64:
            credentials_json = base64.b64decode(credentials_b64).decode("utf-8")
            credentials_dict = json.loads(credentials_json)
            credentials = ee.ServiceAccountCredentials(
                email=credentials_dict["client_email"],
                key_data=json.dumps(credentials_dict)
            )
            ee.Initialize(credentials=credentials, project=project_id)
            logger.info("GEE inicializado con Service Account. Proyecto: %s", project_id)
        else:
            # Modo local — Application Default Credentials
            ee.Initialize(project=project_id)
            logger.info("GEE inicializado con ADC. Proyecto: %s", project_id)

        return True

    except ee.EEException as e:
        logger.error("Error de GEE: %s", str(e))
        raise 