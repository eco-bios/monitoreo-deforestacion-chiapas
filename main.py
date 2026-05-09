import ee
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.gee.client import initialize_gee
from src.gee.ndvi import analizar_salud_vegetal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Monitoreo de Deforestación Chiapas",
    description="API para análisis de salud vegetal usando NDVI, EVI y NBR",
    version="1.0.0"
)

ZONAS = [
    {"nombre": "Selva Lacandona",  "lat": 16.8,  "lon": -91.5},
    {"nombre": "Montes Azules",    "lat": 16.5,  "lon": -91.2},
    {"nombre": "Palenque",         "lat": 17.5,  "lon": -92.0},
    {"nombre": "Escuintla",        "lat": 15.29, "lon": -92.60},
    {"nombre": "Catazajá",         "lat": 17.72, "lon": -91.71},
]


class SitioRequest(BaseModel):
    lat: float
    lon: float
    nombre: str = "Sitio personalizado"


@app.on_event("startup")
def startup():
    try:
        initialize_gee()
        logger.info("GEE inicializado correctamente")
    except Exception as e:
        logger.warning("GEE no inicializado al arrancar: %s", str(e))


@app.get("/")
def root():
    return {
        "proyecto": "Monitoreo de Deforestación Chiapas",
        "version": "1.0.0",
        "endpoints": ["/analizar", "/zonas", "/health", "/scheduler/analizar-zona"]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/zonas")
def listar_zonas():
    return {"zonas": ZONAS}


@app.post("/analizar")
def analizar(sitio: SitioRequest):
    """
    Analiza la salud vegetal de cualquier punto.
    """
    try:
        geometria = ee.Geometry.Point([sitio.lon, sitio.lat])
        resultado = analizar_salud_vegetal(geometria, sitio.nombre)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Error en análisis: %s", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.post("/scheduler/analizar-zona")
def analizar_zona_programada(zona_index: int = 0):
    """
    Endpoint para Cloud Scheduler — analiza una zona predefinida.
    zona_index: 0-4 según la lista de ZONAS
    """
    if zona_index < 0 or zona_index >= len(ZONAS):
        raise HTTPException(status_code=400, detail="Índice de zona inválido")

    zona = ZONAS[zona_index]
    try:
        geometria = ee.Geometry.Point([zona["lon"], zona["lat"]])
        resultado = analizar_salud_vegetal(geometria, zona["nombre"])
        logger.info("Zona analizada por scheduler: %s", zona["nombre"])
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Error en scheduler: %s", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")