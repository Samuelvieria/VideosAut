"""Estúdio — interface web local para o pipeline do canal.

Rodar (a partir da raiz do repo, com o venv ativo):

    python -m uvicorn estudio.main:app --reload --port 8000

Depois abrir http://localhost:8000/projetos

Regra de separação: este pacote PODE importar de `pipeline/` (reusa
`pipeline.comum`, `pipeline.config`). `pipeline/` NUNCA importa de `estudio/` —
os estágios continuam rodáveis sozinhos por linha de comando, sem saber que essa
interface existe. Ver estudio/README.md.
"""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from estudio.routers import correcoes, mixer, personas, pipeline_run, projetos

app = FastAPI(title="Estúdio — Canal de Sono Automatizado")

app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).resolve().parent / "static")),
    name="static",
)

app.include_router(projetos.router)
app.include_router(personas.router)
app.include_router(pipeline_run.router)
app.include_router(mixer.router)
app.include_router(correcoes.router)
