from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.generate_routes import router as generate_router
from app.routes.calendar_routes import router as calendar_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.chat_routes import router as chat_router
from app.routes.pertemuan_routes import router as pertemuan_router
from app.routes.knowledge_routes import router as knowledge_router
from app.routes.admin_auth_routes import router as admin_auth_router

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

app.include_router(
    chat_router,
    prefix="/api/chat",
    tags=["Tanya Wariga AI"]
)

app.include_router(
    pertemuan_router,
    prefix="/api/pertemuan",
    tags=["Pertemuan Lanang Istri"]
)

app.include_router(
    knowledge_router,
    prefix="/api/knowledge",
    tags=["Knowledge Upload"]
)

app.include_router(
    admin_auth_router,
    prefix="/api/admin",
    tags=["Admin Auth"]
)


@app.get("/")
def root():
    return {
        "message": "Backend Kalender Bali Wariga berjalan"
    }
