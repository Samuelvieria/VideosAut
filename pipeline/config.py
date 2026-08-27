"""Segredos e configuração de provedores externos.

As chaves ficam em `.env` na raiz do repositório — que está no `.gitignore` e
NUNCA é versionado. Nada aqui imprime valor de chave: os diagnósticos mostram
só o prefixo e o comprimento, o suficiente para conferir que a chave certa foi
carregada sem expor o segredo em log, terminal ou histórico de conversa.
"""
from __future__ import annotations
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENV = RAIZ / ".env"


def carregar() -> dict[str, str]:
    """Lê o .env. Formato CHAVE=valor, uma por linha; # inicia comentário."""
    valores: dict[str, str] = {}
    if ENV.is_file():
        for linha in ENV.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            k, v = linha.split("=", 1)
            valores[k.strip()] = v.strip().strip('"').strip("'")
    valores.update({k: v for k, v in os.environ.items() if k in _CONHECIDAS})
    return valores


_CONHECIDAS = {
    "FAL_KEY":                        "fal.ai — geração de imagem (Z-Image-Turbo)",
    "REPLICATE_API_TOKEN":            "Replicate — alternativa de imagem",
    "GOOGLE_APPLICATION_CREDENTIALS": "Google Cloud TTS — caminho do JSON da conta de serviço",
    "ANTHROPIC_API_KEY":              "Claude API — adaptação do roteiro pt-BR -> inglês",
    "OPENAI_API_KEY":                 "OpenAI — TTS/imagem (não recomendado para pt-BR)",
    "ELEVENLABS_API_KEY":             "ElevenLabs — TTS premium",
    "DASHSCOPE_API_KEY":              "Alibaba Model Studio — Z-Image / Qwen-TTS",
}


def obter(nome: str, obrigatorio: bool = True) -> str | None:
    v = carregar().get(nome)
    if not v and obrigatorio:
        raise SystemExit(
            f"Falta {nome} no .env ({_CONHECIDAS.get(nome, '')}).\n"
            f"  cp .env.example .env   e preencha. O .env não é versionado."
        )
    return v


def _mascara(v: str) -> str:
    if len(v) <= 12:
        return f"{'*' * len(v)} ({len(v)} chars)"
    return f"{v[:6]}…{v[-4:]}  ({len(v)} chars)"


def diagnostico() -> None:
    """Mostra o que está configurado SEM revelar as chaves."""
    vals = carregar()
    print(f"  .env: {'encontrado' if ENV.is_file() else 'AUSENTE — cp .env.example .env'}")
    for k, desc in _CONHECIDAS.items():
        v = vals.get(k)
        if v and k == "GOOGLE_APPLICATION_CREDENTIALS":
            existe = Path(v).is_file()
            print(f"  {k:<32} {'ok' if existe else 'CAMINHO NAO EXISTE'}  {v}")
        elif v:
            print(f"  {k:<32} {_mascara(v)}")
        else:
            print(f"  {k:<32} —  ({desc})")


# Modelo padrão da adaptação de roteiro. Opus 5 é o default do projeto; trocar
# para claude-sonnet-5 corta o custo para ~40% se a qualidade bastar (adaptação
# não é a tarefa mais exigente do pipeline). Decisão de custo é do Samuel.
MODELO_ROTEIRO = "claude-opus-5"


if __name__ == "__main__":
    diagnostico()
