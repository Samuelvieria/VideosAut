"""Leitura/escrita de estudio/dados/personas.json — sem banco, mesmo estilo de
arquivo-plano usado pelo resto do repo (plano.json, estilo.yaml).
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent.parent / "dados" / "personas.json"

VOZ_VAZIA = {"engine": None, "voice": None, "speed": None, "nota": ""}


def _agora() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _carregar_bruto() -> dict:
    if not ARQUIVO.is_file():
        return {"personas": []}
    return json.loads(ARQUIVO.read_text(encoding="utf-8"))


def _salvar_bruto(dados: dict) -> None:
    ARQUIVO.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def listar() -> list[dict]:
    return _carregar_bruto()["personas"]


def obter(persona_id: str) -> dict | None:
    for p in listar():
        if p["id"] == persona_id:
            return p
    return None


def _slugify(nome: str) -> str:
    base = "".join(c.lower() if c.isalnum() else "-" for c in nome).strip("-")
    while "--" in base:
        base = base.replace("--", "-")
    return base or "persona"


def criar(nome: str, descricao: str, voz_pt_engine: str, voz_pt_voice: str,
          voz_pt_speed: float, voz_pt_nota: str = "") -> dict:
    dados = _carregar_bruto()
    slug = _slugify(nome)
    existentes = {p["id"] for p in dados["personas"]}
    pid, n = slug, 2
    while pid in existentes:
        pid, n = f"{slug}-{n}", n + 1

    persona = {
        "id": pid,
        "nome": nome,
        "descricao": descricao,
        "vozes": {
            "pt": {"engine": voz_pt_engine or "kokoro", "voice": voz_pt_voice,
                   "speed": voz_pt_speed, "nota": voz_pt_nota},
            "en": dict(VOZ_VAZIA, nota="TBD — nenhum engine de voz em inglês escolhido ainda."),
        },
        "criado_em": _agora(),
        "origem_video": None,
    }
    dados["personas"].append(persona)
    _salvar_bruto(dados)
    return persona


def atualizar(persona_id: str, nome: str, descricao: str, voz_pt_engine: str,
              voz_pt_voice: str, voz_pt_speed: float, voz_pt_nota: str = "") -> dict | None:
    dados = _carregar_bruto()
    for p in dados["personas"]:
        if p["id"] == persona_id:
            p["nome"] = nome
            p["descricao"] = descricao
            p["vozes"]["pt"] = {"engine": voz_pt_engine or "kokoro", "voice": voz_pt_voice,
                                 "speed": voz_pt_speed, "nota": voz_pt_nota}
            _salvar_bruto(dados)
            return p
    return None
