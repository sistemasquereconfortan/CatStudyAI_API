from uuid import UUID
from typing import Any, Dict, Optional
from fastapi import APIRouter, Path, HTTPException, status
from pydantic import BaseModel, Field
from celery.result import AsyncResult
from app.workers.tasks.document_tasks import process_document_task

router = APIRouter()

# --- Modelos de Pydantic para Entrada/Salida (Swagger JSON schemas) ---

class DocumentProcessRequest(BaseModel):
    document_id: UUID = Field(
        ...,
        description="Identificador único (UUID) del documento registrado en la base de datos.",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    file_url: str = Field(
        ...,
        description="URL absoluta de almacenamiento (Supabase Storage / S3) donde reside el documento.",
        examples=["https://supabase.co/storage/v1/object/public/documents/lecture1.pdf"]
    )

class TaskTriggerResponse(BaseModel):
    task_id: str = Field(
        ...,
        description="El identificador único de la tarea en la cola de Celery.",
        examples=["a2b3c4d5-e6f7-8a9b-0c1d-2e3f4a5b6c7d"]
    )
    status: str = Field(
        ...,
        description="El estado inicial de la tarea encolada.",
        examples=["PENDING"]
    )
    message: str = Field(
        ...,
        description="Mensaje indicando que la tarea ha sido encolada con éxito.",
        examples=["Tarea de procesamiento de documento encolada correctamente."]
    )

class TaskStatusResponse(BaseModel):
    task_id: str = Field(
        ...,
        description="El identificador de la tarea consultada.",
        examples=["a2b3c4d5-e6f7-8a9b-0c1d-2e3f4a5b6c7d"]
    )
    status: str = Field(
        ...,
        description="El estado actual de la tarea de Celery (PENDING, PROGRESS, SUCCESS, FAILURE, etc.).",
        examples=["PROGRESS"]
    )
    info: Optional[Dict[str, Any]] = Field(
        None,
        description="Detalle o progreso actual de la tarea en ejecución o el resultado final una vez completada.",
        examples=[{"step": "descargando", "progress": 10}]
    )

# --- Endpoints de la API ---

@router.post(
    "/process-document",
    response_model=TaskTriggerResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Encolar procesamiento de documento RAG",
    description=(
        "Recibe los metadatos de un documento y encola una tarea asíncrona de Celery "
        "para realizar la descarga, parsing, segmentación y vectorización (embeddings) "
        "del archivo en segundo plano, sin bloquear el servidor HTTP principal."
    ),
    response_description="Retorna el ID de la tarea y su estado para seguimiento."
)
def trigger_document_processing(payload: DocumentProcessRequest) -> Dict[str, Any]:
    # Encolar la tarea asíncrona enviando los parámetros
    task = process_document_task.delay(str(payload.document_id), payload.file_url)
    
    return {
        "task_id": task.id,
        "status": task.status,
        "message": "Tarea de procesamiento de documento encolada correctamente."
    }

@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estado de una tarea asíncrona",
    description=(
        "Consulta el estado actual y el resultado/progreso de una tarea de Celery "
        "almacenada en Redis utilizando su ID único."
    ),
    responses={
        404: {
            "description": "La tarea especificada no fue encontrada en el backend de resultados.",
            "content": {
                "application/json": {
                    "example": {"detail": "No se encontró la tarea con ID a2b3c4d5..."}
                }
            }
        }
    }
)
def get_task_status(
    task_id: str = Path(
        ...,
        description="El ID único de la tarea de Celery devuelto al encolar la misma.",
        examples=["a2b3c4d5-e6f7-8a9b-0c1d-2e3f4a5b6c7d"]
    )
) -> Dict[str, Any]:
    # Consultar el resultado asíncrono
    result = AsyncResult(task_id)
    
    # Extraer información de progreso o resultado
    info = None
    if result.state == "PROGRESS":
        info = result.info  # Contiene el diccionario de progreso
    elif result.ready():
        if result.successful():
            info = result.result  # Contiene el diccionario retornado por la tarea
        else:
            # En caso de error, retornar el string del error o detalles
            info = {"error": str(result.result)}
            
    return {
        "task_id": task_id,
        "status": result.state,
        "info": info
    }
