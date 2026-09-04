"""Leitura/escrita de estudio/dados/personas.json — sem banco, mesmo estilo de
arquivo-plano usado pelo resto do repo (plano.json, estilo.yaml).

A persona carrega VOZ e ESTÉTICA. A estética entrou em 04/09/2026 porque o
visual morava só em `fase0/video-NN/estilo.yaml`, copiado de projeto em
projeto — e foi assim que o video-03 nasceu com o cue de prompt que já tinha
sido corrigido no video-02. Persona é MOLDE: o estúdio gera o projeto a partir
dela e o `pipeline/` continua lendo só o `plano.json`, sem nunca importar deste
pacote (ver a regra em estudio/main.py).

`_validar_estetica` é a parte que importa. As duas regressões que tivemos
passaram por documentação que ninguém releu; aqui elas viram recusa.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent.parent / "dados" / "personas.json"

VOZ_VAZIA = {"engine": None, "voice": None, "speed": None, "nota": ""}

ESTETICA_VAZIA = {
    "estilo_base": "", "prompt_negativo": "", "paleta": [], "luz": "",
    "resolucao": [1280, 720], "nota": "",
}

# Cada regra abaixo custou uma rodada de erro real. Ver
# .claude/skills/qualidade-producao-video/references/prompt-imagem.md
# Cada regra abaixo custou uma rodada de erro real. Ver
# .claude/skills/qualidade-producao-video/references/prompt-imagem.md
#
# Revisado adversarialmente pelo gemini-3.1-pro em 04/09/2026; ele achou quatro
# buracos que estão fechados abaixo (variantes de negação, "gaming art" sem a
# palavra "background", hora do dia sem o prefixo "at", e o "no" do português
# batendo com a negação inglesa).
_NEG_ALVOS = (r"text|watermark|signature|logo|letter|word|title|caption|"
              r"typography|ui|hud|border|frame|人|character")

_CUES_PROIBIDOS = [
    (r"\bgam(e|ing)\b[\w\s]{0,20}\bart\b|\btitle\s+screen\b|\bmain\s+menu\b|\bgame\s+ui\b",
     "linguagem de arte de jogo convida tela de título — foi o que escreveu "
     "'Moby-Dolk' dentro da imagem no video-02"),

    (r"\b(poster|magazine|flyer)\b|\b(book|album)\s+cover\b",
     "linguagem de capa/cartaz também convida tipografia na imagem"),

    # Hora do dia: com ou sem o "at" na frente, e as expressões que não usam
    # preposição nenhuma. Vale para o estilo_base, que se aplica a TODAS as
    # cenas — a cena individual pode e deve dizer a hora dela.
    (r"\b(at|in\s+the|during\s+the|late)\s+"
     r"(night|dawn|dusk|noon|sunset|sunrise|midnight|morning|afternoon|evening|twilight)\b"
     r"|\b(daytime|nighttime|golden\s+hour|blue\s+hour)\b"
     r"|\b(morning|evening|afternoon|midday)\s+(light|sun|sky)\b",
     "hora do dia não pode ser fixada no estilo_base: ela vale para o vídeo "
     "inteiro e contradiz as cenas que se passam em outro momento (o video-03 "
     "tinha 'at night' e três cenas eram de dia ou amanhecer)"),

    # Negação. O "no" solto NÃO entra: em português é preposição comum
    # ("desenho no papel") e recusaria estilo legítimo. Só marca quando o alvo
    # da negação é uma das coisas que a gente de fato tenta negar.
    (rf"\b(no|without|free\s+of|devoid\s+of|zero|nada\s+de|sem)\s+\w{{0,12}}\s*({_NEG_ALVOS})"
     rf"|\bnot\s+\w{{0,12}}\s*({_NEG_ALVOS})"
     rf"|\bavoid\s+\w{{0,12}}\s*({_NEG_ALVOS})",
     "negação em prompt POSITIVO pede o que nega — modelo de difusão não "
     "processa negação. O que não se quer vai em prompt_negativo"),
]


class EsteticaInvalida(ValueError):
    """Estética recusada por conter um cue que já causou regressão."""


def _validar_resolucao(res) -> None:
    """MEDIDO 02/09/2026: a fal.ai não honra dimensão abaixo de 512px num eixo —
    ela empurra para 512 sem avisar e devolve outra proporção, que o s5_render
    então corta em silêncio. E pixel art exige escala inteira até 1920x1080."""
    if not (isinstance(res, (list, tuple)) and len(res) == 2):
        raise EsteticaInvalida("resolucao tem que ser [largura, altura]")
    l, a = res
    if min(l, a) < 512:
        raise EsteticaInvalida(
            f"{l}x{a}: a fal.ai não entrega eixo abaixo de 512px — ela empurra "
            f"para 512 e devolve outra proporção, sem avisar")
    if abs(l / a - 16 / 9) > 0.01:
        raise EsteticaInvalida(f"{l}x{a} não é 16:9 (razão {l/a:.3f})")

    # O s5_render NÃO escala a fonte direto para 1920x1080: ele escala por um
    # fator INTEIRO (PAN_ESCALA) e depois recorta uma janela de 1920x1080 que
    # desliza dentro do resultado. A sobra é a margem do pan. Então o que
    # precisa valer é: existe k inteiro com l*k >= 1920 e a*k >= 1080, e a
    # margem que sobra tem que ser > 0, senão não há para onde deslizar.
    k = max(-(-1920 // l), -(-1080 // a))       # teto da divisão
    margem_x, margem_y = l * k - 1920, a * k - 1080
    if margem_x <= 0 or margem_y <= 0:
        raise EsteticaInvalida(
            f"{l}x{a}: em escala inteira x{k} vira {l*k}x{a*k}, que não deixa "
            f"margem para o pan (sobra {margem_x}x{margem_y}px). Escolha uma "
            f"fonte maior — 1280x720 dá 640x360 de margem")


def _validar_estetica(est: dict) -> dict:
    """Recusa estética com cue conhecidamente ruim. Levanta EsteticaInvalida."""
    _validar_resolucao(est.get("resolucao") or [1280, 720])
    base = (est.get("estilo_base") or "").strip()
    if not base:
        return est
    problemas = [motivo for padrao, motivo in _CUES_PROIBIDOS
                 if re.search(padrao, base, re.I)]
    if problemas:
        raise EsteticaInvalida(
            "estilo_base recusado:\n- " + "\n- ".join(problemas))
    return est


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
          voz_pt_speed: float, voz_pt_nota: str = "",
          estetica: dict | None = None) -> dict:
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
        "estetica": _validar_estetica({**ESTETICA_VAZIA, **(estetica or {})}),
        "criado_em": _agora(),
        "origem_video": None,
    }
    dados["personas"].append(persona)
    _salvar_bruto(dados)
    return persona


def atualizar(persona_id: str, nome: str, descricao: str, voz_pt_engine: str,
              voz_pt_voice: str, voz_pt_speed: float, voz_pt_nota: str = "",
              estetica: dict | None = None) -> dict | None:
    dados = _carregar_bruto()
    for p in dados["personas"]:
        if p["id"] == persona_id:
            p["nome"] = nome
            p["descricao"] = descricao
            p["vozes"]["pt"] = {"engine": voz_pt_engine or "kokoro", "voice": voz_pt_voice,
                                 "speed": voz_pt_speed, "nota": voz_pt_nota}
            if estetica is not None:
                p["estetica"] = _validar_estetica(
                    {**ESTETICA_VAZIA, **p.get("estetica", {}), **estetica})
            _salvar_bruto(dados)
            return p
    return None
