"""CRUD simples de personas (nome, descrição, voz por idioma)."""
from __future__ import annotations
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from estudio.db import personas as db_personas

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/personas", response_class=HTMLResponse)
async def listar(request: Request):
    return templates.TemplateResponse(request, "personas/lista.html", {
        "personas": db_personas.listar(),
    })


@router.get("/personas/novo", response_class=HTMLResponse)
async def novo_form(request: Request):
    return templates.TemplateResponse(request, "personas/form.html", {
        "persona": None, "acao": "/personas",
    })


@router.post("/personas")
async def criar(nome: str = Form(...), descricao: str = Form(""),
                 voz_pt_voice: str = Form(...), voz_pt_speed: float = Form(0.80),
                 voz_pt_nota: str = Form("")):
    db_personas.criar(nome, descricao, "kokoro", voz_pt_voice, voz_pt_speed, voz_pt_nota)
    return RedirectResponse(url="/personas", status_code=303)


@router.get("/personas/{persona_id}/editar", response_class=HTMLResponse)
async def editar_form(request: Request, persona_id: str):
    persona = db_personas.obter(persona_id)
    if persona is None:
        return RedirectResponse(url="/personas", status_code=303)
    return templates.TemplateResponse(request, "personas/form.html", {
        "persona": persona, "acao": f"/personas/{persona_id}",
    })


@router.post("/personas/{persona_id}")
async def atualizar(persona_id: str, nome: str = Form(...), descricao: str = Form(""),
                     voz_pt_voice: str = Form(...), voz_pt_speed: float = Form(0.80),
                     voz_pt_nota: str = Form("")):
    db_personas.atualizar(persona_id, nome, descricao, "kokoro", voz_pt_voice, voz_pt_speed, voz_pt_nota)
    return RedirectResponse(url="/personas", status_code=303)
