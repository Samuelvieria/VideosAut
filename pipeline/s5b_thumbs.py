"""Gera as três thumbnails candidatas de um projeto.

    python -m pipeline.s5b_thumbs fase0/video-02 [--seco] [--forcar]

Três, não uma, porque escolher thumbnail é decisão de olho e olho precisa
comparar. A receita não foi inventada aqui: está registrada no bloco
`thumbnails` do plano.json do video-02, que foi o primeiro feito à mão.

O que ela diz, e por quê:

- **Três CENAS diferentes, não três tratamentos da mesma.** A variante que
  ganhou (`thumb_B`) ganhou por ser outra cena, não outro corte.
- **Sombra suave, nunca contorno duro.** Contorno grosso lê como conteúdo
  agitado, que é o oposto do nicho. O `drawtext` não borra sombra, então a
  suavidade vem de alfa baixo e deslocamento pequeno.
- **Fonte serifada (Georgia) em creme.** Mesma lógica: serifa lê como calmo.
- **Evitar a cena cujo assunto o modelo erra.** A `thumb_A` do video-02 foi
  descartada porque a baleia saía jubarte em vez de cachalote — e a thumbnail
  é o ativo mais visível para carregar um erro de anatomia.

Sem shell em lugar nenhum: o texto e os caminhos vão como lista de argumentos
para o `ffmpeg`. A versão feita à mão tinha passado por linha de comando e o
zsh comeu o parâmetro em `$G:text=`, porque `:t` é modificador de expansão do
zsh — cinco tentativas perdidas nisso.
"""
from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline import comum
from pipeline.comum import atualizado, carregar_plano, erro, ffmpeg, log, marcar, projeto

# O ffmpeg padrão do Homebrew NÃO traz `drawtext` (falta libfreetype). O
# ffmpeg-full traz, e é o mesmo que o s5_render já precisa por causa do
# librubberband. Resolvido aqui e só para este processo: trocar
# `comum.FFMPEG` globalmente mudaria o binário de todos os estágios, e nenhum
# outro precisa disso.
_CANDIDATOS = ["/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg",
               "/usr/local/opt/ffmpeg-full/bin/ffmpeg"]


def _ffmpeg_com_drawtext() -> str:
    for cam in [comum.FFMPEG, *_CANDIDATOS, shutil.which("ffmpeg") or ""]:
        if not cam or not Path(cam).is_file():
            continue
        r = subprocess.run([cam, "-hide_banner", "-filters"],
                           capture_output=True, text=True)
        if r.returncode == 0 and " drawtext " in r.stdout:
            return cam
    erro("nenhum ffmpeg com o filtro `drawtext` encontrado. O padrão do "
         "Homebrew não traz libfreetype; instale com `brew install ffmpeg-full`.")

LARG, ALT = 1280, 720           # o tamanho que o YouTube recomenda para thumbnail
FONTE = "/System/Library/Fonts/Supplemental/Georgia.ttf"

CREME = "0xF2E8D5"
SOMBRA = "0x000000@0.45"        # alfa baixo: sombra suave, não contorno
SOMBRA_DX = SOMBRA_DY = 4
TAM_FONTE = 66
MARGEM = 64

# Onde o texto assenta. Ponto fixo não serve: a região vazia muda de cena para
# cena — visto na primeira leva, em que o canto inferior esquerdo caía em cima
# da multidão na variante C. Cada variante pode trazer `posicao` no plano.json.
POSICOES = {
    "inf-esq": (f"{MARGEM}", f"h-th-{MARGEM}"),
    "inf-dir": (f"w-tw-{MARGEM}", f"h-th-{MARGEM}"),
    "sup-esq": (f"{MARGEM}", f"{MARGEM}"),
    "sup-dir": (f"w-tw-{MARGEM}", f"{MARGEM}"),
    "centro":  ("(w-tw)/2", "(h-th)/2"),
}
POSICAO_PADRAO = "inf-esq"


def _escapar(t: str) -> str:
    """Escapa para o parser de filtro do ffmpeg. Ordem importa: a barra primeiro."""
    for de, para in (("\\", "\\\\"), (":", "\\:"), ("'", "\\'"),
                     ("%", "\\%"), ("[", "\\["), ("]", "\\]"), (",", "\\,")):
        t = t.replace(de, para)
    return t


def _quebrar(texto: str, por_linha: int = 22) -> str:
    """Quebra em linhas curtas. Thumbnail é lida em miniatura: linha longa some."""
    linhas, atual = [], ""
    for p in texto.split():
        if atual and len(atual) + 1 + len(p) > por_linha:
            linhas.append(atual); atual = p
        else:
            atual = f"{atual} {p}".strip()
    if atual:
        linhas.append(atual)
    return "\n".join(linhas)


def _escolher_cenas(plano: dict) -> list[tuple[str, int, str]]:
    """(id, número da cena, posição do texto). Do plano se houver; senão, espalhadas.

    Espalhar em vez de pegar as três primeiras: a abertura costuma ser a cena
    mais vazia, e três variantes da mesma parte da história não são três
    opções de verdade.
    """
    bloco = plano.get("thumbnails") or {}
    variantes = bloco.get("variantes") or []
    escolhidas = [(v.get("id", chr(65 + i)), v["cena"],
                   v.get("posicao", POSICAO_PADRAO))
                  for i, v in enumerate(variantes) if v.get("cena")]
    if escolhidas:
        for _, _, pos in escolhidas:
            if pos not in POSICOES:
                erro(f"posicao '{pos}' desconhecida; use uma de {', '.join(POSICOES)}")
        return escolhidas
    n = len(plano.get("cenas") or [])
    if n < 3:
        erro(f"o projeto tem {n} cena(s); a thumbnail precisa de pelo menos 3")
    return [("A", max(1, round(n * 0.15)), POSICAO_PADRAO),
            ("B", max(2, round(n * 0.45)), POSICAO_PADRAO),
            ("C", max(3, round(n * 0.75)), POSICAO_PADRAO)]


def _texto_da_thumb(plano: dict) -> str:
    """O texto da thumbnail, do plano ou derivado do título.

    Deriva pegando o que vem ANTES do pipe: pelo padrão de título de
    docs/mercado.md, é ali que mora o termo que tem busca.
    """
    bloco = plano.get("thumbnails") or {}
    if bloco.get("texto"):
        return str(bloco["texto"])
    titulo = (plano.get("titulo") or "").split("|")[0].strip()
    return titulo


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera as três thumbnails candidatas.")
    ap.add_argument("projeto")
    ap.add_argument("--texto", default=None, help="sobrescreve o texto da thumbnail")
    ap.add_argument("--sem-texto", action="store_true", help="gera as três limpas")
    ap.add_argument("--forcar", action="store_true")
    ap.add_argument("--seco", action="store_true", help="mostra o plano e sai")
    a = ap.parse_args()

    proj = projeto(a.projeto)
    plano = carregar_plano(proj)
    imagens = proj / "imagens"
    if not imagens.is_dir():
        erro(f"{imagens} não existe — rode o s3_imagens antes")

    dest = proj / "thumbnails"
    dest.mkdir(exist_ok=True)
    texto = "" if a.sem_texto else (a.texto if a.texto is not None else _texto_da_thumb(plano))
    escolhidas = _escolher_cenas(plano)

    if not Path(FONTE).is_file() and texto:
        erro(f"fonte não encontrada: {FONTE}")
    if not a.seco:
        comum.FFMPEG = _ffmpeg_com_drawtext()
        log(f"ffmpeg: {comum.FFMPEG}")

    titulos = {c["n"]: c.get("titulo", "") for c in plano.get("cenas", [])}
    log(f"texto: {texto or '(sem texto)'}")

    for vid, n, pos in escolhidas:
        origem = imagens / f"cena_{n:02d}.png"
        alvo = dest / f"thumb_{vid}.png"
        if a.seco:
            marca = "ok" if origem.is_file() else "FALTA"
            log(f"{vid}: cena {n:02d} [{marca}] texto em {pos} · {titulos.get(n, '')}")
            continue
        if not origem.is_file():
            erro(f"{origem} não existe — gere as imagens antes (s3_imagens)")

        cfg = f"{LARG}x{ALT};{FONTE};{TAM_FONTE};{CREME};{pos};{texto}"
        if not a.forcar and atualizado(alvo, [origem], cfg):
            log(f"{vid}: cena {n:02d}  já gerada")
            continue
        # Thumbnail que existe SEM marca não foi feita por este estágio — é
        # trabalho manual, e a do video-02 está publicada. Não sobrescrever
        # em silêncio.
        marca = alvo.with_suffix(alvo.suffix + ".stamp")
        if alvo.is_file() and not marca.exists() and not a.forcar:
            erro(f"{alvo.name} já existe e não foi gerada por este estágio "
                 f"(sem marca ao lado). Pode ser feita à mão — a thumb_B do "
                 f"video-02 está publicada. Use --forcar para sobrescrever, "
                 f"depois de salvar uma cópia.")

        vf = [f"scale={LARG}:{ALT}:flags=neighbor"]
        if texto:
            vf.append(
                "drawtext="
                f"fontfile={FONTE}"
                f":text='{_escapar(_quebrar(texto))}'"
                f":fontcolor={CREME}"
                f":fontsize={TAM_FONTE}"
                f":line_spacing=12"
                f":x={POSICOES[pos][0]}"
                f":y={POSICOES[pos][1]}"
                f":borderw=0"                      # NUNCA contorno: ver docstring
                f":shadowcolor={SOMBRA}"
                f":shadowx={SOMBRA_DX}:shadowy={SOMBRA_DY}")

        ffmpeg(["-i", str(origem), "-vf", ",".join(vf),
                "-frames:v", "1", "-update", "1", str(alvo)],
               desc=f"thumbnail {vid}")
        marcar(alvo, [origem], cfg)
        log(f"{vid}: cena {n:02d}  {alvo.stat().st_size/1024:5.0f} KB  {titulos.get(n, '')}")

    if a.seco:
        return

    # Folha de contato com as três lado a lado. É a lição do docs/verificacao.md
    # nº5: inspecionar o LOTE, não a amostra. Escolher thumbnail olhando uma de
    # cada vez é como escolher entre três coisas que você nunca viu juntas.
    feitas = [dest / f"thumb_{v}.png" for v, _, _ in escolhidas]
    if all(f.is_file() for f in feitas):
        args = []
        for f in feitas:
            args += ["-i", str(f)]
        args += ["-filter_complex", f"hstack=inputs={len(feitas)},scale=1920:-1",
                 "-frames:v", "1", "-update", "1", str(dest / "contato.png")]
        ffmpeg(args, desc="folha de contato")
        log(f"folha de contato: {dest / 'contato.png'}")


if __name__ == "__main__":
    main()
