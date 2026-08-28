"""Dispara estágios do pipeline (via estudio.services.runner) e serve o log ao vivo.

Só o estágio 'imagens-seco' existe nesta entrega — é a prova de conceito do
mecanismo de log via SSE (mais barato e rápido possível: monta os prompts e sai,
sem gastar). Os estágios reais (tts/imagens/render/legendas) ficam para a Fase 3
do roteiro de continuação (ver docs/estudio-plano.md ou o plano aprovado).
"""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import StreamingResponse

from estudio.services import runner

router = APIRouter()

FASE0 = RAIZ / "fase0"

# estágio (nome na URL) -> (módulo do pipeline, argumentos extras)
ESTAGIOS: dict[str, tuple[str, list[str]]] = {
    "imagens-seco": ("pipeline.s3_imagens", ["--seco"]),
    # --so-mix refaz só build/mix.m4a (segundos) — não re-renderiza o vídeo
    # inteiro. É o que dá o "mixer com preview rápido" sem esperar o render.
    "mixagem-preview": ("pipeline.s5_render", ["--so-mix"]),
}


def _checar_projeto(slug: str) -> Path:
    if "/" in slug or "\\" in slug or ".." in slug:
        raise HTTPException(status_code=400, detail="slug inválido")
    d = FASE0 / slug
    if not (d / "plano.json").is_file():
        raise HTTPException(status_code=404, detail=f"projeto '{slug}' não encontrado")
    return d


def _checar_estagio(estagio: str) -> tuple[str, list[str]]:
    if estagio not in ESTAGIOS:
        raise HTTPException(status_code=404, detail=f"estágio '{estagio}' desconhecido")
    return ESTAGIOS[estagio]


@router.post("/projetos/{slug}/estagios/{estagio}/rodar")
async def rodar(slug: str, estagio: str,
                 preview_inicio: float = Form(None), preview_dur: float = Form(None)):
    d = _checar_projeto(slug)
    modulo, extra = _checar_estagio(estagio)
    # mixagem-preview aceita trecho custom (ver mixer.html) — o resto dos
    # estágios ignora esses dois campos.
    if estagio == "mixagem-preview" and preview_dur:
        extra = [*extra, "--preview-s", str(preview_dur),
                  "--preview-inicio", str(preview_inicio or 0)]
    ok = runner.iniciar(slug, estagio, modulo, [str(d), *extra])
    if not ok:
        raise HTTPException(status_code=409, detail="já tem uma execução rodando para este estágio")
    return {"status": "iniciado", "slug": slug, "estagio": estagio}


@router.get("/projetos/{slug}/estagios/{estagio}/logs")
async def logs(slug: str, estagio: str):
    _checar_projeto(slug)
    _checar_estagio(estagio)
    return StreamingResponse(runner.acompanhar(slug, estagio), media_type="text/event-stream")
