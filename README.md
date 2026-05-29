# 🛰️ Monitoreo Forestal Chiapas

Sistema automatizado de monitoreo de salud vegetal en Chiapas, México. Analiza índices espectrales usando imágenes satelitales Sentinel-2 a través de Google Earth Engine con cloud-masking por pixel, clasificación de cobertura vegetal y análisis multitemporal.

## 🌐 Demo en Producción

**Interfaz web:**
https://monitoreo-chiapas-306961522035.us-central1.run.app

**Documentación API:**
https://monitoreo-chiapas-306961522035.us-central1.run.app/docs

## 🏗️ Arquitectura
Sentinel-2 (ESA) → Google Earth Engine → FastAPI → GCP Cloud Run
↓
Cloud Scheduler (rotación diaria)
5 zonas de Chiapas automatizadas
## 📊 Índices Espectrales

| Índice | Bandas | Qué detecta |
|--------|--------|-------------|
| NDVI | B8, B4 | Salud vegetal general |
| EVI | B8, B4, B2 | Vegetación densa — no se satura en selva |
| NBR | B8, B12 | Áreas quemadas y recuperación post-incendio |
| NDWI | B3, B8 | Contenido de agua — distingue selva de pasto |
| BSI | B11, B4, B8, B2 | Suelo desnudo — detecta deforestación |

## 🌿 Clasificación de Cobertura Vegetal

El sistema clasifica automáticamente el tipo de vegetación combinando múltiples índices:

- **Selva o bosque maduro** — NDVI alto + NDWI alto + BSI bajo
- **Vegetación secundaria o pasto denso** — NDVI alto + NDWI bajo
- **Área quemada o perturbada** — NBR bajo + BSI alto
- **Suelo desnudo o deforestación reciente** — BSI alto
- **Vegetación dispersa o cultivos** — NDVI medio

## 🔬 Cloud-Masking

Implementa enmascaramiento de nubes a nivel de pixel usando la banda SCL de Sentinel-2, eliminando sombras de nubes (clase 3), nubes de probabilidad media (8), alta (9) y cirrus (10). Más preciso que el filtrado por porcentaje de escena.

## 🗺️ Zonas de Monitoreo Automatizado

| Zona | Coordenadas | Día |
|------|-------------|-----|
| Selva Lacandona | 16.8, -91.5 | Lunes |
| Montes Azules | 16.5, -91.2 | Martes |
| Palenque | 17.5, -92.0 | Miércoles |
| Escuintla | 15.29, -92.60 | Jueves |
| Catazajá | 17.72, -91.71 | Viernes |

## 🚀 Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del servicio |
| GET | `/zonas` | Lista zonas predefinidas |
| POST | `/analizar` | Análisis por punto con años configurables |
| POST | `/analizar/poligono` | Análisis por polígono de vértices |
| POST | `/analizar/serie-temporal` | Serie temporal 2017-2026 por punto |
| POST | `/analizar/serie-temporal/poligono` | Serie temporal por polígono |
| POST | `/scheduler/analizar-zona` | Endpoint para Cloud Scheduler |

### Ejemplo — Análisis por punto

```bash
curl -X POST https://monitoreo-chiapas-306961522035.us-central1.run.app/analizar \
  -H "Content-Type: application/json" \
  -d '{"lat": 16.8, "lon": -91.5, "nombre": "Selva Lacandona", "anio_base": 2018, "anio_actual": 2026}'
```

### Respuesta

```json
{
  "sitio": "Selva Lacandona",
  "anio_base": 2018,
  "anio_actual": 2026,
  "indices": {
    "ndvi": {"2018": 0.771, "2026": 0.792, "delta": 0.021},
    "evi":  {"2018": 2.301, "2026": 2.283, "delta": -0.018},
    "nbr":  {"2018": 0.498, "2026": 0.509, "delta": 0.011},
    "ndwi": {"2018": -0.182, "2026": -0.171, "delta": 0.011},
    "bsi":  {"2018": -0.201, "2026": -0.198, "delta": 0.003}
  },
  "clasificacion": {
    "2018": "Selva o bosque maduro",
    "2026": "Selva o bosque maduro"
  }
}
```

## 🛠️ Stack Tecnológico

- **Google Earth Engine** — procesamiento de imágenes satelitales
- **Sentinel-2** — imágenes multiespectrales 10m resolución
- **FastAPI** — API REST con documentación automática
- **Docker** — contenedor de producción
- **GCP Cloud Run** — deploy serverless
- **GCP Cloud Scheduler** — automatización diaria de 5 zonas
- **pytest** — tests unitarios
- **GitHub Actions** — CI/CD automatizado

## 📁 Estructura del Proyecto
├── src/
│   └── gee/
│       ├── client.py       # Conexión con GEE y Service Account
│       ├── ndvi.py         # Índices espectrales, clasificación y serie temporal
│       └── exportacion.py  # Exportación a Google Drive
├── static/
│   └── index.html          # Interfaz web para usuarios
├── tests/
│   └── test_ndvi.py        # Tests unitarios
├── notebooks/              # Análisis exploratorio original
├── main.py                 # API FastAPI
├── Dockerfile
└── .github/workflows/      # CI/CD
## ⚙️ Instalación Local

```bash
git clone https://github.com/eco-bios/monitoreo-deforestacion-chiapas.git
cd monitoreo-deforestacion-chiapas
pip install -r requirements.txt
cp .env.example .env  # Configura GEE_PROJECT_ID
uvicorn main:app --reload
```

## 🧪 Tests

```bash
pytest tests/ -v
```

## 👤 Autor

Biólogo con conocimientos en tecnología geoespacial y monitoreo ambiental.
Chiapas, México.