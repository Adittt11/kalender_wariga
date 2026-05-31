from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.generate_routes import router as generate_router
from app.routes.calendar_routes import router as calendar_router
from app.routes.dashboard_routes import router as dashboard_router

app = FastAPI(title="Kalender Bali Wariga API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    generate_router,
    prefix="/api/generate",
    tags=["Generate Kalender"]
)

app.include_router(
    calendar_router,
    prefix="/api/calendar",
    tags=["Calendar"]
)

app.include_router(
    dashboard_router,
    prefix="/api/dashboard",
    tags=["Dashboard Calendar"]
)


@app.get("/")
def root():
    return {
        "message": "Backend Kalender Bali Wariga berjalan"
    }
