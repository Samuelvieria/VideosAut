"""Listagem somente-leitura dos vídeos existentes em fase0/ + preview de mídia.

Reusa pipeline.comum.carregar_plano em vez de reimplementar leitura de plano.json —
mesma fonte de verdade que os estágios já usam.
"""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from estudio.routers.pipeline_run import ESTAGIOS, MODELOS_WHISPER
from pipeline.comum import carregar_plano

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

FASE0 = RAIZ / "fase0"


def _nome_seguro(nome: str) -> str:
    if "/" in nome or "\\" in nome or ".." in nome:
        raise HTTPException(status_code=400, detail="nome de arquivo inválido")
    return nome


def _projeto_dir(slug: str) -> Path:
    slug = _nome_seguro(slug)
    d = FASE0 / slug
    if not (d / "plano.json").is_file():
        raise HTTPException(status_code=404, detail=f"projeto '{slug}' não encontrado")
    return d


def _listar_projetos() -> list[dict]:
    projetos = []
    if not FASE0.is_dir():
        return projetos
    for d in sorted(FASE0.iterdir()):
        if not (d / "plano.json").is_file():
            continue
        try:
            plano = carregar_plano(d)
        except Exception:
            continue
        imagens_dir = d / "imagens"
        projetos.append({
            "slug": d.name,
            "titulo": plano.get("titulo", d.name),
            "duracao_alvo_s": plano.get("duracao_alvo_s"),
            "num_cenas": len(plano.get("cenas", [])),
            "tem_video": (d / "final.mp4").is_file(),
            "tem_legendas": (d / "legendas.pt-BR.srt").is_file(),
            "tem_imagens": imagens_dir.is_dir() and any(imagens_dir.glob("cena_*.png")),
        })
    return projetos


@router.get("/", response_class=HTMLResponse)
async def raiz():
    return RedirectResponse(url="/projetos")


@router.get("/projetos", response_class=HTMLResponse)
async def listar(request: Request):
    return templates.TemplateResponse(request, "projetos/lista.html", {
        "projetos": _listar_projetos(),
    })


@router.get("/projetos/{slug}", response_class=HTMLResponse)
async def detalhe(request: Request, slug: str):
    d = _projeto_dir(slug)
    plano = carregar_plano(d)
    imagens = sorted(p.name for p in (d / "imagens").glob("cena_*.png")) if (d / "imagens").is_dir() else []
    audios = sorted(p.name for p in (d / "audio").glob("cena_*.wav")) if (d / "audio").is_dir() else []
    return templates.TemplateResponse(request, "projetos/detalhe.html", {
        "slug": slug, "plano": plano, "imagens": imagens, "audios": audios,
        "estagios": ESTAGIOS, "modelos_whisper": MODELOS_WHISPER,
        "tem_video": (d / "final.mp4").is_file(),
        "tem_legendas": (d / "legendas.pt-BR.srt").is_file(),
    })


@router.get("/projetos/{slug}/arquivos/imagens/{nome}")
async def arquivo_imagem(slug: str, nome: str):
    d = _projeto_dir(slug)
    caminho = d / "imagens" / _nome_seguro(nome)
    if not caminho.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(caminho)


@router.get("/projetos/{slug}/arquivos/audio/{nome}")
async def arquivo_audio(slug: str, nome: str):
    d = _projeto_dir(slug)
    caminho = d / "audio" / _nome_seguro(nome)
    if not caminho.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(caminho, media_type="audio/wav")


@router.get("/projetos/{slug}/video")
async def video(slug: str):
    d = _projeto_dir(slug)
    caminho = d / "final.mp4"
    if not caminho.is_file():
        raise HTTPException(status_code=404, detail="final.mp4 ainda não existe")
    return FileResponse(caminho, media_type="video/mp4")


@router.get("/projetos/{slug}/legendas")
async def legendas(slug: str):
    d = _projeto_dir(slug)
    caminho = d / "legendas.pt-BR.srt"
    if not caminho.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(caminho, media_type="text/plain; charset=utf-8")
