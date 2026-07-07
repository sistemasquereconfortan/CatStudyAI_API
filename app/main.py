from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend modular con workers asíncronos y soporte para RAG en CatStudyAI.",
    version="1.0.0",
)

# Registrar rutas versionadas
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"], summary="Verificar estado del servicio")
def health_check() -> dict[str, str]:
    """
    Retorna el estado de salud de la API.
    """
    return {"status": "ok"}
