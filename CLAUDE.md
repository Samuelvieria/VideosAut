# Contexto do projeto — Canal de Sono Automatizado

Análise completa em [docs/viabilidade-tecnica.md](docs/viabilidade-tecnica.md).
**Estado atual, custo por vídeo e ordem das frentes abertas em
[docs/estado-e-direcao.md](docs/estado-e-direcao.md)** (03/09/2026) — comece por
ele. Resumo das decisões de arquitetura já tomadas — não reabrir essas
discussões sem motivo novo:

## Decisões fixadas

- **Zero editor de vídeo.** Tudo em FFmpeg puro (render, mix de áudio, concat).
  Nada de DaVinci/Premiere/CapCut.
- **Formato: 30 min, não 1–3 h.** Decidido em 26/08/2026. A duração é um *parâmetro*,
  não uma constante — o pipeline é idêntico para 30 min e 3 h, muda o número de cenas
  e o `-t`. Se a retenção pedir formato longo depois, é um número, não uma reescrita.
  **CONTRARIADO PELO MERCADO em 04/09/2026.** Medido em [docs/mercado.md](docs/mercado.md):
  não existe **um só** caso de sucesso na amostra perto de 30–41 min. A faixa que funciona
  em narrativa é **65–170 min**; ambiente é medido em horas. O padrão de projeto novo
  no estúdio já nasce em **75 min** (mediana do History at Night). O video-02 tem 41 e o
  video-03 foi planejado com 30 — este último ainda não foi produzido, então mudar é
  barato agora e caro depois.
- **N imagens em sequência, não 1 imagem estática.** Referência de formato:
  narração + sequência de cenas ilustradas, sem vídeo real. ~20 cenas em 30 min.
- **Claude Code é o engenheiro, não o servidor de produção.** Quem roda em produção é um
  pipeline Python + cron, determinístico e idempotente. Claude (API, não Claude Code) só
  gera o estágio criativo (roteiro/metadados) dentro do pipeline.
- **Sem prompt fixo.** Banco de premissas + 5–8 estruturas narrativas sorteadas por vídeo,
  para não cair em "conteúdo inautêntico" (política do YouTube desde jul/2025).
- **Cadência humana: 2–3 vídeos/semana**, nunca 7. Volume alto + formato idêntico é o sinal
  de risco mais forte. **Em revisão desde 04/09/2026** — a pesquisa de mercado
  ([docs/mercado.md](docs/mercado.md)) mostrou que os dois canais de referência do nicho
  publicam **um vídeo a cada 5 semanas** com seis vídeos no total e ~80 mil inscritos cada,
  enquanto o de 399 vídeos tem a pior mediana de views. Não é decisão tomada; é uma
  premissa que o dado contraria e que precisa da sua leitura.
- **Gate manual obrigatório antes de publicar.** Todo upload sobe como `private`; você aprova
  antes de tornar público. Isso também contorna a trava automática de vídeos como privados
  em projetos de API não auditados (armadilha nº1 da seção 5).
- **Áudio ambiente gerado proceduralmente** (brown/pink noise via FFmpeg `anoisesrc`), nunca
  música de terceiros sem whitelist de Content ID. É a única fonte impossível de dar match.
- **Legendas sempre soft (`captions.insert`), nunca queimadas** — permite multi-idioma sem
  re-renderizar e não atrapalha o objetivo do conteúdo (texto na tela é contraproducente
  em vídeo de sono).
- **Divulgação de conteúdo sintético ativada** para voz/imagem geradas (toggle no Studio).

## TTS — decisão tomada (vídeo 1, validar se mantém para os próximos)

Trocamos Azure por **Kokoro-82M** (local, Apache-2.0, licença comercial livre — ao
contrário do XTTS-v2/Coqui, que é CPML e proíbe uso comercial). Resolve o bloqueio
de conta Azure e roda 100% offline no Mac (CPU, sem GPU).

- Voz: `pm_santa` (lang_code `p` = pt-BR), **speed=0.60** (padronizado em 27/08/2026;
  era 0.80 no vídeo 1, depois 0.75 no vídeo 2 — ver `fase0/video-02/plano.json`),
  sem pitch shift.
- **`speed` baixo como mecanismo principal de lentidão está superado desde
  28/08/2026** (pesquisa de ritmo de narração pt-BR — ver
  `.claude/skills/qualidade-producao-video/SKILL.md` § Ritmo de narração):
  estica a fala toda por igual (vogal e consoante) e soa "sedado". O
  `pm_santa`/0.60 do video-02 fica como está — já aprovado de ouvido, não
  foi refeito — mas **personas novas usam speed perto do natural + pausa
  crescente entre frases/parágrafos** (`FATOR_PAUSA_INICIO`/`FIM` em
  `pipeline/s2_tts.py`), não o multiplicador. Kokoro-82M só tem 3 vozes
  pt-BR: `pm_santa`, `pm_alex`, `pf_dora` — ver `estudio/dados/personas.json`
  para os candidatos em avaliação.
- Testamos blend de vozes (`load_voice("v1,v2")`, média dos vetores de estilo) e
  pitch shift via `ffmpeg-full` + filtro `rubberband` (`formant=preserved` para não
  soar artificial) — nenhum dos dois melhorou em relação à voz pura mais lenta.
- Setup: `.venv` no root do repo (Python 3.12 via Homebrew, não o Python 3.9 do
  sistema) + `pip install kokoro soundfile` + `brew install espeak-ng`.
- Render final precisa de `ffmpeg-full` (não o `ffmpeg` padrão do Homebrew) por
  causa do `librubberband` — instalado keg-only em
  `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`.

## Render — arquitetura medida (26/08/2026)

Cada cena é um **clipe independente** com fade-in/fade-out para preto e GOP fechado
alinhado; a montagem final é `concat -c copy`. Nada de `xfade` no vídeo inteiro.

- Medido: **0,56× realtime** a 24 fps (clipe de 30 s renderizou em 17 s) com
  `preset medium -crf 21`. 30 min de vídeo ≈ 17 min de render, paralelizável por cena.
- `concat -c copy` de clipes com GOP alinhado: **instantâneo, sem artefato de emenda**
  (verificado com `-f null`).
- Fade-to-preto entre cenas em vez de crossfade: além de mais calmo para conteúdo de
  sono, é o que permite o `-c copy` (crossfade obrigaria reencodar tudo).

**Duas pegadinhas do `zoompan`, ambas medidas** (histórico — o movimento de
cena implementado em 27/08/2026 usa `crop` deslizante + escala inteira, não
`zoompan`, exatamente para não cair nelas; ver `pipeline/s5_render.py`):

1. `-t` é opção de **saída** — vai depois do `-vf`. Com `-t` antes do `-i`, o
   `-framerate` alimenta N frames de entrada e o `zoompan` gera `d` frames de saída
   para cada um: milhões de frames, o comando nunca termina.
2. `scale` **antes** do `zoompan` é obrigatório. O `zoompan` reescala a imagem inteira
   a cada frame de saída; alimentá-lo com 4K direto é o que trava o render.

O comando corrigido está na seção 6b do doc de viabilidade.

## Imagens — ferramenta e direitos

**Gerador: fal.ai (Z-Image-Turbo)**, via API — não Draw Things/SD 1.5 local como o
doc de viabilidade original previa. Migrou junto com a workstation Windows
(`pipeline/s3_imagens.py`); Draw Things era o plano pro M2 sem GPU dedicada de
sobra, mas a API acabou sendo o caminho real desde o video-02.

A resolução deixou de ser constante em 04/09/2026: o `plano.json` pode trazer
`resolucao: [l, a]`, gravado pela persona ao criar o projeto, e o `s3_imagens` lê
(com o valor abaixo como padrão, então plano antigo não muda). O `s5_render`
continua abortando se a fonte não bater com o que o pan assume.

**Gerar em 1280×720 e fazer upscale nearest-neighbor ×2 para 1920×1080** (não
640×360 ×3 — essa combinação nunca funcionou de verdade: **medido em
02/09/2026, a fal.ai não entrega dimensão abaixo de 512px num eixo**, então
640×360 e 768×432 (a correção intermediária de 27/08) vinham sempre esticadas
pra 640×512/768×512, fora de 16:9, e o `s5_render` cortava a cena em silêncio
sem avisar. 1280×720 é múltiplo do preset nativo `landscape_16_9` do modelo
(1024×576) e devolve exatamente o que é pedido. Escala inteira e
`flags=neighbor` continuam obrigatórias — qualquer interpolação borra a grade
de pixels. Ver `pipeline/s3_imagens.py` e `PAN_*` em `pipeline/s5_render.py`.

**`enable_prompt_expansion: False`** no payload da fal.ai — ligado, o LLM
interno do provedor reescreve o prompt a cada chamada e destrói a
consistência de estilo entre cenas (achado junto com a correção de resolução).

Estilo travado por vídeo (`fase0/video-NN/estilo.yaml`: prefixo, negativos,
paleta, seed fixa por cena) — mesma base visual entre vídeos, ambientação
troca por episódio. Padrão emprestado do OpenMontage; o código dele é AGPL,
não usar.

**Para temas históricos, usar imagens de acervo livremente.** Decisão do Samuel em
26/08/2026: **não gatear imagem por status de direito** — ele avaliou o risco de
reclamação e assumiu. Não reabrir essa discussão. Fica só o registro leve de origem
(instituição, URL, autor) em [docs/fontes-imagens.md](docs/fontes-imagens.md), que
serve para refazer a imagem, não para autorizar.

Preferir `uso: referencia_img2img` por motivo **estético**: pintura a óleo no meio de
uma sequência de pixel art quebra a linguagem visual do canal.

Diferença crítica em relação ao áudio: imagem no YouTube não passa por Content ID —
reclamação vira *strike*, não claim. Áudio custa receita, imagem custa o canal.

Quando a obra-fonte for histórica (ex.: Moby-Dick, 1851): **o texto original é PD, mas
traduções publicadas são obra autoral protegida.** A adaptação em português tem que ser
escrita por nós, nunca colada de tradução em catálogo.

## Hardware e perfis

Máquina atual: MacBook Pro **M2, 8 GB, 8 CPUs, sem GPU**. Migração para workstation
planejada — ver [docs/migracao-workstation.md](docs/migracao-workstation.md).

Nada nos estágios lê hardware direto: tudo passa por `pipeline/perfil.py`, que
detecta GPU/RAM/CPU e devolve modelo de whisper, device, preset de x264 e
paralelismo. Forçar com `PERFIL=teste|m2-8gb|workstation`.

Gargalo medido: `s4_legendas` com `large-v3` em CPU roda a **3,44× realtime** —
~87 min por vídeo. `s2_tts` leva ~12 min e `s5_render` 8 min. A máquina nova compra
de volta basicamente o tempo de legenda.

## Não pular a Fase 0

O maior risco do projeto não é técnico — é construir automação eficiente demais para um
produto não validado. Não escrever `s1_roteiro.py`/`s6_upload.py` antes de ter 2–3 vídeos
manuais publicados e alguma leitura de retenção/audiência.

## Itens não verificados (não assumir como fato)

Ver seção 10 do documento de viabilidade — custo de quota de `videos.insert`/`captions.insert`,
nome exato do campo de divulgação sintética na Data API v3, comportamento de loudness do
YouTube, expiração de refresh token OAuth. Confirmar na documentação oficial antes de
depender desses valores em código.

## Ritmo de narração — medido em 04/09/2026

Nossa narração roda a **102 palavras/min** sobre os 32,2 min de fala real do
video-02 (não sobre os 41 min totais, que incluem a cauda). As referências:
Dreamoria **128 ppm**, History at Night **180 ppm**. Fala de conversa fica em ~150.

**Ninguém desacelera, nem eles nem nós.** Por terço de vídeo eles variam −4,1%
e −1,0%; nosso `FATOR_PAUSA`, medido com o roteiro real em três posições do
episódio, dá 163, 168 e 169 ppm — praticamente reta. **O mecanismo faz muito
menos do que se supunha.** Quem produz a nossa lentidão é a pausa de
`PAUSA_PARAGRAFO` a cada quebra de parágrafo, não a rampa ao longo do episódio.

Nenhuma das duas referências tem **cauda de ambiente**. As duas narram até o
último segundo. A nossa cauda de 9 min é aposta não testada.

Amostras de ritmo para escutar: `fase0/_vozes-candidatas/`.

## Estrutura do repositório

Fase 0 (validação manual) rodando em paralelo com a Fase 1 (automação dos estágios
mecânicos). `pipeline/` já tem `s2_tts`, `s4_legendas` e `s5_render` — ver
[pipeline/README.md](pipeline/README.md). `s1_roteiro.py` e `s6_upload.py` continuam
proibidos até 2–3 vídeos publicados.
`output/` e `state/` (quando existirem) são gerados localmente e não versionados.
