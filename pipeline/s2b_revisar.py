"""Monta uma página local para ouvir a narração cena a cena, com o texto ao lado.

    python -m pipeline.s2b_revisar fase0/video-03
    open fase0/video-03/audio/revisar.html

Existe porque "a ênfase nas sílabas está errada" é a informação certa dita no
lugar impossível de agir: sem saber QUAL cena e QUAL frase, não dá para
diagnosticar. Três medições automáticas falharam em achar o defeito
(taxa de erro do whisper por velocidade, energia por sílaba, varredura de regra
de tonicidade) — e falharam porque nenhuma delas mede prosódia. O ouvido mede.

A página é HTML local, sem servidor: os `<audio>` apontam para os `.wav` na
mesma pasta. Cada frase tem número, então dá para dizer "cena 7, frase 3" e
isso vira uma coordenada exata no roteiro.

Nada aqui é enviado para lugar nenhum, e a página não é publicada.
"""
from __future__ import annotations
import argparse
import html
import re
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.comum import carregar_plano, erro, log, projeto
from pipeline.s2_tts import blocos

CSS = """
:root{--bg:#0d1117;--card:#1a212d;--borda:#2b3a4a;--txt:#dde3ea;--fraco:#8a97a8;
      --ambar:#e8a54b;--verde:#5fb98c}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);
     font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--borda);
       padding:1rem 1.5rem;z-index:9}
h1{margin:0 0 .3rem;font-size:1.1rem}
.meta{color:var(--fraco);font-size:.85rem}
main{max-width:1100px;margin:0 auto;padding:1.5rem}
.cena{background:var(--card);border:1px solid var(--borda);border-radius:8px;
      padding:1rem 1.2rem;margin-bottom:1.1rem}
.cab{display:flex;align-items:center;gap:.8rem;flex-wrap:wrap;margin-bottom:.6rem}
.n{background:var(--borda);color:var(--txt);border-radius:5px;padding:.1rem .5rem;
   font-variant-numeric:tabular-nums;font-weight:600}
.tit{font-weight:600}
.dur{color:var(--fraco);font-size:.85rem;margin-left:auto;font-variant-numeric:tabular-nums}
audio{width:100%;margin:.4rem 0 .7rem;filter:invert(.92) hue-rotate(180deg)}
.frases{margin:0;padding:0;list-style:none}
.frases li{display:flex;gap:.7rem;padding:.15rem 0;border-radius:4px}
.frases li:hover{background:#ffffff0d}
.fn{color:var(--fraco);font-size:.78rem;min-width:2.2rem;text-align:right;
    font-variant-numeric:tabular-nums;padding-top:.15rem;user-select:none}
.aviso{background:#e8a54b1a;border:1px solid var(--ambar);color:var(--ambar);
       border-radius:8px;padding:.9rem 1.1rem;margin-bottom:1.3rem;font-size:.9rem}
.falta{opacity:.5}
"""

JS = """
// Marca a frase clicada, para virar coordenada exata na conversa.
document.addEventListener('click', e => {
  const li = e.target.closest('.frases li');
  if (!li) return;
  const cena = li.closest('.cena').dataset.n;
  const n = li.querySelector('.fn').textContent.trim();
  navigator.clipboard?.writeText(`cena ${cena}, frase ${n}: ${li.querySelector('span:last-child').textContent.trim()}`);
  li.style.background = '#5fb98c33';
  setTimeout(() => li.style.background = '', 700);
});
"""


def _frases(corpo: str) -> list[str]:
    p = " ".join(corpo.split())
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+", p) if f.strip()]


def _dur(w: Path) -> float:
    try:
        with wave.open(str(w)) as f:
            return f.getnframes() / f.getframerate()
    except Exception:
        return 0.0


def main() -> None:
    ap = argparse.ArgumentParser(description="Página local para ouvir e apontar.")
    ap.add_argument("projeto")
    a = ap.parse_args()

    proj = projeto(a.projeto)
    plano = carregar_plano(proj)
    audio = proj / "audio"
    if not audio.is_dir():
        erro(f"{audio} não existe — rode o s2_tts antes")

    cenas = blocos(proj / "roteiro.md")
    voz = plano.get("voz", {})
    feitas = tot = 0.0
    partes = []
    for n, titulo, corpo in cenas:
        w = audio / f"cena_{n:02d}.wav"
        d = _dur(w) if w.is_file() else 0.0
        tot += d
        feitas += 1 if w.is_file() else 0
        player = (f'<audio controls preload="none" src="cena_{n:02d}.wav"></audio>'
                  if w.is_file() else
                  '<p class="dur">— ainda não gerada</p>')
        itens = "\n".join(
            f'<li><span class="fn">{i}</span><span>{html.escape(f)}</span></li>'
            for i, f in enumerate(_frases(corpo), 1))
        partes.append(f"""<section class="cena{'' if w.is_file() else ' falta'}" data-n="{n}">
  <div class="cab"><span class="n">{n:02d}</span>
    <span class="tit">{html.escape(titulo)}</span>
    <span class="dur">{d/60:.0f}min{d%60:02.0f} · {len(corpo.split())} palavras</span></div>
  {player}
  <ul class="frases">{itens}</ul>
</section>""")

    saida = audio / "revisar.html"
    saida.write_text(f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revisar narração — {html.escape(plano.get('titulo', ''))}</title>
<style>{CSS}</style></head><body>
<header>
  <h1>{html.escape(plano.get('titulo', ''))}</h1>
  <div class="meta">voz {html.escape(str(voz.get('voice')))} · speed {voz.get('speed')}
    · {int(feitas)} de {len(cenas)} cenas · {tot/60:.0f} min de narração</div>
</header>
<main>
  <div class="aviso"><strong>Como usar:</strong> ouça e, quando algo soar errado,
  <strong>clique na frase</strong> — ela é copiada como "cena N, frase M" e é só
  colar na conversa. Isso vira coordenada exata no roteiro, e aí dá para
  diagnosticar de verdade. Ouça no fone, à noite, no volume de dormir.</div>
  {''.join(partes)}
</main>
<script>{JS}</script></body></html>""", encoding="utf-8")
    log(f"{saida}  ({int(feitas)}/{len(cenas)} cenas, {tot/60:.0f} min)")


if __name__ == "__main__":
    main()
