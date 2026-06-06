# CatStudyAI Backend

API independiente del MVP, construida con FastAPI para soportar autenticacion, gestion de materiales, consultas RAG, evaluaciones y procesos asincronos.

## Proposito

Este repositorio concentra la logica de servidor, persistencia, seguridad, orquestacion de workers y adaptadores hacia servicios externos.

## Enfoque de arquitectura

Se adopta un monolito modular con workers asincronos, alineado con la documentacion de arquitectura del proyecto. El backend expone endpoints REST, enruta tareas pesadas a cola y conserva integridad multiusuario con enfoque RBAC.

## Patrones aplicados

- Repository: desacopla acceso a datos de reglas de negocio.
- Factory: construye generadores o flujos segun tipo de evaluacion.
- Strategy: permite cambiar parseo, chunking y retrieval sin romper el flujo.
- Observer: base para eventos de finalizacion y actualizacion de estado.
- Dependency Injection: facilita pruebas y reemplazo de implementaciones.
- Adapter: encapsula integraciones con DB, queue, storage y LLM.

## Estructura actual

- `app/main.py`: punto de entrada de la API.
- `app/api/`: capa de rutas.
- `app/api/v1/`: versionado de endpoints.
- `app/core/`: configuracion y seguridad transversal.
- `app/domains/`: modulos por dominio.
- `app/domains/auth/`: autenticacion y autorizacion.
- `app/domains/users/`: usuarios y perfiles.
- `app/domains/rooms/`: salas y membresias.
- `app/domains/documents/`: documentos y estado de ingesta.
- `app/domains/rag/`: consulta semantica y recuperacion.
- `app/domains/quizzes/`: generacion y evaluacion de reactivos.
- `app/domains/webhooks/`: callbacks internos de proceso.
- `app/infrastructure/`: integraciones tecnicas.
- `app/infrastructure/db/`: capa de persistencia relacional.
- `app/infrastructure/storage/`: acceso a object storage.
- `app/infrastructure/vector_store/`: operaciones vectoriales.
- `app/infrastructure/llm/`: proveedor de modelos.
- `app/infrastructure/queue/`: cola y mensajeria.
- `app/workers/`: procesamiento asincrono.
- `app/workers/tasks/`: tareas de cola.
- `app/workers/parsers/`: parseo por tipo de archivo.
- `app/workers/chunking/`: segmentacion de contenido.
- `app/workers/embedding/`: vectorizacion de chunks.
- `tests/`: pruebas.

## Por que este enfoque

El backend debe sostener flujos sincronos y asincronos con reglas sensibles. Separar dominio, aplicacion e infraestructura reduce acoplamiento y facilita evolucionar el motor RAG sin rehacer el nucleo.

## Archivos init

Se incluyen `__init__.py` en paquetes del backend para mantener estructura versionada y preparar importacion modular desde el inicio.

## Flujo

1. `api/v1` recibe y valida solicitudes.
2. `domains` aplica reglas del negocio y controles de acceso.
3. `infrastructure` persiste datos o consulta servicios externos.
4. `workers` ejecuta tareas pesadas fuera del ciclo HTTP.

## Por qué Git Flow

Git Flow reduce el riesgo en cambios que cruzan API, dominio e integraciones. También ayuda a separar trabajo experimental, integración y liberación final, algo útil cuando el backend combina solicitudes síncronas, colas y workers.

- `main`: rama estable para producción.
- `develop`: rama de integración continua.
- `feature/*`: funcionalidades nuevas o mejoras aisladas.
- `release/*`: estabilización de una versión.
- `hotfix/*`: reparaciones urgentes en producción.

## Convenciones tecnicas

- Mantener reglas de negocio desacopladas de detalles de framework.
- Encapsular integraciones externas en `infrastructure`.
- Evitar logica de transporte dentro de `domains`.
- Tratar seguridad, RLS y autorizacion como requisitos base.