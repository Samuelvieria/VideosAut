# Ritmo de narração e velocidade de TTS — referência completa

Carregado sob demanda pela skill `qualidade-producao-video`.

## Ritmo de narração e velocidade de TTS (`pipeline/s2_tts.py`)

**WPM de indústria (ACX/audiolivro: 150-160 palavras/min) é medido em
INGLÊS e não atravessa pra português.** Português tem mais sílabas por
palavra (~2,3-2,5 contra ~1,4 do inglês) — copiar o número em pt-BR sai
rápido demais. Não existe benchmark de indústria de locução pt-BR
equivalente ao da ACX; os únicos dados encontrados são estudos
fonoaudiológicos de fala espontânea (90-126 wpm, metodologias divergentes
entre si). Fator de conversão usado (estimativa, não medição): `wpm_ptBR ≈
wpm_inglês × 0,60-0,70`.
- **Correção ao cálculo de roteiro:** 30 min a ~85 wpm bruto (não 110-130,
  que era calibrado em inglês) dá **~2.550 palavras**, não 3.600. Escrever
  3.600 palavras em português pra 30 min de vídeo sai a ritmo ~120 wpm —
  rápido demais pro formato.
- **Alvos pra história de dormir em pt-BR:** WPM bruto 80-95 · WPM
  articulado (só o tempo com fala, sem contar silêncio) 115-130 ·
  orçamento de pausa 25-35% da linha do tempo · 3,2-4,0 sílabas/s
  articuladas.

**Velocidade percebida tem dois componentes independentes — pra sono,
mexer só no segundo:**
| Componente | O que é | Onde mexer |
|---|---|---|
| Taxa de articulação | Sílabas/s enquanto há som | `speed` do Kokoro |
| Orçamento de pausa | % da linha do tempo em silêncio | `PAUSA_RESPIRO`/`PAUSA_PARAGRAFO`/pontuação do roteiro |

**Não usar `speed` baixo (multiplicador global) como mecanismo principal de
lentidão.** `speed<1.0` no Kokoro estica TUDO por igual — vogal, consoante,
plosiva — e isso produz a assinatura característica de "voz sedada"
(formantes borrados); o ouvinte percebe que é sintético mesmo sem saber
identificar por quê. `pm_santa` a `speed=0.60` (decisão do video-02, ver
CLAUDE.md) usa exatamente esse mecanismo — funcionou bem no julgamento de
ouvido do Samuel pra esse vídeo específico, então **não foi refeito**, mas
não é o caminho recomendado daqui pra frente: prefira `speed` mais alto
(perto do natural) e regule o ritmo pela pausa.
- Como aplicar: o pipeline já corta o texto em "..." e quebras de
  parágrafo e insere SILÊNCIO DIGITAL entre os pedaços (`sintetiza()` em
  `s2_tts.py`) — isso já é o jeito certo (Kokoro não tem SSML/`<break>`,
  então o silêncio manual substitui). O que faltava era não depender do
  `speed` por cima disso.
- **Densidade decrescente pela pausa, não pela fala:** `FATOR_PAUSA_INICIO`/
  `FATOR_PAUSA_FIM` em `s2_tts.py` escalam `PAUSA_RESPIRO`/`PAUSA_PARAGRAFO`
  de 1,0× na primeira cena até 1,6× na última — a história fica mais
  rarefeita ao longo do episódio sem que a voz mude de velocidade.

**Vozes pt-BR disponíveis no Kokoro-82M**: `pm_santa` (masc., em uso desde
o video-01), `pm_alex` (masc.), `pf_dora` (fem.) — só 3 no pacote oficial.
Personas novas devem escolher entre essas 3 (ou trazer outro engine de TTS)
e validar por audição antes de fixar `speed` — a avaliação objetiva
(duração, % de silêncio) não substitui ouvir.

**Medir ritmo de verdade em vez de estimar** — pausas via ffmpeg
(`silencedetect=noise=-35dB:d=0.30`, somar `silence_duration`) e WPM
bruto/articulado a partir de palavras e duração real do áudio, não do
roteiro escrito. Ver `duracoes.json` (já grava `ppm` por cena) como ponto
de partida — falta ainda separar bruto de articulado e medir % de silêncio
por lá.

**Referências**: ACX/9300 palavras-hora (karencommins.com); faixas de WPM
por contexto (podcastify.io); velocidade de fala em PB, SciELO/CoDAS
(scielo.br/j/codas) e RBCS/UFPB (periodicos.ufpb.br/index.php/rbcs).

