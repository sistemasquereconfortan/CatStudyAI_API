from fastapi import FastAPI

app = FastAPI(title="Arquitectura GitFlow Backend")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
