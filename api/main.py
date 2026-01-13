from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from src.resources.weather_resource import router as weather_router
from prometheus_fastapi_instrumentator import Instrumentator, metrics

tags_metadata = [
    {
        "name": "Health",
        "description": "Health check endpoints",
    },
    {
        "name": "Weather",
        "description": "Endpoints pour récupérer les données météo actuelles et les prévisions",
    },
]

app = FastAPI(
    title="CY Weather API",
    description="API for CY Weather application",
    version="0.1.0",
    openapi_tags=tags_metadata,
    redoc_url="/docs",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(
    prefix="/api",
)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="inprogress",
    inprogress_labels=True
)

instrumentator.instrument(app)
@app.on_event("startup")
async def _startup():
    instrumentator.expose(app)

@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "ok"}


app.include_router(router)
app.include_router(weather_router, prefix="/api")
