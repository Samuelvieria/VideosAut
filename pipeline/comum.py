"""Infraestrutura compartilhada dos estágios do pipeline.

Regra de ouro (ver CLAUDE.md): estes scripts são DETERMINÍSTICOS e IDEMPOTENTES.
Rodar duas vezes com a mesma entrada produz o mesmo resultado e não refaz trabalho.
Nenhum LLM roda aqui dentro.
"""
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# ffmpeg-full é keg-only no Homebrew e traz librubberband; o padrão serve para o resto.
FFMPEG = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
FFPROBE = os.environ.get("FFPROBE") or shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"


def log(msg: str) -> None:
    print(f"  {msg}", flush=True)


def erro(msg: str) -> "NoReturn":
    print(f"ERRO: {msg}", file=sys.stderr)
    raise SystemExit(1)


def projeto(caminho: str | os.PathLike) -> Path:
    """Diretório de um vídeo (ex.: fase0/video-02). Precisa conter plano.json."""
    p = Path(caminho).resolve()
    if not (p / "plano.json").is_file():
        erro(f"{p} não tem plano.json — não parece um projeto de vídeo")
    return p


def carregar_plano(proj: Path) -> dict:
    return json.loads((proj / "plano.json").read_text(encoding="utf-8"))


def ffmpeg(args: list[str], desc: str = "") -> None:
    """Roda ffmpeg abortando no primeiro erro, com stderr preservado."""
    cmd = [FFMPEG, "-hide_banner", "-v", "error", "-y", *args]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        erro(f"ffmpeg falhou{' em ' + desc if desc else ''}:\n{r.stderr.strip()}\ncmd: {' '.join(cmd)}")


def duracao(caminho: Path) -> float:
    r = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(caminho)],
        capture_output=True, text=True)
    if r.returncode != 0:
        erro(f"ffprobe falhou em {caminho}: {r.stderr.strip()}")
    return float(r.stdout.strip())


def _hash(caminhos: list[Path], extra: str = "") -> str:
    h = hashlib.sha256(extra.encode())
    for c in sorted(caminhos):
        h.update(c.name.encode())
        h.update(str(c.stat().st_mtime_ns).encode())
        h.update(str(c.stat().st_size).encode())
    return h.hexdigest()[:16]


def atualizado(saida: Path, entradas: list[Path], extra: str = "") -> bool:
    """True se `saida` já reflete estas entradas. É o que dá idempotência.

    Guarda o hash das entradas ao lado da saída. Mudou qualquer entrada ou o
    parâmetro `extra` (config), refaz; senão pula.
    """
    marca = saida.with_suffix(saida.suffix + ".stamp")
    if not saida.exists() or not marca.exists():
        return False
    return marca.read_text().strip() == _hash(entradas, extra)


def marcar(saida: Path, entradas: list[Path], extra: str = "") -> None:
    saida.with_suffix(saida.suffix + ".stamp").write_text(_hash(entradas, extra))


def escapar_concat(p: Path) -> str:
    """Path para lista do concat demuxer. Aspa simples precisa de escape.

    Padrão emprestado do MoneyPrinterTurbo (MIT) — app/services/video.py.
    """
    return str(p.resolve()).replace("\\", "/").replace("'", "'\\''")


def lista_concat(destino: Path, arquivos: list[Path]) -> Path:
    destino.write_text("".join(f"file '{escapar_concat(a)}'\n" for a in arquivos))
    return destino
