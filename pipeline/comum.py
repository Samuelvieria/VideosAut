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

# No Windows o stdout nasce em cp1252, que não codifica IPA nem símbolo fora do
# Latin-1 — e aí um LOG derruba o estágio inteiro. Aconteceu em 04/09/2026: o
# s2_tts morreu com UnicodeEncodeError ao anunciar a troca de vogal final
# (`ɐ`, U+0250) ANTES de sintetizar a primeira cena. Reconfigurar aqui vale
# para todos os estágios, porque todos passam por este módulo.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):     # fluxo redirecionado/não-reconfigurável
        pass


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


_VERSAO_MARCA = "v2"   # muda quando o algoritmo de hash muda; ver nota abaixo
_BLOCO = 65536


def _hash(caminhos: list[Path], extra: str = "") -> str:
    """Hash das entradas por CONTEÚDO, não por mtime.

    Era mtime_ns + tamanho até 03/09/2026. O problema não é teórico: `git
    checkout`, `git pull` e troca de branch reescrevem o mtime de arquivo
    versionado sem tocar no conteúdo. Medido no merge de 03/09 — o
    `roteiro.md` do video-02 ficou byte a byte idêntico e o stamp das 20
    cenas de TTS furou do mesmo jeito, o que mandaria refazer 12 min de
    narração à toa. Em `s4_legendas` o mesmo furo custa os 87 min de whisper.

    Custo medido de hashear conteúdo aqui: 0,17 s para 111 MB (39 arquivos,
    os WAVs de narração + os 20 PNGs). Irrelevante perto do que evita.

    Padrão emprestado de affaan-m/ecc (MIT), skill content-hash-cache-pattern.
    """
    h = hashlib.sha256(f"{_VERSAO_MARCA}\0{extra}".encode())
    for c in sorted(caminhos):
        h.update(c.name.encode())
        h.update(b"\0")
        with open(c, "rb") as f:
            while bloco := f.read(_BLOCO):
                h.update(bloco)
        h.update(b"\0")
    return h.hexdigest()[:16]


def atualizado(saida: Path, entradas: list[Path], extra: str = "") -> bool:
    """True se `saida` já reflete estas entradas. É o que dá idempotência.

    Guarda o hash das entradas ao lado da saída. Mudou qualquer entrada ou o
    parâmetro `extra` (config), refaz; senão pula.

    Nota sobre a troca de mtime para conteúdo em 03/09/2026: o `_VERSAO_MARCA`
    entra no hash, então todo stamp gravado no esquema antigo passa a não
    bater e o estágio refaz uma vez. Isso é de propósito e sai de graça — o
    único projeto com artefato em disco é o video-02, que está publicado e
    não precisa rodar de novo. Não vale construir um re-stamper: ele
    precisaria saber as entradas de cada estágio, que só o próprio estágio
    conhece.
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
