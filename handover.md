# Handover — Timeline Generator

## Project Overview
A fitness coaching client timeline tracker. FastAPI + SQLite + Jinja2 templates in a single Docker container (`timeline-generator`). Dark-themed, server-side rendered. Coaches can manage clients, add weekly entries with phase colour coding, and export/print timelines as PDFs. Accessible at `http://localhost:8888`.

## Steps Completed
- [x] handover.md created
- [x] git repo initialised, .gitignore created
- [x] project directory structure scaffolded
- [x] Dockerfile + docker-compose.yml written
- [x] requirements.txt written
- [x] database.py — SQLite init, table creation on startup
- [x] models.py — Pydantic models, phase list, phase colour map
- [x] routers/clients.py — all client CRUD routes
- [x] routers/entries.py — all entry CRUD + print routes
- [x] All Jinja2 templates (base, index, client_detail, client_form, entry_form, print_view)
- [x] static/style.css — dark theme, phase colours, responsive
- [x] static/app.js — custom phase dropdown logic
- [x] main.py — wired together
- [x] Built and started container successfully
- [x] All routes tested (200/303 responses confirmed)
- [x] SQLite DB persists at ./data/timeline.db on host
- [x] **start_date / goal_date** added to clients table (with safe ALTER TABLE migration for existing DBs)
- [x] Client form updated with start/goal date fields (required on create, optional on edit)
- [x] Auto-generate weekly entries on client creation based on date range
- [x] Edit client: extend date range → appends new weeks; shorten → warning banner, no deletion
- [x] Client detail: profile bar shows dates; timeline-progress counter; empty weeks show as muted dashed cards with "Plan" button
- [x] Print view: dates shown in header; `/print?hide_empty=true` filters unplanned weeks
- [x] JS: week count hint + goal-date-after-start validation on client form

## What Went Right
- Docker build clean first try
- All routes functional
- SQLite volume mapping works
- Phase colour system implemented correctly

## What Went Wrong
1. **Starlette 1.0.0 TemplateResponse API change** — the old `TemplateResponse(name, {"request": request, ...})` call pattern broke with `TypeError: unhashable type: 'dict'` due to a cache key bug in the new version.

## How Issues Were Fixed
1. Updated all `TemplateResponse` calls to the new Starlette 1.0.0 keyword-argument signature: `TemplateResponse(request=request, name="...", context={...})` — `request` is no longer part of the context dict.

## Current State
- Container running at http://localhost:8888
- Full CRUD for clients and entries working
- Timeline view with phase colour coding working
- Print/PDF view working (with optional hide_empty filter)
- Dark theme applied
- Custom phase dropdown working (JS)
- DB persists on host at ./data/timeline.db
- Start/goal date fields on clients with auto-generated weekly entries

- [x] **Copy week to multiple weeks** — "Copy to…" button on filled entry cards opens a copy form showing source week data and checkboxes for all other weeks. Submitting copies phase/calories/cardio/steps/training_specifics/goals_expectations/notes to selected targets while preserving each target's week_number and date. JS helpers: Select All Empty, Select All toggle, submit guard. New route: GET/POST `/clients/{client_id}/entries/{entry_id}/copy`. New template: `copy_entry.html`.

## Next Steps
- None — all features implemented and tested
- Run `docker compose up --build` to start fresh on any machine
