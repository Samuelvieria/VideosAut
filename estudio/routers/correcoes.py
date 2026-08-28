"""Aba de correções: anotações do que precisa de ajuste num vídeo, por cena ou
geral. Não dispara nada sozinho — é um lugar pra registrar o que foi pedido e
o que já foi resolvido, em vez de depender só do histórico de chat.
"""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from estudio.db import correcoes as db_correcoes

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

FASE0 = RAIZ / "fase0"


def _checar_projeto(slug: str) -> None:
    if "/" in slug or "\\" in slug or ".." in slug:
        raise HTTPException(status_code=400, detail="slug inválido")
    if not (FASE0 / slug / "plano.json").is_file():
        raise HTTPException(status_code=404, detail=f"projeto '{slug}' não encontrado")


@router.get("/projetos/{slug}/correcoes", response_class=HTMLResponse)
async def listar(request: Request, slug: str):
    _checar_projeto(slug)
    itens = db_correcoes.listar(slug)
    abertas = [i for i in itens if i["estado"] == "aberta"]
    resolvidas = [i for i in itens if i["estado"] == "resolvida"]
    return templates.TemplateResponse(request, "projetos/correcoes.html", {
        "slug": slug, "abertas": abertas, "resolvidas": resolvidas,
    })


@router.post("/projetos/{slug}/correcoes")
async def adicionar(slug: str, texto: str = Form(...), cena: str = Form("")):
    _checar_projeto(slug)
    if not texto.strip():
        raise HTTPException(status_code=400, detail="texto vazio")
    cena_n = int(cena) if cena.strip().isdigit() else None
    db_correcoes.adicionar(slug, texto, cena_n)
    return RedirectResponse(url=f"/projetos/{slug}/correcoes", status_code=303)


@router.post("/projetos/{slug}/correcoes/{item_id}/resolver")
async def resolver(slug: str, item_id: str):
    _checar_projeto(slug)
    db_correcoes.resolver(slug, item_id)
    return RedirectResponse(url=f"/projetos/{slug}/correcoes", status_code=303)


@router.post("/projetos/{slug}/correcoes/{item_id}/reabrir")
async def reabrir(slug: str, item_id: str):
    _checar_projeto(slug)
    db_correcoes.reabrir(slug, item_id)
    return RedirectResponse(url=f"/projetos/{slug}/correcoes", status_code=303)
