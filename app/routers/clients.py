from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.database import get_connection
from app.models import PHASE_COLOURS

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _colour(phase: str) -> str:
    return PHASE_COLOURS.get(phase, "#333333")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    conn = get_connection()
    clients = conn.execute(
        "SELECT id, name, goal, start_weight, created_at FROM clients ORDER BY name"
    ).fetchall()
    conn.close()
    return templates.TemplateResponse(request=request, name="index.html", context={"clients": clients})


@router.get("/clients/new", response_class=HTMLResponse)
async def new_client_form(request: Request):
    return templates.TemplateResponse(request=request, name="client_form.html", context={"client": None})


@router.post("/clients/new")
async def create_client(
    name: str = Form(...),
    goal: Optional[str] = Form(None),
    start_weight: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    contact_email: Optional[str] = Form(None),
    contact_phone: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    sw = float(start_weight) if start_weight else None
    conn = get_connection()
    with conn:
        cur = conn.execute(
            "INSERT INTO clients (name, goal, start_weight, date_of_birth, contact_email, contact_phone, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, goal, sw, date_of_birth, contact_email, contact_phone, notes),
        )
        client_id = cur.lastrowid
    conn.close()
    return RedirectResponse(f"/clients/{client_id}", status_code=303)


@router.get("/clients/{client_id}", response_class=HTMLResponse)
async def client_detail(request: Request, client_id: int):
    conn = get_connection()
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    entries = conn.execute(
        "SELECT * FROM entries WHERE client_id = ? ORDER BY week_number", (client_id,)
    ).fetchall()
    conn.close()
    if not client:
        return HTMLResponse("Client not found", status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="client_detail.html",
        context={"client": client, "entries": entries, "phase_colour": _colour},
    )


@router.get("/clients/{client_id}/edit", response_class=HTMLResponse)
async def edit_client_form(request: Request, client_id: int):
    conn = get_connection()
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    if not client:
        return HTMLResponse("Client not found", status_code=404)
    return templates.TemplateResponse(request=request, name="client_form.html", context={"client": client})


@router.post("/clients/{client_id}/edit")
async def edit_client(
    client_id: int,
    name: str = Form(...),
    goal: Optional[str] = Form(None),
    start_weight: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    contact_email: Optional[str] = Form(None),
    contact_phone: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    sw = float(start_weight) if start_weight else None
    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE clients SET name=?, goal=?, start_weight=?, date_of_birth=?, "
            "contact_email=?, contact_phone=?, notes=? WHERE id=?",
            (name, goal, sw, date_of_birth, contact_email, contact_phone, notes, client_id),
        )
    conn.close()
    return RedirectResponse(f"/clients/{client_id}", status_code=303)


@router.post("/clients/{client_id}/delete")
async def delete_client(client_id: int):
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.close()
    return RedirectResponse("/", status_code=303)
