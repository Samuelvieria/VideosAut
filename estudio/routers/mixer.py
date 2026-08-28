"""Mixer de áudio por projeto — edita o bloco `mixagem` do plano.json e dispara
um preview rápido (`s5_render --so-mix`, só o áudio, sem re-renderizar o vídeo).

Existe porque ninguém aqui consegue OUVIR o resultado enquanto ajusta os
parâmetros de ffmpeg às cegas — é mais rápido e mais confiável o Samuel ajustar
e tocar o preview ele mesmo do que descrever "mais baixo"/"mais reverb" de volta
e pra frente.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from pipeline.comum import carregar_plano
from pipeline.s5_render import MIXAGEM_PADRAO

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

FASE0 = RAIZ / "fase0"

CAMPOS = list(MIXAGEM_PADRAO.keys())


def _projeto_dir(slug: str) -> Path:
    if "/" in slug or "\\" in slug or ".." in slug:
        raise HTTPException(status_code=400, detail="slug inválido")
    d = FASE0 / slug
    if not (d / "plano.json").is_file():
        raise HTTPException(status_code=404, detail=f"projeto '{slug}' não encontrado")
    return d


@router.get("/projetos/{slug}/mixagem", response_class=HTMLResponse)
async def form(request: Request, slug: str):
    d = _projeto_dir(slug)
    plano = carregar_plano(d)
    valores = {**MIXAGEM_PADRAO, **plano.get("mixagem", {})}
    return templates.TemplateResponse(request, "projetos/mixagem.html", {
        "slug": slug, "valores": valores,
        "tem_preview": (d / "build" / "mix.m4a").is_file(),
        "tem_preview_curto": (d / "build" / "mix_preview.m4a").is_file(),
        "cenas": _cenas_com_offset(d, plano),
    })


@router.post("/projetos/{slug}/mixagem")
async def salvar(
    slug: str,
    voz_ganho: float = Form(...),
    voz_reverb: float = Form(...),
    voz_deesser: float = Form(...),
    ambiente_ganho: float = Form(...),
    ambiente_reverb: float = Form(...),
    ambiente_lowpass_hz: int = Form(...),
    duck_threshold: float = Form(...),
    duck_ratio: float = Form(...),
    duck_attack_ms: int = Form(...),
    duck_release_ms: int = Form(...),
):
    d = _projeto_dir(slug)
    caminho = d / "plano.json"
    plano = json.loads(caminho.read_text(encoding="utf-8"))
    plano.setdefault("mixagem", {})
    plano["mixagem"].update({
        "voz_ganho": voz_ganho,
        "voz_reverb": voz_reverb,
        "voz_deesser": voz_deesser,
        "ambiente_ganho": ambiente_ganho,
        "ambiente_reverb": ambiente_reverb,
        "ambiente_lowpass_hz": ambiente_lowpass_hz,
        "duck_threshold": duck_threshold,
        "duck_ratio": duck_ratio,
        "duck_attack_ms": duck_attack_ms,
        "duck_release_ms": duck_release_ms,
    })
    caminho.write_text(json.dumps(plano, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return RedirectResponse(url=f"/projetos/{slug}/mixagem", status_code=303)


@router.get("/projetos/{slug}/arquivos/mix")
async def arquivo_mix(slug: str):
    d = _projeto_dir(slug)
    caminho = d / "build" / "mix.m4a"
    if not caminho.is_file():
        raise HTTPException(status_code=404, detail="ainda não tem preview gerado")
    return FileResponse(caminho, media_type="audio/mp4")


@router.get("/projetos/{slug}/arquivos/mix-preview")
async def arquivo_mix_preview(slug: str):
    d = _projeto_dir(slug)
    caminho = d / "build" / "mix_preview.m4a"
    if not caminho.is_file():
        raise HTTPException(status_code=404, detail="ainda não tem preview curto gerado")
    return FileResponse(caminho, media_type="audio/mp4")


def _cenas_com_offset(d: Path, plano: dict) -> list[dict]:
    """(n, titulo, offset_s) de cada cena, a partir de duracoes_render.json se
    existir (durações reais já renderizadas) ou dur_s do plano como fallback."""
    reais = {}
    dr = d / "duracoes_render.json"
    if dr.is_file():
        reais = {int(k): v for k, v in json.loads(dr.read_text(encoding="utf-8"))["cenas"].items()}
    offset = 0.0
    saida = []
    for c in plano["cenas"]:
        dur = reais.get(c["n"], c.get("dur_s", 60))
        saida.append({"n": c["n"], "titulo": c["titulo"], "offset": round(offset, 1)})
        offset += dur
    return saida
