from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["backoffice"])


@router.get("/", response_class=HTMLResponse)
async def backoffice_home(request: Request):
    return templates.TemplateResponse(
        "backoffice/index.html",
        {
            "request": request,
            "title": "NeuroBank Backoffice",
        },
    )


@router.get("/health")
async def backoffice_health():
    return {"status": "ok", "component": "backoffice"}

