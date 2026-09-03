---
projeto: Canal de Sono Automatizado
assunto: briefing para consultar outros modelos de IA
data: 2026-09-02
uso: colar a PARTE 1 + um dos prompts da PARTE 2 numa conversa nova
---

# Briefing externo

Este arquivo existe para extrair valor de outros modelos (ChatGPT, Gemini, Grok,
DeepSeek…) sem gastar a conversa toda explicando o projeto e sem receber de volta
conselho que já foi avaliado e descartado aqui.

**Como usar:** cole a **Parte 1** inteira, depois cole **um** dos prompts da
Parte 2. Um prompt por conversa — misturar assuntos dilui a resposta.

---

# PARTE 1 — Contexto (colar sempre)

## O que é

Canal de YouTube de conteúdo para dormir (*sleep stories*): narração calma em
português sobre uma sequência de imagens em pixel art, com ambiente sonoro de
chuva e mar por trás. Sem vídeo real, sem rosto, sem música de terceiros.

Produção automatizada por um pipeline Python + FFmpeg. **Nada foi publicado
ainda** — o primeiro vídeo está pronto para revisão.

## Como chegamos aqui (10 dias, 15 commits)

O projeto já mudou de forma várias vezes, sempre por evidência. Isso importa para
quem for opinar: **não há apego ao formato atual.**

| quando | mudança | motivo |
|---|---|---|
| 24/08 | repositório criado, primeiro roteiro escrito | *A Chuva na Cabana*, 2.822 palavras |
| 26/08 | **1–3 h → 30 min** | decisão de produto; duração virou parâmetro, não constante |
| 26/08 | **1 imagem estática → ~20 imagens em sequência** | referência de formato encontrada |
| 26/08 | **primeiro vídeo abandonado** | a cabana virou Moby Dick, com moldura de narrador |
| 27/08 | pipeline automatizado (TTS, imagem, legenda, render) | estágios mecânicos, sem LLM dentro |
| 28/08 | **migração para workstation** (Windows, RTX 3060) | legendas levavam 87 min em CPU |
| 28/08 | interface web local (`estudio/`) | mixer e execução de estágios pelo navegador |
| 28/08 | **ritmo lento por pausa, não por `speed`** | `speed` baixo degradava pronúncia (medido) |
| 02/09 | **imagens 640×360 → 1024×576** | o gerador nunca honrou o tamanho pedido |

O roteiro da cabana (2.822 palavras) existe pronto e nunca virou vídeo. Serviu
para validar a voz e o TTS.

## O primeiro vídeo (referência concreta)

| | |
|---|---|
| Tema | Moby Dick, adaptação própria em português |
| Duração | 33,5 min (32,5 narrados + 1 min de cauda só ambiente) |
| Roteiro | 3.467 palavras, escritas do zero |
| Cenas | 20 imagens, ~100 s cada, com pan lento |
| Voz | TTS local (Kokoro `pm_santa`), 103 palavras/min |
| Moldura | um velho baleeiro no cais reconta a história — invenção nossa, não está no livro |

A moldura existe por três motivos: cria obra original sobre um texto em domínio
público, justifica a persona da voz, e dá abertura e fecho ao vídeo.

## Arquitetura

```
roteiro.md ──► s2_tts    (Kokoro local)      ──► um .wav por cena
plano.json ──► s3_imagens (fal.ai Z-Image)   ──► 20 PNG 1024×576
           ──► s4_legendas (faster-whisper)  ──► SRT alinhado ao roteiro
           ──► s5_render  (FFmpeg puro)      ──► final.mp4 + mix de áudio
```

Estágios determinísticos e idempotentes. Nenhum LLM roda dentro do pipeline —
LLM só escreve/adapta roteiro, fora do loop de produção.

Há também `estudio/`, uma interface web local (FastAPI) para operar o pipeline
pelo navegador: mixer de áudio, cadastro de personas de voz, execução dos
estágios e registro de correções. A separação é rígida — `estudio/` importa de
`pipeline/`, nunca o contrário, e invoca os estágios por subprocesso. Cada
estágio continua rodável sozinho por linha de comando.

São ~2.200 linhas de Python no total, entre pipeline e interface.

**Não existem, de propósito:** geração automática de roteiro e upload automático.
A regra do projeto é não construir a fábrica antes de validar o produto.

## Estado atual

| | |
|---|---|
| Roteiro do vídeo 1 | pronto — 3.467 palavras |
| Narração | gerada — 32,5 min, 20 cenas |
| Imagens | 20 geradas em 1024×576 |
| Ambiente sonoro | sintetizado, estéreo, por cena |
| Legendas pt-BR | 313 blocos, alinhadas ao roteiro |
| Render final | **pendente** — o último é de imagens antigas |
| Publicação | **nada publicado** |
| Versão em inglês | planejada, não iniciada |
| Roteiro automático / upload automático | **não existem, de propósito** |

O gargalo não é técnico. É que ninguém viu o vídeo ainda.

## Custo mensal real

~R$ 25 (US$ 5). Imagem ~R$ 18 (fal.ai, ~700 gerações), voz R$ 0 (TTS local),
adaptação de roteiro para inglês ~R$ 9 (Claude API). Hardware: um MacBook M2 de
8 GB e uma workstation Windows com RTX 3060.

## Decisões TRAVADAS — não sugerir alternativas

Cada uma custou análise ou medição. Sugerir o contrário é ruído.

1. **FFmpeg puro, zero editor de vídeo.** Não é limitação, é escolha: o formato
   não tem timeline, corte ou transição complexa.
2. **TTS local (Kokoro, Apache 2.0).** ElevenLabs e afins foram avaliados e
   custam caro no volume real (26+ min de fala por vídeo). XTTS-v2 é CPML e
   proíbe uso comercial.
3. **Ambiente sonoro gerado proceduralmente** (ruído filtrado + eventos de onda
   sintetizados). Motivo: Content ID varre 100% dos uploads por impressão
   digital, e som gerado não tem referência para casar. Biblioteca "royalty
   free" NÃO resolve isso — licença e Content ID são coisas separadas.
4. **Legendas soft**, nunca queimadas.
5. **Pixel art com upscale de escala inteira e nearest-neighbor.** Qualquer
   interpolação borra a grade e mata o estilo.
6. **Cadência de 2–3 vídeos por semana**, nunca diária.
7. **Gate manual antes de publicar**; todo upload sobe como privado.
8. **Divulgação de conteúdo sintético ativada.**

## Medições já feitas (não precisa estimar de novo)

- Modelo de difusão **não processa negação**: escrever "a chuva parou" contém
  "chuva" e o modelo desenha chuva. Só descrever o que existe funciona.
- O gerador de imagem **empurra silenciosamente** qualquer dimensão abaixo de
  512px. Pedir 640×360 devolvia 640×512.
- **Reduzir a velocidade do TTS degrada a pronúncia** — verificado transcrevendo
  o áudio de volta: em `speed=0.60` uma palavra saiu errada; em `1.00` saiu
  certa. O ritmo lento agora vem de **pausa maior entre frases**, não de fala
  esticada.
- O TTS **ignora reticências**; a pausa é inserida por código, cortando o texto
  e emendando silêncio.
- Render de 30 min leva ~8 min; rerodar sem mudanças leva segundos.
- Masterização a **−14 LUFS** (o alvo que o YouTube normaliza), true peak −1.5.
- Áudio para dormir quer **dinâmica plana** — o ambiente nunca some sob a voz.
  Isso é o oposto da regra de podcast (música cai 20–30 dB sob a fala).

## O que ainda está em aberto

1. Nada publicado — **zero dado de retenção ou audiência**.
2. Não se sabe se 33,5 min é a duração certa, ou se sleep content pede 1–3 h.
3. Não se sabe se a moldura do narrador ajuda ou atrapalha.
4. Thumbnail e título para nicho de sono ainda não testados.
5. Versão em inglês planejada: indefinido se vira faixa de áudio extra no mesmo
   vídeo ou canal separado.
6. Risco de política: o YouTube desmonetiza "conteúdo inautêntico" (produção em
   massa com template). Não se sabe onde exatamente este formato cai.

---

# PARTE 2 — Prompts (escolher UM por conversa)

## A. Retenção e formato

> Acima está o briefing de um canal de sono no YouTube, ainda sem nada
> publicado. Preciso da sua leitura sobre **retenção**, não sobre produção.
>
> 1. Para conteúdo de sono, o que efetivamente segura o espectador nos
>    primeiros 60 segundos, quando ele ainda está escolhendo se fica?
> 2. 33,5 minutos é um erro de formato? Canais grandes do nicho usam 1–3 h.
>    Qual a lógica por trás disso — watch time bruto, ou o vídeo não acabar
>    enquanto a pessoa dorme?
> 3. A moldura do velho narrador ("vou te contar a história do Pequod") ajuda
>    ou é fricção antes do conteúdo?
> 4. Um vídeo de sono deve ter clímax narrativo, ou qualquer pico de tensão é
>    um defeito porque acorda quem estava adormecendo?
>
> Seja concreto e diga em que baseia cada resposta. Se for intuição, diga que é.

## B. Descoberta e primeiros inscritos

> Acima está o briefing. O canal tem **zero inscritos** e nada publicado.
>
> 1. Como um canal de sono novo é descoberto hoje? Busca, sugeridos, Shorts?
> 2. Título e thumbnail para esse nicho: o que funciona, e o que só parece que
>    funciona?
> 3. Faz sentido usar Shorts como porta de entrada para vídeo longo de sono,
>    ou o público é outro?
> 4. Quanto tempo, realisticamente, até os primeiros 1.000 inscritos publicando
>    2–3 vídeos por semana com essa qualidade?
> 5. O que você **não** faria no lugar dele?

## C. Risco de política do YouTube

> Acima está o briefing. A preocupação é a política de **conteúdo inautêntico**,
> que desmonetiza produção em massa com template.
>
> Este canal usa: voz sintética, imagens geradas por IA, ambiente sintetizado,
> pipeline automatizado — mas roteiro escrito à mão, revisão humana obrigatória
> antes de publicar, 2–3 vídeos por semana, e divulgação de conteúdo sintético
> ativada.
>
> 1. Onde exatamente esse formato cai na política? Cite o texto oficial.
> 2. Quais sinais concretos separam "IA como ferramenta" de "produção em massa"?
> 3. O que aumentaria o risco sem parecer que aumenta?
> 4. Casos reais de canais desmonetizados por isso — o que tinham em comum?

## D. Áudio

> Acima está o briefing. Sobre a mixagem, especificamente.
>
> Hoje: ambiente sintetizado (mar por eventos de onda com ataque rápido e cauda
> longa, chuva por ruído filtrado), estéreo por decorrelação real (seeds
> independentes por canal, correlação L/R ≈ 0), voz mono centrada, ducking
> sidechain suave de 4–6 dB, masterização a −14 LUFS.
>
> 1. Para conteúdo de sono, essa profundidade de ducking está certa?
> 2. −14 LUFS é apropriado, ou material para dormir deve ser mais baixo mesmo
>    sabendo que o YouTube normaliza?
> 3. Que camada sonora sentiria falta num ambiente de mar noturno em pixel art?
> 4. Como sintetizar rangido de madeira de navio de forma convincente, sem
>    gravação de terceiros?

## E. Bilíngue (pt-BR + inglês)

> Acima está o briefing. Quero servir português e inglês. O material visual é o
> mesmo; só narração e metadados mudam. RPM em inglês é 3–5× o brasileiro.
>
> 1. Uma faixa de áudio extra no mesmo vídeo, ou canal separado por idioma?
>    Considere algoritmo, watch time e esforço de manutenção.
> 2. Se canal separado: os dois publicando o mesmo formato em paralelo agravam
>    o risco de "conteúdo inautêntico"?
> 3. Vale começar pelo inglês, dado o RPM, mesmo o dono sendo brasileiro e
>    julgando melhor a qualidade em português?

## F. Imagem

> Acima está o briefing. As imagens são pixel art gerada, 1024×576, 20 por
> vídeo, estilo travado por prefixo de prompt e seed fixa por cena.
>
> Problema concreto: a cena da baleia branca de Moby Dick sai como **jubarte**,
> não cachalote — cabeça pontuda em vez do bloco quadrado. Cinco tentativas,
> incluindo descrever a anatomia explicitamente e trocar a pose. O modelo tem
> viés de treino ("baleia" → jubarte).
>
> 1. Como contornar viés de treino desse tipo sem trocar de modelo?
> 2. Vale usar img2img a partir de uma gravura do século XIX em domínio público?
> 3. Como manter consistência de personagem entre 20 cenas, além de repetir a
>    descrição literal e fixar a seed?

---

## Depois de coletar as respostas

Traga tudo de volta para esta conversa. O critério de aproveitamento é:

- **Contradiz uma medição nossa?** Descartar, a não ser que traga método
  verificável — nossos números foram medidos nesta máquina.
- **Reabre decisão travada sem argumento novo?** Descartar.
- **É afirmação verificável?** Testar antes de adotar.
- **É opinião de produto** (retenção, formato, título)? Aí vale mesmo, porque é
  onde temos zero dado próprio.
