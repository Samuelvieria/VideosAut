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

## Regras que valem para todos (colar junto com o prompt escolhido)

```
Antes de responder, quatro regras:

1. NÃO elogie o projeto. Não comece dizendo que está bem estruturado. Eu já
   sei o que fiz de certo; preciso do que está errado.
2. Marque CADA afirmação com [OBSERVADO] se você viu isso em dados ou casos
   concretos, [INFERIDO] se deduziu, ou [PALPITE] se está chutando. Uma
   resposta toda [PALPITE] é útil — uma resposta que esconde o palpite não é.
3. Se você não sabe, diga "não sei". Não preencha lacuna com plausibilidade.
4. No fim, escreva a frase: "Eu poderia estar errado sobre X" — onde X é a
   parte da sua resposta em que você tem menos confiança.
```

**Rode o mesmo prompt em 2–3 modelos diferentes.** Onde eles concordam, é sinal.
Onde divergem, é onde a incerteza real está — e é aí que vale testar em vez de
escolher pela resposta que soou melhor.

---

## A. Retenção e formato — *pré-mortem*

> Você é analista de retenção de uma MCN. Já viu centenas de canais falharem.
> Não dá conselho motivacional e não tem paciência para "crie conteúdo de
> qualidade".
>
> **Cenário: o vídeo acima foi publicado e fracassou.** 340 visualizações em
> 30 dias, retenção média de 11%, a maioria saindo antes dos 90 segundos.
>
> Explique **por que fracassou**. Não me diga o que fazer — me diga o que
> aconteceu. Liste as causas em ordem da mais provável para a menos, e para
> cada uma diga qual número no YouTube Analytics confirmaria ou descartaria
> aquela hipótese.
>
> Depois responda duas coisas, escolhendo, não listando opções:
>
> - A duração certa para este formato é X minutos. Diga o X e defenda.
> - A moldura do velho narrador nos primeiros 60 segundos: mantém ou corta?
>
> **Proibido:** falar de thumbnail, título ou SEO. Isso é outra conversa.
> Quero só o que acontece depois que a pessoa já clicou.

## B. Descoberta — *o mecanismo, não a lista*

> Você trabalha com crescimento de canais no YouTube e é cético com
> conteúdo de IA. Sua função aqui é dizer onde este canal vai travar.
>
> Canal novo, zero inscritos, nicho de sono, 2–3 vídeos por semana.
>
> **Pergunta única:** qual é o mecanismo de distribuição que efetivamente
> tira um canal de sono do zero hoje? Escolha **um** e explique como ele
> funciona na prática. Se a resposta honesta for "não existe, só volume e
> tempo", diga isso.
>
> Depois:
>
> - Escreva 3 títulos que você usaria para este vídeo, e explique o que cada
>   um está tentando explorar.
> - Diga uma coisa que este projeto está fazendo que **não deveria** estar
>   fazendo nesta fase.
>
> **Proibido:** "poste com consistência", "otimize a thumbnail", "use
> palavras-chave", "engaje com a comunidade". Se sua resposta caberia em
> qualquer canal de qualquer nicho, ela não serve.

## C. Risco de política — *cite ou admita*

> Você é consultor de conformidade de plataforma. Sua reputação depende de
> nunca inventar o que uma política diz.
>
> O canal acima usa voz sintética, imagens geradas por IA, ambiente sonoro
> sintetizado e pipeline automatizado. Tem roteiro escrito à mão, revisão
> humana obrigatória antes de publicar, 2–3 vídeos por semana e divulgação
> de conteúdo sintético ativada.
>
> 1. Cite o **texto oficial** da política de conteúdo inautêntico do YouTube,
>    com URL. Se você não consegue acessar ou não tem certeza da redação
>    atual, **diga isso e pare** — não parafraseie de memória.
> 2. Dê uma nota de risco de 1 a 5 para este canal ser desmonetizado nos
>    próximos 12 meses, e explique o que sustenta a nota.
> 3. Qual mudança **aumentaria** o risco sem parecer que aumenta? É o que eu
>    mais quero saber, porque é a que eu faria sem perceber.
> 4. Se você conhece casos reais de canais atingidos por essa política,
>    descreva o que tinham em comum. Se não conhece, diga que não conhece.

## D. Áudio — *um teste, não uma aula*

> Você é engenheiro de mixagem e já trabalhou com áudio para sono e
> meditação. Assuma que eu sei o básico de compressão e EQ.
>
> Mixagem atual: ambiente sintetizado (mar por eventos de onda com ataque
> rápido e cauda longa; chuva por ruído filtrado), estéreo por decorrelação
> real (fontes independentes por canal, correlação L/R ≈ 0), voz mono
> centrada, ducking sidechain de 4–6 dB com release de 1,5–3 s,
> masterização a −14 LUFS integrado com true peak em −1,5 dB.
>
> **Não me explique o que é ducking.** Me dê:
>
> 1. **Uma** mudança de parâmetro que você faria primeiro, com o valor
>    antes e depois, e o que eu deveria ouvir de diferente. Preciso poder
>    testar em um comando.
> 2. Um erro que essa cadeia provavelmente tem e que eu não listei — algo
>    que só aparece depois de 20 minutos de escuta, não nos primeiros 30
>    segundos.
> 3. −14 LUFS está certo para material de dormir, sabendo que o YouTube
>    normaliza para lá? Responda sim ou não antes de explicar.

## E. Bilíngue — *decida, não compare*

> Você é diretor de operações de um canal multilíngue. Já tocou os dois
> modelos e sabe onde cada um dói.
>
> O material visual é idêntico nos dois idiomas; só narração e metadados
> mudam. RPM em inglês é 3–5× o brasileiro. O dono é brasileiro e julga
> qualidade muito melhor em português.
>
> **Escolha uma arquitetura e defenda:** faixa de áudio adicional no mesmo
> vídeo, ou canais separados por idioma. Não faça tabela comparativa — eu já
> tenho uma. Escolha.
>
> Depois:
>
> - Descreva o modo de falha da opção que você **não** escolheu. O que dá
>   errado, e em quanto tempo?
> - Dado o RPM, começar pelo inglês é o certo — mesmo o dono julgando pior
>   a qualidade em inglês? Considere que ele não tem como saber se a
>   narração em inglês está boa.

## F. Imagem — *viés de treino*

> Você trabalha com geração de imagem em produção e conhece os vieses dos
> modelos de difusão.
>
> Problema: a cena da baleia branca de Moby Dick precisa de um **cachalote**
> (cabeça retangular ocupando um terço do corpo). O modelo entrega
> consistentemente uma **jubarte** (focinho pontudo, pregas na garganta,
> nadadeira peitoral longa). Cinco tentativas: descrever a anatomia
> explicitamente, mudar a pose de salto para perfil, e fechar o
> enquadramento só na cabeça. O modelo é Z-Image-Turbo, 8 passos, **sem
> suporte a `negative_prompt`**.
>
> 1. Qual técnica de prompt contorna viés de treino desse tipo? Quero o
>    mecanismo, não "seja mais específico" — já fui.
> 2. Existe vocabulário que ativa a região certa do espaço latente sem
>    nomear "baleia"? Termos de anatomia, de época, de estilo de ilustração?
> 3. img2img a partir de uma gravura do século XIX em domínio público
>    resolve, ou o viés volta na difusão mesmo com imagem de referência?
> 4. Estilo consistente entre 20 cenas: além de prefixo fixo e seed fixa, o
>    que mais funciona na prática?

## Depois de coletar as respostas

Traga tudo de volta para a conversa principal. O critério de triagem:

| situação | o que fazer |
|---|---|
| Contradiz uma medição nossa | **descartar**, salvo se vier com método verificável |
| Reabre decisão travada sem argumento novo | **descartar** |
| Afirmação marcada `[OBSERVADO]` | **verificar**, depois adotar |
| Afirmação marcada `[PALPITE]` | tratar como hipótese, não como dado |
| Opinião de produto (retenção, formato, título) | **peso alto** — é onde não temos dado próprio |
| Dois ou três modelos concordaram | sinal forte |
| Modelos divergiram | é aí que a incerteza real mora — testar, não escolher pela prosa |

Uma armadilha: a resposta mais bem escrita não é a mais certa. Modelos escrevem
com a mesma confiança quando sabem e quando não sabem — foi para isso que os
prompts exigem `[OBSERVADO] / [INFERIDO] / [PALPITE]` e a frase "eu poderia
estar errado sobre X". Se um modelo ignorar essas duas regras, a resposta dele
vale menos, não mais.
