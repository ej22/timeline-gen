from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import date, timedelta
from math import ceil
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
    start_date: Optional[str] = Form(None),
    goal_date: Optional[str] = Form(None),
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
            "INSERT INTO clients (name, goal, start_date, goal_date, start_weight, date_of_birth, contact_email, contact_phone, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, goal, start_date, goal_date, sw, date_of_birth, contact_email, contact_phone, notes),
        )
        client_id = cur.lastrowid

        if start_date and goal_date:
            sd = date.fromisoformat(start_date)
            gd = date.fromisoformat(goal_date)
            total_days = (gd - sd).days
            if total_days > 0:
                num_weeks = ceil(total_days / 7)
                entries = []
                for i in range(num_weeks):
                    week_date = sd + timedelta(weeks=i)
                    entries.append((client_id, i + 1, week_date.isoformat(), "", None, "", None, "", "", ""))
                conn.executemany(
                    "INSERT INTO entries (client_id, week_number, date, phase, calories, cardio, steps, training_specifics, goals_expectations, notes) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    entries,
                )
    conn.close()
    return RedirectResponse(f"/clients/{client_id}", status_code=303)


@router.get("/clients/{client_id}", response_class=HTMLResponse)
async def client_detail(request: Request, client_id: int, warning: Optional[str] = None):
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
        context={"client": client, "entries": entries, "phase_colour": _colour, "warning": warning},
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
    start_date: Optional[str] = Form(None),
    goal_date: Optional[str] = Form(None),
    start_weight: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    contact_email: Optional[str] = Form(None),
    contact_phone: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    sw = float(start_weight) if start_weight else None
    conn = get_connection()
    warning = None
    with conn:
        conn.execute(
            "UPDATE clients SET name=?, goal=?, start_date=?, goal_date=?, start_weight=?, date_of_birth=?, "
            "contact_email=?, contact_phone=?, notes=? WHERE id=?",
            (name, goal, start_date, goal_date, sw, date_of_birth, contact_email, contact_phone, notes, client_id),
        )

        if start_date and goal_date:
            sd = date.fromisoformat(start_date)
            gd = date.fromisoformat(goal_date)
            total_days = (gd - sd).days
            if total_days > 0:
                new_week_count = ceil(total_days / 7)
                existing_count = conn.execute(
                    "SELECT COUNT(*) FROM entries WHERE client_id = ?", (client_id,)
                ).fetchone()[0]

                if new_week_count > existing_count:
                    last = conn.execute(
                        "SELECT week_number, date FROM entries WHERE client_id = ? ORDER BY week_number DESC LIMIT 1",
                        (client_id,)
                    ).fetchone()

                    new_entries = []
                    if last and last["date"]:
                        next_week_num = last["week_number"] + 1
                        last_date = date.fromisoformat(last["date"])
                        for i in range(new_week_count - existing_count):
                            week_date = last_date + timedelta(weeks=(i + 1))
                            new_entries.append((client_id, next_week_num + i, week_date.isoformat(), "", None, "", None, "", "", ""))
                    elif existing_count == 0:
                        for i in range(new_week_count):
                            week_date = sd + timedelta(weeks=i)
                            new_entries.append((client_id, i + 1, week_date.isoformat(), "", None, "", None, "", "", ""))
                    else:
                        next_week_num = (last["week_number"] if last else existing_count) + 1
                        for i in range(new_week_count - existing_count):
                            week_date = sd + timedelta(weeks=(next_week_num + i - 1))
                            new_entries.append((client_id, next_week_num + i, week_date.isoformat(), "", None, "", None, "", "", ""))

                    if new_entries:
                        conn.executemany(
                            "INSERT INTO entries (client_id, week_number, date, phase, calories, cardio, steps, training_specifics, goals_expectations, notes) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            new_entries,
                        )

                elif new_week_count < existing_count:
                    warning = "date_shortened"

    conn.close()
    url = f"/clients/{client_id}"
    if warning == "date_shortened":
        url += "?warning=date_shortened"
    return RedirectResponse(url, status_code=303)


@router.post("/clients/{client_id}/delete")
async def delete_client(client_id: int):
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.close()
    return RedirectResponse("/", status_code=303)
