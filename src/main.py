import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.api.v1.router import v1_router
from src.config import settings

app = FastAPI(
    title="LODEX Middleware API",
    description=(
        "Decoupled, multi-tenant knowledge indexing and grounded retrieval engine "
        "designed to power semantic search and conversational question-answering across web applications."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for cross-origin integration (Next.js, Laravel, React, Vue, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static branding assets (SVG logos, previews)
assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

app.include_router(v1_router)

# Path to Dashboard HTML template
template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard():
    """Serve the interactive LODEX Dark-Mode Playground and Dashboard."""
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h2>LODEX Middleware is Running</h2><p>Visit <a href='/docs'>/docs</a> for API docs.</p>")


@app.get("/health", tags=["System"])
async def health_check():
    """System health and operational status check."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "qdrant_mode": settings.QDRANT_MODE,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
    }


@app.get("/api/info", tags=["System"])
async def api_info():
    """Raw JSON service information."""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "dashboard": "/",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
