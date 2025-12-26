from fastapi import FastAPI
from .database import Base, engine
from .routers import patient, admin
from .config import get_settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title=get_settings().app_name)

app.include_router(patient.router, prefix="/api/patient", tags=["patient"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/health")
def healthcheck():
    return {"status": "ok"}

