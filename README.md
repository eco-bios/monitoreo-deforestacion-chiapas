# 🛰️ Monitoreo de Deforestación Chiapas

Pipeline automatizado para monitoreo de salud vegetal en Chiapas, México. Analiza índices espectrales NDVI, EVI y NBR usando imágenes satelitales Sentinel-2 a través de Google Earth Engine.

## 🌐 Demo en Producción

**API desplegada en GCP Cloud Run:**
https://monitoreo-chiapas-306961522035.us-central1.run.app

**Documentación interactiva:**
https://monitoreo-chiapas-306961522035.us-central1.run.app/docs

## 🏗️ Arquitectura
Sentinel-2 (ESA) → Google Earth Engine → FastAPI → GCP Cloud Run
↓
Cloud Scheduler (rotación diaria)
↓
Cloud Storage (historial)
## 📊 Índices Espectrales

| Índice | Bandas | Qué detecta |
|--------|--------|-------------|
| NDVI | B8, B4 | Salud vegetal general |
| EVI | B8, B4, B2 | Vegetación densa — no se satura en selva |
| NBR | B8, B12 | Áreas quemadas y recuperación post-incendio |

## 🗺️ Zonas de Monitoreo

| Zona | Coordenadas |
|------|-------------|
| Selva Lacandona | 16.8, -91.5 |
| Montes Azules | 16.5, -91.2 |
| Palenque | 17.5, -92.0 |
| Escuintla | 15.29, -92.60 |
| Catazajá | 17.72, -91.71 |

## 🚀 Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del servicio |
| GET | `/zonas` | Lista zonas predefinidas |
| POST | `/analizar` | Análisis por coordenadas personalizadas |

### Ejemplo de uso

```bash
curl -X POST https://monitoreo-chiapas-306961522035.us-central1.run.app/analizar \
  -H "Content-Type: application/json" \
  -d '{"lat": 16.8, "lon": -91.5, "nombre": "Selva Lacandona"}'
```

### Respuesta

```json
{
  "sitio": "Selva Lacandona",
  "indices": {
    "ndvi": {"2024": 0.623, "2026": 0.541, "delta": -0.082},
    "evi":  {"2024": 0.489, "2026": 0.421, "delta": -0.068},
    "nbr":  {"2024": 0.712, "2026": 0.634, "delta": -0.078}
  }
}
```

## 🛠️ Stack Tecnológico

- **Google Earth Engine** — procesamiento de imágenes satelitales
- **Sentinel-2** — imágenes multiespectrales 10m resolución
- **FastAPI** — API REST con documentación automática
- **Docker** — contenedor de producción
- **GCP Cloud Run** — deploy serverless
- **GCP Cloud Scheduler** — automatización diaria
- **pytest** — tests unitarios
- **GitHub Actions** — CI/CD automatizado

## 📁 Estructura del Proyecto
├── src/
│   └── gee/
│       ├── client.py      # Conexión con GEE
│       ├── ndvi.py        # Cálculo NDVI, EVI, NBR
│       └── exportacion.py # Exportación a Drive
├── tests/
│   └── test_ndvi.py       # Tests unitarios
├── notebooks/             # Análisis exploratorio original
├── main.py                # API FastAPI
├── Dockerfile
└── .github/workflows/     # CI/CD
## ⚙️ Instalación Local

```bash
git clone https://github.com/eco-bios/monitoreo-deforestacion-chiapas.git
cd monitoreo-deforestacion-chiapas
pip install -r requirements.txt
cp .env.example .env  # Configura tu GEE_PROJECT_ID
uvicorn main:app --reload
```

## 🧪 Tests

```bash
pytest tests/ -v
```

## 👤 Autor

Biólogo especializado en tecnología geoespacial y monitoreo ambiental.
Chiapas, México. 