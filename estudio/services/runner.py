"""Dispara estágios do pipeline como subprocesso e guarda o log em memória.

Subprocesso, não import direto: `pipeline.comum.erro()` faz `raise SystemExit(1)` —
importar `main()` no processo do servidor deixaria um erro de estágio derrubar o
servidor inteiro. Subprocesso isola isso como só um código de saída não-zero, e
garante reuso literal do mesmo comando (`python -m pipeline.sN_xxx ...`) que já
roda por linha de comando.

Sem fila/assinante: asyncio é cooperativo de thread única, então a task que lê o
subprocesso e o gerador da rota SSE (`acompanhar`) só trocam de contexto em pontos
de `await` — um cursor por índice na mesma lista é suficiente, sem condição de
corrida, sem precisar de asyncio.Queue.
"""
from __future__ import annotations
import asyncio, sys
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent


@dataclass
class Execucao:
    linhas: list[str] = field(default_factory=list)
    finalizado: bool = False
    codigo: int | None = None


_execucoes: dict[tuple[str, str], Execucao] = {}


def em_andamento(slug: str, estagio: str) -> bool:
    ex = _execucoes.get((slug, estagio))
    return bool(ex and not ex.finalizado)


def estado(slug: str, estagio: str) -> Execucao | None:
    return _execucoes.get((slug, estagio))


async def _rodar(chave: tuple[str, str], modulo: str, argv: list[str]) -> None:
    ex = _execucoes[chave]
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-u", "-m", modulo, *argv,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            cwd=str(RAIZ),
        )
        assert proc.stdout is not None
        while True:
            bruta = await proc.stdout.readline()
            if not bruta:
                break
            ex.linhas.append(bruta.decode("utf-8", errors="replace").rstrip("\n"))
        codigo = await proc.wait()
    except Exception as e:  # noqa: BLE001 — reportar qualquer falha de lançamento no próprio log
        ex.linhas.append(f"[estudio] erro ao rodar {modulo}: {e}")
        codigo = -1
    ex.finalizado = True
    ex.codigo = codigo


def iniciar(slug: str, estagio: str, modulo: str, argv: list[str]) -> bool:
    """Dispara em segundo plano. Devolve False se essa (slug, estagio) já está rodando."""
    chave = (slug, estagio)
    if em_andamento(slug, estagio):
        return False
    _execucoes[chave] = Execucao()
    asyncio.create_task(_rodar(chave, modulo, argv))
    return True


async def acompanhar(slug: str, estagio: str):
    """Gerador SSE: reenvia o que já rodou (buffer) e depois transmite ao vivo."""
    chave = (slug, estagio)
    ex = _execucoes.get(chave)
    if ex is None:
        yield "event: done\ndata: -1\n\n"
        return
    i = 0
    while True:
        while i < len(ex.linhas):
            linha = ex.linhas[i].replace("\r", "")
            yield f"data: {linha}\n\n"
            i += 1
        if ex.finalizado:
            yield f"event: done\ndata: {ex.codigo}\n\n"
            return
        await asyncio.sleep(0.2)
