from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import parse, adapters, configure, simulate, audit, health
import uvicorn

app = FastAPI(
    title="FinSpark Integration Orchestration Engine",
    description="AI-powered enterprise integration configuration platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(parse.router, prefix="/api/parse", tags=["Document Parsing"])
app.include_router(adapters.router, prefix="/api/adapters", tags=["Adapter Registry"])
app.include_router(configure.router, prefix="/api/configure", tags=["Auto Configuration"])
app.include_router(simulate.router, prefix="/api/simulate", tags=["Simulation"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit Logs"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
