import ee
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.gee.client import initialize_gee
from src.gee.ndvi import analizar_salud_vegetal, analizar_poligono, serie_temporal, serie_temporal_poligono

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Monitoreo de Deforestación Chiapas",
    description="API para análisis de salud vegetal usando NDVI, EVI y NBR",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

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
    anio_base: int = 2024
    anio_actual: int = 2026


class PoligonoRequest(BaseModel):
    vertices: list
    nombre: str = "Poligono personalizado"
    anio_base: int = 2024
    anio_actual: int = 2026


class SerieTemporalRequest(BaseModel):
    lat: float
    lon: float
    nombre: str = "Sitio personalizado"
    anio_inicio: int = 2017
    anio_fin: int = 2026


class SerieTemporalPoligonoRequest(BaseModel):
    vertices: list
    nombre: str = "Poligono personalizado"
    anio_inicio: int = 2017
    anio_fin: int = 2026


@app.on_event("startup")
def startup():
    try:
        initialize_gee()
        logger.info("GEE inicializado correctamente")
    except Exception as e:
        logger.warning("GEE no inicializado al arrancar: %s", str(e))


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/zonas")
def listar_zonas():
    return {"zonas": ZONAS}


@app.post("/analizar")
def analizar(sitio: SitioRequest):
    """Analiza la salud vegetal de cualquier punto."""
    try:
        geometria = ee.Geometry.Point([sitio.lon, sitio.lat])
        resultado = analizar_salud_vegetal(geometria, sitio.nombre, sitio.anio_base, sitio.anio_actual)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Error en analisis: %s", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.post("/analizar/poligono")
def analizar_por_poligono(request: PoligonoRequest):
    """Analiza salud vegetal de un poligono definido por vertices."""
    try:
        resultado = analizar_poligono(request.vertices, request.nombre, request.anio_base, request.anio_actual)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error en analisis de poligono: %s", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.post("/analizar/serie-temporal")
def analizar_serie_temporal(request: SerieTemporalRequest):
    """
    Analiza la serie temporal año por año.
    Detecta incendios, deforestacion y recuperacion en el tiempo.
    """
    try:
        geometria = ee.Geometry.Point([request.lon, request.lat])
        resultado = serie_temporal(geometria, request.nombre, request.anio_inicio, request.anio_fin)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error en serie temporal: %s", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.post("/analizar/serie-temporal/poligono")
def analizar_serie_temporal_poligono(request: SerieTemporalPoligonoRequest):
    """Serie temporal para un poligono definido por vertices."""
    try:
        resultado = serie_temporal_poligono(request.vertices, request.nombre, request.anio_inicio, request.anio_fin)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error en serie temporal poligono: %s", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.post("/scheduler/analizar-zona")
def analizar_zona_programada(zona_index: int = 0):
    """Endpoint para Cloud Scheduler — analiza una zona predefinida."""
    if zona_index < 0 or zona_index >= len(ZONAS):
        raise HTTPException(status_code=400, detail="Indice de zona invalido")

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