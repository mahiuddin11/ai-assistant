from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Hello World Service")

Instrumentator().instrument(app).expose(app)


@app.get("/")
def root():
    return {"message": "AI Assistant Platform - Foundation service is running"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}