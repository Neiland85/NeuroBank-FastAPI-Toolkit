"""
Backoffice dashboard router.

Provides administrative HTML endpoints for NeuroBank.
This module must only expose an APIRouter instance named `router`.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(
    prefix="/backoffice",
    tags=["Backoffice"],
)


@router.get(
    "/",
    response_class=HTMLResponse,
    name="backoffice_home",
    summary="Backoffice dashboard home",
)
async def backoffice_home() -> HTMLResponse:
    """Render the main backoffice dashboard page."""
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8" />
                <title>NeuroBank Backoffice</title>
            </head>
            <body>
                <h1>NeuroBank Admin Dashboard</h1>
                <p>Backoffice is up and running.</p>
            </body>
        </html>
        """,
        status_code=200,
    )
