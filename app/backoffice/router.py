from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(
    prefix="/backoffice",
    tags=["Backoffice Dashboard"],
)


@router.get("/", response_class=HTMLResponse)
async def backoffice_home():
    return """
    <html>
        <head>
            <title>NeuroBank Backoffice</title>
        </head>
        <body>
            <h1>NeuroBank Admin Dashboard</h1>
            <p>Backoffice is up and running.</p>
        </body>
    </html>
    """
