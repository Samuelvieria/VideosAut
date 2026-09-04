"""CRUD de personas — nome, descrição, voz por idioma e ESTÉTICA.

A estética entrou em 04/09/2026. A persona virou o molde a partir do qual um
projeto novo nasce, para o visual parar de ser copiado de `estilo.yaml` em
`estilo.yaml` — foi assim que o video-03 herdou um cue de prompt que já tinha
sido corrigido no video-02.

Cue conhecidamente ruim é RECUSADO na gravação (`db.personas._validar_estetica`),
com o motivo na tela. Documentação não impediu a regressão; recusa impede.
"""
from __future__ import annotations
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from estudio.db import personas as db_personas
from estudio.db.personas import EsteticaInvalida

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def _estetica_do_form(estilo_base: str, prompt_negativo: str, paleta: str,
                      luz: str, res_l: int, res_a: int, nota: str) -> dict:
    return {
        "estilo_base": estilo_base.strip(),
        "prompt_negativo": prompt_negativo.strip(),
        "paleta": [c.strip() for c in paleta.split(",") if c.strip()],
        "luz": luz.strip(),
        "resolucao": [res_l, res_a],
        "nota": nota.strip(),
    }


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
async def criar(request: Request, nome: str = Form(...), descricao: str = Form(""),
                 voz_pt_voice: str = Form(...), voz_pt_speed: float = Form(0.80),
                 voz_pt_nota: str = Form(""),
                 estilo_base: str = Form(""), prompt_negativo: str = Form(""),
                 paleta: str = Form(""), luz: str = Form(""),
                 res_l: int = Form(1280), res_a: int = Form(720),
                 estetica_nota: str = Form("")):
    est = _estetica_do_form(estilo_base, prompt_negativo, paleta, luz, res_l, res_a, estetica_nota)
    try:
        db_personas.criar(nome, descricao, "kokoro", voz_pt_voice, voz_pt_speed,
                          voz_pt_nota, estetica=est)
    except EsteticaInvalida as e:
        return templates.TemplateResponse(request, "personas/form.html", {
            "persona": None, "acao": "/personas", "erro": str(e),
        }, status_code=400)
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
async def atualizar(request: Request, persona_id: str, nome: str = Form(...),
                     descricao: str = Form(""), voz_pt_voice: str = Form(...),
                     voz_pt_speed: float = Form(0.80), voz_pt_nota: str = Form(""),
                     estilo_base: str = Form(""), prompt_negativo: str = Form(""),
                     paleta: str = Form(""), luz: str = Form(""),
                     res_l: int = Form(1280), res_a: int = Form(720),
                     estetica_nota: str = Form("")):
    est = _estetica_do_form(estilo_base, prompt_negativo, paleta, luz, res_l, res_a, estetica_nota)
    try:
        db_personas.atualizar(persona_id, nome, descricao, "kokoro", voz_pt_voice,
                              voz_pt_speed, voz_pt_nota, estetica=est)
    except EsteticaInvalida as e:
        return templates.TemplateResponse(request, "personas/form.html", {
            "persona": db_personas.obter(persona_id),
            "acao": f"/personas/{persona_id}", "erro": str(e),
        }, status_code=400)
    return RedirectResponse(url="/personas", status_code=303)
