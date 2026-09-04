"""Dispara estágios do pipeline (via estudio.services.runner) e serve o log ao vivo.

Agora com todos os estágios mecânicos ligados — s2_tts, s3_imagens, s4_legendas
e s5_render — e não só o `imagens-seco` da prova de conceito. Os dois que faltam
no pipeline, `s1_roteiro` e `s6_upload`, seguem proibidos pelo CLAUDE.md até
2-3 vídeos publicados: não há o que ligar aqui até lá.

A tabela ESTAGIOS carrega três coisas além do módulo:

- `custa`: `s3_imagens` sem `--seco` chama a fal.ai e gasta de verdade. A rota
  EXIGE confirmação explícita no corpo do POST. É guarda de servidor de
  propósito — um `curl` errado, um duplo-clique ou um htmx retentando não devem
  conseguir gastar só porque a tela tinha um aviso.
- `tempo`: ordem de grandeza MEDIDA no M2 8 GB (ver CLAUDE.md § Hardware), para
  a tela avisar antes de você clicar e sumir por uma hora e meia.
- `campos`: quais parâmetros o estágio aceita. Só o que está declarado aqui
  chega ao argv; o resto é ignorado em silêncio. Sem isso, cada estágio novo
  viraria mais um `if estagio == ...` na rota.

Os argumentos vão por `create_subprocess_exec` (sem shell), então não existe
injeção de comando. Ainda assim `--modelo` é conferido contra lista fechada:
argv arbitrário não é injeção, mas é jeito fácil de fazer o whisper baixar
2 GB de modelo por engano.
"""
from __future__ import annotations
import sys
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import StreamingResponse

from estudio.services import runner

router = APIRouter()

FASE0 = RAIZ / "fase0"

MODELOS_WHISPER = ("tiny", "base", "small", "medium", "large-v2", "large-v3")


@dataclass(frozen=True)
class Estagio:
    rotulo: str                       # o que a tela mostra no botão
    modulo: str
    args: tuple[str, ...] = ()        # argumentos fixos do estágio
    custa: bool = False               # gasta em API externa -> exige confirmação
    tempo: str = ""                   # ordem de grandeza medida no M2 8 GB
    campos: tuple[str, ...] = ()      # parâmetros aceitos do formulário
    nota: str = ""


# chave = nome no URL. Ordem = ordem em que os estágios rodam de verdade.
ESTAGIOS: dict[str, Estagio] = {
    "narracao": Estagio(
        rotulo="s2_tts — gerar narração por cena",
        modulo="pipeline.s2_tts", tempo="~12 min", campos=("forcar",),
        nota="Kokoro local, offline. Não gasta nada além de CPU.",
    ),
    "imagens-seco": Estagio(
        rotulo="s3_imagens --seco — só montar os prompts",
        modulo="pipeline.s3_imagens", args=("--seco",), tempo="segundos",
        campos=("cena",),
        nota="Grátis. Serve para conferir prompt e seed antes de gastar.",
    ),
    "imagens": Estagio(
        rotulo="s3_imagens — GERAR imagens na fal.ai",
        modulo="pipeline.s3_imagens", custa=True, tempo="~2 min",
        campos=("forcar", "cena"),
        nota="Chama a fal.ai e GASTA. Rode o --seco antes e confira os prompts.",
    ),
    "legendas": Estagio(
        rotulo="s4_legendas — transcrever e alinhar SRT",
        modulo="pipeline.s4_legendas", tempo="~87 min no M2",
        campos=("forcar", "modelo"),
        nota="É o estágio mais lento do pipeline. Whisper large-v3 em CPU roda "
             "a 3,44x realtime.",
    ),
    "thumbnails": Estagio(
        rotulo="s5b_thumbs — gerar as três thumbnails candidatas",
        modulo="pipeline.s5b_thumbs", tempo="segundos", campos=("forcar",),
        nota="Três CENAS diferentes, com o mesmo tratamento de texto. Gera "
             "também uma folha de contato com as três lado a lado — escolher "
             "olhando uma de cada vez é escolher entre coisas que você nunca "
             "viu juntas. Não sobrescreve thumbnail feita à mão sem --forcar.",
    ),
    "render": Estagio(
        rotulo="s5_render — montar o vídeo final",
        modulo="pipeline.s5_render", tempo="~8 min",
        campos=("forcar", "jobs"),
        nota="Precisa das imagens e da narração prontas.",
    ),
    "mixagem-preview": Estagio(
        # --so-mix refaz só build/mix.m4a (segundos) — não re-renderiza o vídeo
        # inteiro. É o que dá o "mixer com preview rápido" sem esperar o render.
        rotulo="s5_render --so-mix — refazer só a mixagem",
        modulo="pipeline.s5_render", args=("--so-mix",), tempo="segundos",
        campos=("preview_inicio", "preview_dur"),
    ),
}


# Sequências: os estágios dependem uns dos outros (o render precisa das imagens
# E do áudio; a legenda precisa do áudio), então rodar na mão significa lembrar
# a ordem. Aqui a ordem está escrita uma vez.
SEQUENCIAS: dict[str, tuple[str, tuple[str, ...], str]] = {
    "mecanica": (
        "produção sem gastar — narração, legendas, render",
        ("narracao", "legendas", "render"),
        "Assume que as imagens já existem. Não chama a fal.ai, não gasta nada.",
    ),
    "completa": (
        "produção completa — inclui GERAR as imagens",
        ("narracao", "imagens", "legendas", "render", "thumbnails"),
        "Inclui o s3_imagens, que GASTA na fal.ai. Rode o --seco antes e "
        "confira os prompts.",
    ),
}


def _checar_projeto(slug: str) -> Path:
    if "/" in slug or "\\" in slug or ".." in slug:
        raise HTTPException(status_code=400, detail="slug inválido")
    d = FASE0 / slug
    if not (d / "plano.json").is_file():
        raise HTTPException(status_code=404, detail=f"projeto '{slug}' não encontrado")
    return d


def _checar_estagio(nome: str) -> Estagio:
    if nome not in ESTAGIOS:
        raise HTTPException(status_code=404, detail=f"estágio '{nome}' desconhecido")
    return ESTAGIOS[nome]


def _montar_argv(e: Estagio, valores: dict) -> list[str]:
    """Traduz o formulário em argv, aceitando só os campos que o estágio declara."""
    argv: list[str] = list(e.args)

    def quer(campo: str):
        return valores.get(campo) if campo in e.campos else None

    if quer("forcar"):
        argv.append("--forcar")

    cena = quer("cena")
    if cena is not None:
        if cena < 1:
            raise HTTPException(status_code=400, detail="cena tem que ser >= 1")
        argv += ["--cena", str(cena)]

    modelo = quer("modelo")
    if modelo:
        if modelo not in MODELOS_WHISPER:
            raise HTTPException(
                status_code=400,
                detail=f"modelo '{modelo}' não é um dos conhecidos: "
                       f"{', '.join(MODELOS_WHISPER)}")
        argv += ["--modelo", modelo]

    jobs = quer("jobs")
    if jobs is not None:
        if not 1 <= jobs <= 32:
            raise HTTPException(status_code=400, detail="jobs tem que estar entre 1 e 32")
        argv += ["--jobs", str(jobs)]

    dur = quer("preview_dur")
    if dur:
        argv += ["--preview-s", str(dur),
                 "--preview-inicio", str(quer("preview_inicio") or 0)]
    return argv


@router.post("/projetos/{slug}/estagios/{estagio}/rodar")
async def rodar(slug: str, estagio: str,
                forcar: bool = Form(False),
                cena: int = Form(None),
                modelo: str = Form(None),
                jobs: int = Form(None),
                preview_inicio: float = Form(None),
                preview_dur: float = Form(None),
                confirmo_custo: str = Form(None)):
    d = _checar_projeto(slug)
    e = _checar_estagio(estagio)

    # Guarda de gasto no servidor. Ver o docstring do módulo: a tela avisando
    # não basta, porque a tela não é o único jeito de chamar esta rota.
    if e.custa and confirmo_custo != "sim":
        raise HTTPException(
            status_code=400,
            detail="este estágio gasta na fal.ai — falta confirmo_custo=sim")

    argv = _montar_argv(e, {
        "forcar": forcar, "cena": cena, "modelo": modelo, "jobs": jobs,
        "preview_inicio": preview_inicio, "preview_dur": preview_dur,
    })
    ok = runner.iniciar(slug, estagio, e.modulo, [str(d), *argv])
    if not ok:
        raise HTTPException(status_code=409,
                            detail="já tem uma execução rodando para este estágio")
    return {"status": "iniciado", "slug": slug, "estagio": estagio, "argv": argv}


@router.post("/projetos/{slug}/sequencias/{nome}/rodar")
async def rodar_sequencia(slug: str, nome: str, confirmo_custo: str = Form(None),
                          forcar: bool = Form(False)):
    d = _checar_projeto(slug)
    if nome not in SEQUENCIAS:
        raise HTTPException(status_code=404, detail=f"sequência '{nome}' desconhecida")
    _, etapas, _ = SEQUENCIAS[nome]

    # A confirmação é exigida se QUALQUER etapa da sequência gastar. O usuário
    # aperta um botão só; a guarda tem que olhar a sequência inteira.
    if any(ESTAGIOS[e].custa for e in etapas) and confirmo_custo != "sim":
        gasta = [e for e in etapas if ESTAGIOS[e].custa]
        raise HTTPException(
            status_code=400,
            detail=f"esta sequência inclui etapa que gasta na fal.ai "
                   f"({', '.join(gasta)}) — falta confirmo_custo=sim")

    passos = []
    for e in etapas:
        est = ESTAGIOS[e]
        argv = _montar_argv(est, {"forcar": forcar})
        passos.append((f"{e} ({est.modulo})", est.modulo, [str(d), *argv]))
    if not runner.iniciar_sequencia(slug, nome, passos):
        raise HTTPException(status_code=409, detail="esta sequência já está rodando")
    return {"status": "iniciado", "slug": slug, "sequencia": nome,
            "passos": [p[0] for p in passos]}


@router.get("/projetos/{slug}/estagios/{estagio}/logs")
async def logs(slug: str, estagio: str):
    _checar_projeto(slug)
    # aceita nome de estágio OU de sequência: o SSE é o mesmo mecanismo
    if estagio not in ESTAGIOS and estagio not in SEQUENCIAS:
        raise HTTPException(status_code=404, detail=f"'{estagio}' desconhecido")
    return StreamingResponse(runner.acompanhar(slug, estagio),
                             media_type="text/event-stream")
