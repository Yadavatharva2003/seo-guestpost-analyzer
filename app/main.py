from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router


app = FastAPI(title="SEO Guest Post Analyzer")

# -------------------------
# STATIC FILES
# -------------------------
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# -------------------------
# TEMPLATES
# -------------------------
templates = Jinja2Templates(directory="app/templates")

# -------------------------
# API ROUTES
# -------------------------
# routes.py already has prefix="/api"
app.include_router(router)

# -------------------------
# HOME PAGE
# -------------------------
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
