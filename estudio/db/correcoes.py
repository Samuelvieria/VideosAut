"""Anotações de correção por projeto — estudio/dados/correcoes/<slug>.json.

Fica fora do plano.json de propósito: isso é histórico de revisão do humano,
não input que os estágios do pipeline precisam ler.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent / "dados" / "correcoes"


def _agora() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _arquivo(slug: str) -> Path:
    return DIR / f"{slug}.json"


def listar(slug: str) -> list[dict]:
    caminho = _arquivo(slug)
    if not caminho.is_file():
        return []
    return json.loads(caminho.read_text(encoding="utf-8"))["itens"]


def _salvar(slug: str, itens: list[dict]) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    _arquivo(slug).write_text(json.dumps({"itens": itens}, indent=2, ensure_ascii=False) + "\n",
                               encoding="utf-8")


def adicionar(slug: str, texto: str, cena: int | None) -> dict:
    itens = listar(slug)
    novo_id = str(max((int(i["id"]) for i in itens), default=0) + 1)
    item = {"id": novo_id, "cena": cena, "texto": texto.strip(),
            "estado": "aberta", "criado_em": _agora(), "resolvida_em": None}
    itens.append(item)
    _salvar(slug, itens)
    return item


def resolver(slug: str, item_id: str) -> None:
    itens = listar(slug)
    for i in itens:
        if i["id"] == item_id:
            i["estado"] = "resolvida"
            i["resolvida_em"] = _agora()
    _salvar(slug, itens)


def reabrir(slug: str, item_id: str) -> None:
    itens = listar(slug)
    for i in itens:
        if i["id"] == item_id:
            i["estado"] = "aberta"
            i["resolvida_em"] = None
    _salvar(slug, itens)
