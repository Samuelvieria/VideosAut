"""Segredos e configuração de provedores externos.

As chaves ficam em `.env` na raiz do repositório — que está no `.gitignore` e
NUNCA é versionado. Nada aqui imprime valor de chave: os diagnósticos mostram
só o prefixo e o comprimento, o suficiente para conferir que a chave certa foi
carregada sem expor o segredo em log, terminal ou histórico de conversa.
"""
from __future__ import annotations
import os
import re
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


_SUSPEITO = ("cd ", "./", "python", "source ", "export ", "setenv ", "git ", "sudo ",
             "curl ", "wget ", "http://", "https://", "brew ", "pip ", "npm ")

# Formato esperado por chave. Pegar o formato errado aqui evita descobrir só na
# primeira chamada de API, com erro de autenticação que não diz o que houve.
_FORMATO = {
    "FAL_KEY":           (r"[0-9a-f-]{36}:[0-9a-f]{32}", "uuid:hex, 69 chars"),
    "ANTHROPIC_API_KEY": (r"sk-ant-[A-Za-z0-9_\-]{20,}", "começa com sk-ant-"),
    "OPENAI_API_KEY":    (r"sk-[A-Za-z0-9_\-]{20,}", "começa com sk-"),
}


def _valida(nome: str, valor: str) -> str:
    """Rejeita o que claramente não é chave.

    O modo anterior lia da área de transferência, e isso falha justamente quando
    o usuário copia o COMANDO de algum lugar para colar no terminal: o clipboard
    passa a ter o comando, e o comando grava a si mesmo. Aconteceu 4 vezes.
    """
    valor = valor.strip()
    if not valor:
        raise SystemExit("nada digitado — nenhuma alteração feita")
    if "\n" in valor or "\r" in valor:
        raise SystemExit("valor tem mais de uma linha; cole só a chave")
    baixo = valor.lower()
    if any(baixo.startswith(x) for x in _SUSPEITO) or " && " in valor:
        raise SystemExit(
            f"isso parece um COMANDO, não uma chave:\n    {valor[:60]}...\n"
            f"  Nada foi gravado. Cole o valor da chave, não a linha de comando.")
    # Colar repetido é o erro mais comum: o prompt oculto não dá retorno visual,
    # então o usuário duplica sem perceber. Aconteceu com 4 repetições.
    metade = len(valor) // 2
    if len(valor) % 2 == 0 and valor[:metade] == valor[metade:]:
        raise SystemExit(
            f"o valor é a mesma coisa repetida 2x ({len(valor)} chars).\n"
            f"  Nada gravado — cole UMA vez só. O prompt não mostra nada, mas registrou.")
    for n in (3, 4):
        if len(valor) % n == 0:
            parte = len(valor) // n
            if len({valor[i*parte:(i+1)*parte] for i in range(n)}) == 1:
                raise SystemExit(
                    f"o valor é a mesma coisa repetida {n}x ({len(valor)} chars).\n"
                    f"  Nada gravado — cole UMA vez só.")

    esperado = _FORMATO.get(nome)
    if esperado and not re.fullmatch(esperado[0], valor):
        raise SystemExit(
            f"não parece uma {nome} válida (esperado: {esperado[1]}).\n"
            f"  Recebi {len(valor)} chars começando com {valor[:8]!r}.\n"
            f"  Nada gravado — cole só o valor da chave, sem comando em volta.")

    if nome == "GOOGLE_APPLICATION_CREDENTIALS":
        if not Path(valor).expanduser().is_file():
            raise SystemExit(f"caminho não existe: {valor}")
        valor = str(Path(valor).expanduser().resolve())
    elif len(valor) < 16:
        raise SystemExit(f"só {len(valor)} caracteres — parece curto demais para uma chave")
    return valor


def definir(nome: str) -> None:
    """Lê a chave por digitação OCULTA e grava no .env.

    getpass lê do terminal sem ecoar: o valor não aparece na tela, não vai para
    o histórico do shell (não é argumento de comando) e não depende do
    clipboard. Colar dentro do prompt funciona normalmente.
    """
    import getpass

    if nome not in _CONHECIDAS:
        raise SystemExit(f"Chave desconhecida: {nome}. Opções: {', '.join(_CONHECIDAS)}")

    print(f"  {nome} — {_CONHECIDAS[nome]}")
    print("  Cole o valor e tecle Enter. Nada aparece na tela; isso é esperado.")
    valor = _valida(nome, getpass.getpass("  > "))

    linhas = ENV.read_text(encoding="utf-8").splitlines() if ENV.is_file() else []
    for i, l in enumerate(linhas):
        if l.strip().startswith(f"{nome}="):
            linhas[i] = f"{nome}={valor}"
            break
    else:
        linhas.append(f"{nome}={valor}")

    ENV.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    ENV.chmod(0o600)
    print(f"  gravado: {_mascara(valor)}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == "set":
        definir(sys.argv[2])
    else:
        diagnostico()
