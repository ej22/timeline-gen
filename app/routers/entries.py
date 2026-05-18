from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.database import get_connection
from app.models import PHASES, PHASE_COLOURS

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _colour(phase: str) -> str:
    return PHASE_COLOURS.get(phase, "#333333")


@router.get("/clients/{client_id}/entries/new", response_class=HTMLResponse)
async def new_entry_form(request: Request, client_id: int):
    conn = get_connection()
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    next_week = conn.execute(
        "SELECT COALESCE(MAX(week_number), 0) + 1 FROM entries WHERE client_id = ?", (client_id,)
    ).fetchone()[0]
    conn.close()
    if not client:
        return HTMLResponse("Client not found", status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="entry_form.html",
        context={"client": client, "entry": None, "phases": PHASES, "next_week": next_week},
    )


@router.post("/clients/{client_id}/entries/new")
async def create_entry(
    client_id: int,
    week_number: int = Form(...),
    date: Optional[str] = Form(None),
    phase: Optional[str] = Form(None),
    phase_custom: Optional[str] = Form(None),
    calories: Optional[str] = Form(None),
    cardio: Optional[str] = Form(None),
    steps: Optional[str] = Form(None),
    training_specifics: Optional[str] = Form(None),
    goals_expectations: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    if phase == "__custom__":
        phase = phase_custom or "Custom"
    cal = int(calories) if calories else None
    st = int(steps) if steps else None
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO entries (client_id, week_number, date, phase, calories, cardio, steps, "
            "training_specifics, goals_expectations, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (client_id, week_number, date, phase, cal, cardio, st, training_specifics, goals_expectations, notes),
        )
    conn.close()
    return RedirectResponse(f"/clients/{client_id}", status_code=303)


@router.get("/clients/{client_id}/entries/{entry_id}/edit", response_class=HTMLResponse)
async def edit_entry_form(request: Request, client_id: int, entry_id: int):
    conn = get_connection()
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    entry = conn.execute("SELECT * FROM entries WHERE id = ? AND client_id = ?", (entry_id, client_id)).fetchone()
    conn.close()
    if not client or not entry:
        return HTMLResponse("Not found", status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="entry_form.html",
        context={"client": client, "entry": entry, "phases": PHASES, "next_week": None},
    )


@router.post("/clients/{client_id}/entries/{entry_id}/edit")
async def edit_entry(
    client_id: int,
    entry_id: int,
    week_number: int = Form(...),
    date: Optional[str] = Form(None),
    phase: Optional[str] = Form(None),
    phase_custom: Optional[str] = Form(None),
    calories: Optional[str] = Form(None),
    cardio: Optional[str] = Form(None),
    steps: Optional[str] = Form(None),
    training_specifics: Optional[str] = Form(None),
    goals_expectations: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    if phase == "__custom__":
        phase = phase_custom or "Custom"
    cal = int(calories) if calories else None
    st = int(steps) if steps else None
    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE entries SET week_number=?, date=?, phase=?, calories=?, cardio=?, steps=?, "
            "training_specifics=?, goals_expectations=?, notes=? WHERE id=? AND client_id=?",
            (week_number, date, phase, cal, cardio, st, training_specifics, goals_expectations, notes, entry_id, client_id),
        )
    conn.close()
    return RedirectResponse(f"/clients/{client_id}", status_code=303)


@router.post("/clients/{client_id}/entries/{entry_id}/delete")
async def delete_entry(client_id: int, entry_id: int):
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM entries WHERE id = ? AND client_id = ?", (entry_id, client_id))
    conn.close()
    return RedirectResponse(f"/clients/{client_id}", status_code=303)


@router.get("/clients/{client_id}/print", response_class=HTMLResponse)
async def print_view(request: Request, client_id: int):
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
        name="print_view.html",
        context={"client": client, "entries": entries, "phase_colour": _colour},
    )
