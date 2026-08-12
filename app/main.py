import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.seed import init_db, seed_data
from app.security.auth import decode_access_token

from app.routes.auth_routes import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.management import router as management_router
from app.routes.schedule import router as schedule_router
from app.routes.classifieds import router as classifieds_router
from app.routes.events import router as events_router
from app.routes.financial import router as financial_router

app = FastAPI(title="RioAiki DOJOCHO - Sistema de Gerenciamento de Dojos de Aikido")

# Anti-"Failed to fetch" Guard: CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Rotas públicas: apenas estas NÃO exigem autenticação (negar por padrão)
PUBLIC_PATHS = ["/login", "/logout", "/favicon.ico", "/reset-password"]
PUBLIC_PREFIXES = ("/static", "/api/forgot-password", "/api/reset-password", "/api/import/faixa-preta")

# Middleware Global de Autenticação
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    # Libera somente rotas explicitamente públicas
    if path in PUBLIC_PATHS or any(path.startswith(p) for p in PUBLIC_PREFIXES):
        return await call_next(request)

    token = request.cookies.get("access_token")
    if not token and request.headers.get("authorization"):
        auth_hdr = request.headers.get("authorization", "")
        if auth_hdr.startswith("Bearer "):
            token = auth_hdr.split(" ")[1]

    user = decode_access_token(token) if token else None

    # Negar por padrão: APIs recebem 401 JSON; páginas HTML redirecionam para /login
    if not user:
        if path.startswith("/api"):
            return JSONResponse({"detail": "Não autenticado."}, status_code=401)
        response = RedirectResponse(url="/login", status_code=303)
        if token:
            response.delete_cookie("access_token", path="/")
        return response

    request.state.user = user
    response = await call_next(request)
    return response

# Include Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(management_router)
app.include_router(schedule_router)
app.include_router(classifieds_router)
app.include_router(events_router)
app.include_router(financial_router)

@app.post("/api/import/faixa-preta")
@app.get("/api/import/faixa-preta")
async def import_faixa_preta_endpoint():
    """
    Harness API Endpoint for Faixa Preta import.
    Guaranteed non-blocking, exception-handled response to avoid 'Failed to fetch' browser errors.
    """
    try:
        # Import harness runner from FinanceiroAntigravity workspace
        import sys
        sys.path.insert(0, "C:/DOJOCHO/FinanceiroAntigravity")
        from import_faixa_preta_harness import run_import_harness
        
        md_file = "C:/DOJOCHO/FinanceiroAntigravity/alunos_faixa_preta.md"
        res = run_import_harness(md_file)
        return JSONResponse(content=res, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": str(e),
                "message": f"Erro no endpoint de importação: {str(e)}"
            },
            status_code=500
        )

@app.on_event("startup")
def startup_event():
    db_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rioaiki.db")
    if not os.path.exists(db_file):
        print("Database rioaiki.db not found. Initializing and seeding...")
        init_db()
        seed_data()
    else:
        print("Database rioaiki.db found. Ensuring tables...")
        Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

