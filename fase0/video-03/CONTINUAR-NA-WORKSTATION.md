# video-03 — como terminar na máquina com GPU

Escrito em 04/09/2026. O video-03 está a **três comandos** de ficar pronto.
O gargalo é máquina, não decisão: no M2 de 8 GB o caminho que falta leva cerca
de **duas horas**; com GPU deve cair para uns 20 minutos.

Setup da máquina: [SETUP.md](../../SETUP.md). Este documento é só o que muda
para **este** vídeo.

---

## Regra número um

**NÃO rode `s3_imagens`.** As 39 imagens estão aprovadas — palavras do Samuel em
04/09: *"gostei muito das imagens, não é pra mexer nelas"* — e custaram
R$ 1,97. Elas vêm **versionadas no git**, com os `.stamp` junto, exatamente para
que a outra máquina não precise (nem possa, por acidente) regerar.

Como a marca de idempotência é hash de **conteúdo** desde 03/09, ela vale em
qualquer máquina. Se por algum motivo você rodar `s3_imagens`, ele vai dizer
"já gerada" em todas as 39 e não gastar nada. O perigo real é só o `--forcar`.

O mesmo vale para as três thumbnails em `thumbnails/`.

---

## O que já está pronto e versionado

| | |
|---|---|
| roteiro | 38 cenas narradas + cauda · 6.375 palavras |
| plano | 39 cenas, prompts, ambiente por cena, voz |
| imagens | **39, aprovadas** — no git |
| thumbnails | 3 candidatas + folha de contato — no git |
| metadados | título, 20 tags, descrição em `metadados.md` |

## O que falta gerar (tudo local e gratuito)

| | o que é | M2 8 GB | com GPU |
|---|---|---|---|
| `s2_tts` | narração, 38 cenas | ~35 min | ~5 min |
| `s4_legendas` | alinhamento e SRT | ~30 min | ~3 min |
| `s5_render` | vídeo final | ~60 min | ~10 min |

Nada disso está no git de propósito: áudio e vídeo são grandes e **reproduzíveis
de graça**. As imagens não são — por isso a exceção.

---

## Os três comandos

```bash
python -m pipeline.preflight   fase0/video-03    # confere antes; sai 1 se houver erro
python -m pipeline.s2_tts      fase0/video-03
python -m pipeline.s4_legendas fase0/video-03    # com GPU pode usar large-v3
python -m pipeline.s5_render   fase0/video-03
```

Ou tudo de uma vez pelo estúdio, na sequência `mecanica`, que já roda o
preflight primeiro e **para no primeiro erro**:

```bash
python -m uvicorn estudio.main:app --port 8000
# abrir http://localhost:8000/projetos/video-03 e usar "rodar sequência"
```

### Sobre o modelo do whisper

No M2 usei `--modelo small` porque `large-v3` custaria 189 minutos. **Com GPU,
tire o `--modelo`**: o perfil detecta e usa `large-v3`, que dá limites de
palavra mais precisos. Só o *timing* do whisper sobrevive — o texto exibido vem
sempre do roteiro — então a diferença é de alinhamento, não de conteúdo.

---

## O que esperar no fim

| | valor conferido no M2 |
|---|---|
| duração | ~73 min (a configuração B encurtou 3% dos 75,9 anteriores) |
| formato | 1920×1080 · h264 · 24 fps · AAC estéreo 48 kHz |
| loudness | perto de −14,7 LUFS · LRA ~4,2 |

Se sair muito longe disso, algo mudou — confira o bloco `voz` do `plano.json`
antes de investigar qualquer outra coisa.

### A configuração de voz, e por que ela é essa

```
voice pm_santa · speed 0.75
pausa_respiro_s   0.45
pausa_paragrafo_s 0.30
pausa_frase_s     1.2
vogal_final_pt    true
```

Cada número foi **julgado de ouvido** pelo Samuel, não medido por mim, e em
dois casos a medição perdeu:

- **speed 0.75** — a minha medição dizia que abaixo de 0.85 o acento tonal se
  perde. Ele ouviu 0.75 e 0.85 lado a lado e escolheu 0.75. A medição foi feita
  em palavra isolada, sem pausa e sem a correção de vogal; com as compensações,
  o resultado perceptual é outro.
- **pausa de frase 1,2s** — 1,8s foi rejeitado às cegas por "matar a fluidez".
- **respiro e parágrafo no padrão** — eu os havia triplicado para comprar
  duração, sem pedir julgamento. Ele notou que "a voz do video 2 estava melhor",
  e era isso.

O `preflight` avisa que 0.75 está abaixo do piso medido. **É aviso, não erro**,
e está correto assim: se alguém mexer numa das compensações, precisa ouvir de
novo.

---

## Depois do render

O upload continua **manual**. O `s6_upload.py` está proibido pelo CLAUDE.md até
2–3 vídeos publicados, e este é o segundo — publicando, a regra destrava.

Tudo para colar está em [metadados.md](metadados.md). O que não pode esquecer:

- Visibilidade **privada** até revisar
- **Anúncios no meio: DESATIVAR** — o padrão do YouTube liga sozinho acima de
  8 minutos, e é a coisa mais fácil de esquecer desta lista
- **Conteúdo alterado ou sintético: ATIVADO**
- Enviar `legendas.pt-BR.srt` como legenda **soft**, nunca queimada
- Escolher a thumbnail em `thumbnails/contato.png` — as três lado a lado
