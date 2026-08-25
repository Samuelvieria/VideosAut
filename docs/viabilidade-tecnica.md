---
projeto: Canal de Conteúdo para Dormir — Pipeline Automatizado
autor: análise técnica
data: 2026-08-24
status: estudo de viabilidade / arquitetura
---

# Canal de Sono Automatizado — Viabilidade Técnica e Arquitetura

> **Nota de método:** cada afirmação abaixo está marcada como `[FATO]` (documentação
> oficial ou comportamento documentado), `[SECUNDÁRIO]` (fonte de terceiros, precisa
> verificação) ou `[HIPÓTESE]` (minha inferência técnica, não verificada).
> Preços de API mudam com frequência — todos os valores citados são de fontes
> secundárias datadas e **devem ser confirmados na página oficial do fornecedor**.

---

## 1. Resposta direta à sua pergunta

**"O Claude Code consegue acessar programas de edição de vídeo?"**

Depende do que você chama de "acessar". Três categorias distintas:

| Categoria | Claude Code consegue? | Como |
|---|---|---|
| **CLI / bibliotecas** (FFmpeg, ImageMagick, SoX, MoviePy, whisper.cpp, Blender `-b`, `aerender` do After Effects) | **Sim, nativamente** | Ele executa `bash`. Se roda no terminal, ele roda. `[FATO]` |
| **Apps com API de script** (DaVinci Resolve via Python, Blender via `bpy`, Nuke via Python) | **Sim, indiretamente** | Ele escreve e executa o script Python; quem fala com o app é o script, não o Claude. `[FATO]` |
| **GUI por cliques** (arrastar clipe na timeline do Premiere, clicar em botão do CapCut) | **Não** | Claude Code não tem controle de mouse/teclado do desktop. Precisaria de camada externa (xdotool, PyAutoGUI, AppleScript) que *você* expõe como CLI. `[FATO]` |

### O ponto que importa mais que a resposta

**Para um canal de sono você não precisa de editor de vídeo nenhum.**

Um vídeo de sono é, estruturalmente:

```
1 imagem (ou 1 loop curto de 30–60 s)  +  1 trilha de áudio de 1–3 h
```

Não tem corte, não tem transição, não tem timeline. Isso é `ffmpeg`, não Premiere.
Colocar DaVinci Resolve nesse pipeline é adicionar uma dependência de GUI, licença
paga e ~8 GB de RAM para fazer o que um comando de 4 linhas faz melhor e mais rápido.

**Recomendação: FFmpeg puro. Zero editor de vídeo no pipeline.**

Sobre o Resolve, para registro: a API de scripting Python existe e o app roda em
modo headless (`-nogui`) `[FATO]` — <https://resolvedevdoc.readthedocs.io/en/latest/API_intro.html>.
Há fontes secundárias afirmando que a API só é exposta na versão **Studio** (paga)
`[SECUNDÁRIO]`. **Não confirmei isso na documentação oficial da Blackmagic** — se
você quiser esse caminho, verifique antes de comprar. Mas repito: você não precisa.

---

## 2. Erro de arquitetura na sua ideia original (causa raiz)

Você descreveu: *"crio uma rotina com o Claude Code que ele crie conteúdo com um
mesmo prompt, ele cria para uma semana e posta"*.

Há **dois problemas estruturais** aí, e o segundo pode matar o canal.

### 2.1 Problema técnico — LLM dentro do loop de produção

Um LLM agêntico é **não determinístico**. Se ele é quem executa o pipeline toda
semana, você tem:

- falhas silenciosas (ele "acha" que renderizou e não renderizou);
- variação de custo imprevisível por execução;
- debugging impossível (não há stack trace, há prosa);
- risco de ação irreversível (upload público de arquivo errado).

**Arquitetura correta — separação de papéis:**

```
Claude Code  →  ESCREVE e MANTÉM o pipeline (papel de engenheiro)
Pipeline Python + cron  →  EXECUTA o pipeline (determinístico, idempotente, logado)
Claude API (dentro do pipeline)  →  gera SÓ o estágio criativo (roteiro/metadados)
```

O Claude Code é seu engenheiro, não seu servidor de produção. O que entra em `cron`
é um script Python que você consegue rodar 100 vezes e obter 100 resultados válidos.

Se ainda assim quiser Claude Code no runtime, o modo correto é headless:

```bash
claude -p "$PROMPT" \
  --output-format json \
  --allowedTools "Bash(python3:*),Read,Write" \
  --max-turns 30 \
  --permission-mode dontAsk \
  > resultado.json 2> claude.err
```

`[SECUNDÁRIO]` — flags documentadas em <https://code.claude.com/docs/en/cli-reference>
(confirme os nomes exatos na versão que você tiver instalada).

**Sobre agendamento — a doc oficial é explícita** `[FATO]`
(<https://code.claude.com/docs/en/scheduled-tasks>):

| | Cloud (Routines) | Desktop scheduled tasks | `/loop` (sessão) |
|---|---|---|---|
| Precisa da máquina ligada | Não | Sim | Sim |
| **Acesso a arquivos locais** | **Não (clone limpo)** | **Sim** | Sim |
| Persistente após restart | Sim | Sim | Restaurado com `--resume` |
| Intervalo mínimo | 1 hora | 1 minuto | 1 minuto |

Tarefas de sessão **expiram em 7 dias** e morrem quando você fecha o terminal `[FATO]`.

**Consequência direta:** para um pipeline de vídeo (que manipula arquivos de GB no
disco), **Routines na nuvem não serve** — não tem acesso a arquivos locais. Sobra
Desktop scheduled task (macOS/Windows) ou, o que eu recomendo, `cron`/`systemd timer`
comum chamando seu script Python.

### 2.2 Problema de política — este é o risco real do projeto

**"Mesmo prompt, uma semana de vídeos, postagem automática" é a descrição literal do
que o YouTube desmonetiza.**

`[FATO]` Em **15 de julho de 2025** o YouTube renomeou a política de "conteúdo
repetitivo" para **"conteúdo inautêntico"**, e em **julho de 2026** publicou um
esclarecimento com três categorias explicitamente não monetizáveis.
<https://support.google.com/youtube/answer/1311392>

`[SECUNDÁRIO]` O que a cobertura de imprensa e os guias descrevem como padrão de risco:

- vídeos com template e substituição mínima entre eles;
- slideshows com narração TTS lida verbatim e sem edição;
- alta frequência de upload com formato idêntico;
- ausência de comentário, estrutura ou valor autoral.

Fontes: <https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/>
e <https://www.auditsocials.com/blog/youtube-inauthentic-content-policy-2026-mass-produced-ai-generated-monetization-creators-brands>

`[SECUNDÁRIO]` Houve ondas de desmonetização e remoção do YPP em dez/2025 e início de
2026 atingindo canais com milhões de views por esse motivo.

**Isso não é proibição de IA.** IA como ferramenta continua elegível. O que é punido
é o padrão industrial sem valor autoral.

`[FATO]` Além disso: divulgação de conteúdo sintético é obrigatória quando o conteúdo
é realista e alterado/gerado — o toggle "conteúdo alterado ou sintético" no YouTube
Studio. <https://support.google.com/youtube/answer/14328491>

#### Mitigações concretas (aplicáveis no pipeline)

1. **Não use um prompt fixo.** Use um *banco de premissas* + variação estrutural.
   Cada vídeo deve ter roteiro, imagem, paleta, ritmo e duração diferentes.
2. **Cadência humana.** 2–3 vídeos por semana, não 7. Volume alto + formato idêntico
   é o sinal mais forte de risco.
3. **Camada autoral real.** Você revisa e edita cada roteiro antes do render. É o
   `human-in-the-loop` que separa "IA como ferramenta" de "conteúdo em massa".
4. **Divulgação ligada** para voz sintética e imagens geradas. Não vale a pena arriscar.
5. **Um gate manual obrigatório** no pipeline: renderiza tudo automático, sobe como
   `private`, e o `public` só depois da sua aprovação.

---

## 3. Segundo risco: Content ID no áudio ambiente

Canal de sono vive de música/ambiente. Isso é o campo minado mais denso do YouTube.

`[FATO]` "Royalty-free" **não** significa "livre de reivindicação". O Content ID faz
match por impressão digital de áudio independentemente da licença que você comprou.
Um trecho de 3 segundos pode gerar claim.
<https://support.google.com/youtube/answer/15577610?hl=pt-BR>

`[FATO]` A única fonte que o YouTube garante que **não** será reivindicada é a
**Biblioteca de Áudio do YouTube Studio** (faixas sem restrição de direitos).
<https://support.google.com/youtube/answer/3376882?hl=pt-BR>

`[FATO]` Uma reivindicação redireciona receita; não é strike, mas em canal automatizado
a 100% do catálogo, é o mesmo que não monetizar.
<https://support.google.com/youtube/answer/6013276?hl=pt-BR>

**Estratégia de menor risco, em ordem:**

1. **Ruído/ambiente gerado proceduralmente por você** (brown/pink noise, chuva
   sintetizada, drones em Python/SoX). Impossível dar match porque não existe
   referência. É a opção mais segura e custa R$ 0.
2. Biblioteca de Áudio do YouTube Studio.
3. Creator Music (dentro do Studio, com licenciamento resolvido — disponibilidade
   por região) `[FATO]`, ver link acima.
4. Bibliotecas comerciais — **só com contrato que inclua whitelist de Content ID
   para o seu Channel ID**. Sem isso, você vai gastar meses disputando claims.

`[HIPÓTESE]` Ruído gerado proceduralmente também resolve outro problema: é
tecnicamente "original" no sentido autoral, o que ajuda no argumento de conteúdo
não-inautêntico.

Exemplo de brown noise puro em FFmpeg (sem nenhuma dependência externa):

```bash
# 3 h de brown noise com filtro passa-baixa suave e fade de 5 min no fim
ffmpeg -f lavfi -i "anoisesrc=color=brown:amplitude=0.35:r=48000:d=10800" \
  -af "lowpass=f=500,highpass=f=20,afade=t=in:st=0:d=30,afade=t=out:st=10500:d=300" \
  -c:a flac ambiente.flac
```

---

## 4. Arquitetura do pipeline

```
                        ┌─────────────────────────────┐
                        │  banco_premissas.yaml       │
                        │  (você escreve, 50–200 itens)│
                        └──────────────┬──────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │ [1] ROTEIRO   — Claude API          │
                    │     saída: JSON estruturado         │
                    │     script.txt + metadata.json      │
                    └──────────────────┬──────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
   ┌──────────▼─────────┐  ┌───────────▼──────────┐  ┌──────────▼─────────┐
   │ [2] TTS            │  │ [3] IMAGENS          │  │ [4] METADADOS      │
   │ narracao.wav       │  │ bg_4k.png            │  │ título/desc/tags   │
   │ + timestamps.json  │  │ thumb.png            │  │ i18n               │
   └──────────┬─────────┘  └───────────┬──────────┘  └──────────┬─────────┘
              │                        │                        │
   ┌──────────▼─────────┐              │                        │
   │ [5] LEGENDAS       │              │                        │
   │ alinhamento forçado│              │                        │
   │ → .srt pt-BR       │              │                        │
   │ → tradução N idio. │              │                        │
   └──────────┬─────────┘              │                        │
              │                        │                        │
        ┌─────▼────────────────────────▼──────┐                 │
        │ [6] RENDER — FFmpeg                 │                 │
        │   6a mix de áudio (duck + loudnorm) │                 │
        │   6b loop de vídeo (concat -c copy) │                 │
        │   6c mux final                      │                 │
        └─────────────────┬───────────────────┘                 │
                          │                                     │
                ┌─────────▼─────────────────────────────────────▼──┐
                │ [7] GATE MANUAL  → status: private              │
                └─────────────────┬───────────────────────────────┘
                                  │
                ┌─────────────────▼───────────────────────────────┐
                │ [8] UPLOAD — YouTube Data API v3                │
                │   videos.insert (resumable) → captions.insert   │
                │   → thumbnails.set → videos.update (i18n)       │
                └─────────────────────────────────────────────────┘
```

---

## 5. Detalhamento por estágio

### [1] Roteiro — Claude API

Use a **Claude API** direto (não Claude Code) dentro do pipeline. Força saída JSON:

```python
import anthropic, json, random, yaml

client = anthropic.Anthropic()
premissas = yaml.safe_load(open("banco_premissas.yaml"))
p = random.choice([x for x in premissas if not x["usado"]])

SYSTEM = """Você escreve roteiros de sleep story em pt-BR.
Regras rígidas:
- 2ª pessoa, presente, ritmo lento, frases curtas
- sem clímax, sem conflito, sem diálogo, sem números
- densidade sensorial alta (tato, temperatura, som), visão baixa
- ~110 palavras/minuto de leitura falada
Responda SOMENTE com JSON válido, sem markdown, sem preâmbulo."""

msg = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8000,
    system=SYSTEM,
    messages=[{"role": "user", "content": json.dumps({
        "premissa": p["texto"],
        "duracao_narrada_min": p["duracao"],
        "estrutura": p["estrutura"],   # varia entre vídeos: jornada, ciclo, catálogo...
        "schema": {
            "titulo": "str",
            "titulo_i18n": {"en": "str", "es": "str"},
            "descricao": "str",
            "tags": ["str"],
            "paragrafos": ["str"],
            "prompt_imagem": "str",
            "paleta": "str"
        }
    })}]
)
roteiro = json.loads(msg.content[0].text)
```

Doc: <https://docs.claude.com/en/api/overview>

**Ponto crítico:** o campo `estrutura` é o que quebra o padrão de template. Mantenha
5–8 estruturas narrativas distintas e sorteie. Sem isso, o output vira template.

### [2] TTS — o item de maior custo recorrente

**Cálculo de volume.** Narração de sono roda a ~100–120 palavras/min. Palavra média
em pt-BR ≈ 6,5 caracteres com espaço.

```
60 min de narração × 110 wpm × 6,5 chars ≈ 43.000 caracteres/hora
```

**Comparativo de custo por 1 h de narração** (43k chars) `[SECUNDÁRIO]` — preços de
blogs comparativos de 2026, **confirme na página oficial antes de decidir**:

| Provedor / tier | US$/1M chars | Custo/1h narração | Observação |
|---|---|---|---|
| Google Standard | ~$4 | ~$0,17 | robótico demais para sono |
| Amazon Polly Standard | ~$4 | ~$0,17 | idem |
| Azure Neural | ~$16 | ~$0,69 | bom custo-benefício, muitas vozes pt-BR |
| Google Neural2 | ~$16 | ~$0,69 | |
| Google Chirp 3 HD | ~$30 | ~$1,29 | qualidade alta; relatos de lentidão em textos longos |
| ElevenLabs Flash/Turbo | ~$60 | ~$2,58 | |
| ElevenLabs Multilingual v2 / v3 | ~$120 | ~$5,16 | melhor qualidade expressiva |
| **Kokoro-82M (local, CPU)** | **$0** | **$0** | open-source, **inglês apenas** |

Fontes: <https://www.forasoft.com/blog/article/synthetic-voice-library-apps>,
<https://texttolab.com/blog/best-text-to-speech-api>,
<https://inworld.ai/resources/best-text-to-speech-apis>
Oficiais: <https://cloud.google.com/text-to-speech/pricing> ·
<https://elevenlabs.io/pricing> · <https://azure.microsoft.com/pricing/details/cognitive-services/speech-services/>

**Recomendação:** comece em **Azure Neural** ou **Google Chirp 3 HD** para pt-BR.
ElevenLabs só se testes A/B provarem que a expressividade retém mais público — em
conteúdo de sono, a expressividade importa menos que consistência e prosódia lenta.

**Detalhe que economiza um estágio inteiro do pipeline:** peça os **timestamps** ao
próprio TTS. ElevenLabs tem endpoint `with-timestamps`; Azure emite eventos de
`WordBoundary`. `[SECUNDÁRIO]` Com isso você gera o `.srt` **sem** rodar
alinhamento forçado nem Whisper. Ver seção [5].

### [3] Imagens

`[SECUNDÁRIO]` Faixa de preço 2026 por imagem:

| Modelo | US$/imagem |
|---|---|
| GPT Image 1 Mini | ~$0,005 |
| Imagen 4 Fast | ~$0,02 |
| FLUX.2 Pro | ~$0,03 |
| Imagen 4 Standard / GPT Image 1.5 | ~$0,04 |
| Imagen 4 Ultra | ~$0,06 |
| Gemini 3 Pro Image (4K) | ~$0,24 |
| SD / FLUX Dev auto-hospedado | <$0,01 (custo de GPU) |

Fontes: <https://awesomeagents.ai/pricing/image-generation-pricing/> ·
<https://www.digitalapplied.com/blog/ai-image-generation-api-pricing-comparison-2026>
Oficiais: <https://ai.google.dev/pricing> · <https://openai.com/api/pricing/>

**Para canal de sono você precisa de pouquíssimas imagens:** 1 background + 1
thumbnail por vídeo. Isso é **$0,08/vídeo**. Custo desprezível — pegue a qualidade
mais alta que couber (4K, para permitir Ken Burns sem perda).

`[FATO]` Google aplica marca d'água (SynthID) nas imagens geradas — relevante se
você planeja alegar autoria. <https://ai.google.dev/responsible/docs/safeguards/synthid>

### [4] e [5] Legendas multi-idioma — duas rotas distintas

Você tem **duas** opções no YouTube, e elas resolvem coisas diferentes:

| | Legendas (captions) | Faixas de áudio multi-idioma |
|---|---|---|
| O que é | texto `.srt`/`.vtt` por idioma | dublagem, áudio separado por idioma |
| API | `captions.insert` | **não exposta na Data API v3** — só via Studio `[FATO]` |
| Auto-dub do YouTube | — | gratuito, ativo por padrão em canais elegíveis `[SECUNDÁRIO]` |
| Limite | muitos idiomas | até ~30 faixas customizadas por vídeo `[SECUNDÁRIO]` |

`[FATO]` A dublagem multi-idioma **não gera áudio automaticamente** quando você sobe
faixa própria — você precisa produzir o áudio antes.
<https://support.google.com/youtube/answer/13338784>

`[SECUNDÁRIO]` O auto-dubbing do YouTube foi expandido a todos os criadores elegíveis
no início de 2026, com dezenas de idiomas, gratuito.

**Recomendação para o seu caso — legendas soft, nunca queimadas.**

Razão técnica, não estética: legenda queimada (hardsub) num vídeo de sono é
contraproducente — texto brilhante na tela atrapalha o objetivo do conteúdo, e
impede completamente a estratégia multi-idioma (você teria que renderizar N vídeos).
Legenda soft via `captions.insert` custa 1 render e serve N idiomas.

**Fluxo:**

```python
# 1) SRT pt-BR a partir dos timestamps do TTS (sem Whisper, sem alinhador)
#    Se o seu TTS não devolver timestamps, use alinhamento FORÇADO —
#    não transcrição. Você já tem o texto ground-truth.
#    Opções: stable-ts, WhisperX, aeneas, Montreal Forced Aligner.

# 2) Tradução do SRT preservando timing
for lang in ["en", "es", "fr", "de", "it", "ja"]:
    msg = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=16000,
        system=("Traduza o SRT para {}. Preserve EXATAMENTE numeração e timecodes. "
                "Traduza apenas as linhas de texto. Responda só com o SRT.").format(lang),
        messages=[{"role":"user","content": open("pt-BR.srt").read()}])
    open(f"{lang}.srt","w").write(msg.content[0].text)
```

Depois, `captions.insert` por idioma:
<https://developers.google.com/youtube/v3/docs/captions/insert>

> ⚠️ **Verifique o custo de quota do `captions.insert`** na calculadora oficial
> (<https://developers.google.com/youtube/v3/determine_quota_cost>) antes de
> dimensionar. Não confirmei esse valor nesta pesquisa e não vou chutar. Se for um
> método caro, 8 idiomas × N vídeos pode estourar a cota de 10.000 unidades/dia.

### [6] Render — FFmpeg

O truque que faz a diferença entre render de 40 min e render de 40 s.

**6a — mix de áudio com ducking, normalização e fade:**

```bash
ffmpeg -i narracao.wav -i ambiente.flac -filter_complex "\
[1:a]volume=0.28[amb]; \
[amb][0:a]sidechaincompress=threshold=0.06:ratio=5:attack=250:release=2000[duck]; \
[duck][0:a]amix=inputs=2:duration=longest:normalize=0[mix]; \
[mix]afade=t=out:st=10500:d=300,loudnorm=I=-18:TP=-2.0:LRA=7[out]" \
-map "[out]" -c:a aac -b:a 192k -ar 48000 mix.m4a
```

- `sidechaincompress` abaixa o ambiente **quando a narração fala** e devolve o volume
  no silêncio. É o que dá acabamento profissional. O 1º input é o comprimido, o 2º é
  o sidechain.
- `loudnorm=I=-18` — masteriza **abaixo** do alvo do YouTube (~-14 LUFS)
  deliberadamente. `[SECUNDÁRIO/HIPÓTESE]` O comportamento amplamente relatado é que
  o YouTube **atenua** conteúdo mais alto que o alvo mas **não amplifica** o mais
  baixo. Se isso se confirmar, masterizar a -18 mantém o vídeo naturalmente baixo,
  que é o desejado. **Teste com um vídeo antes de adotar como padrão.**

**6b — vídeo de 3 h SEM reencodar (o pulo do gato):**

```bash
# Renderize UM loop de 60 s com Ken Burns lento e GOP fechado
ffmpeg -loop 1 -framerate 30 -t 60 -i bg_4k.png \
  -vf "zoompan=z='min(zoom+0.00015,1.12)':d=1800:s=1920x1080:fps=30,format=yuv420p" \
  -c:v libx264 -preset slow -crf 20 \
  -g 60 -keyint_min 60 -sc_threshold 0 \
  -an loop60.mp4

# Concatena 180× = 3 h, com -c copy (custo de CPU ≈ zero)
python3 -c "open('list.txt','w').write(\"file 'loop60.mp4'\n\"*180)"
ffmpeg -f concat -safe 0 -i list.txt -c copy -an video3h.mp4
```

O `-g 60 -keyint_min 60 -sc_threshold 0` força GOP fechado e alinhado — sem isso o
concat com `-c copy` produz artefato nas emendas. `[FATO]`

**6c — mux final:**

```bash
ffmpeg -i video3h.mp4 -i mix.m4a \
  -c:v copy -c:a copy -shortest -movflags +faststart final.mp4
```

**Alternativa mais simples (imagem 100% estática):**

```bash
ffmpeg -loop 1 -framerate 24 -i bg.png -i mix.m4a \
  -c:v libx264 -preset veryfast -tune stillimage -crf 22 \
  -pix_fmt yuv420p -r 24 -c:a copy -shortest -movflags +faststart final.mp4
```

`-tune stillimage` faz o x264 comprimir frames idênticos a quase zero bits. Um vídeo
de 3 h estático em 1080p costuma sair na casa de **algumas centenas de MB**, não GB.
`[HIPÓTESE]` — depende do conteúdo; meça no seu caso.

### [7] e [8] Upload — YouTube Data API v3

**Este é o estágio com mais armadilhas. Leia antes de escrever código.**

#### 🚨 Armadilha nº 1 — o bloqueador do projeto

`[FATO]` **Todo vídeo enviado via `videos.insert` por um projeto de API não auditado,
criado depois de 28/07/2020, fica travado como PRIVADO.** Para liberar, o projeto
precisa passar por auditoria de conformidade com os Termos de Serviço.
<https://developers.google.com/youtube/v3/docs/videos>

`[FATO]` Vídeos travados como privados por esse motivo **não podem ser apelados**.
<https://support.google.com/youtube/answer/7300965>

**Isso significa:** se você não fizer a auditoria, seu pipeline "automatizado" vai
subir 100% dos vídeos como privados e você vai ter que tornar cada um público
manualmente pelo Studio. O que, ironicamente, é exatamente o gate manual que eu
recomendei na seção 2.2 — então trate isso como feature no MVP e faça a auditoria só
quando o canal estiver validado.

Formulário de auditoria/extensão:
<https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits>

#### Armadilha nº 2 — cota (informação desatualizada em toda parte)

`[FATO]` Documentação oficial atual: projetos com a YouTube Data API habilitada têm
alocação padrão de **100 chamadas `search.list`, 100 chamadas `videos.insert`, e
10.000 unidades/dia para os demais endpoints**.
<https://developers.google.com/youtube/v3/getting-started>

⚠️ **Fontes divergem sobre o custo de `videos.insert`.** Páginas em cache mostram
tanto "1 unidade no bucket Video Uploads" quanto "100 unidades", e praticamente todo
blog ainda repete o valor antigo de 1.600 unidades. `[SECUNDÁRIO]` Há relato de que
o custo foi reduzido em 04/12/2025. **Não tenho certeza de qual valor está vigente
hoje.** Consulte a calculadora oficial:
<https://developers.google.com/youtube/v3/determine_quota_cost>

**Na prática, nada disso te limita:** 100 uploads/dia >> 3 vídeos/semana. Seu gargalo
é a auditoria, não a cota.

#### Armadilha nº 3 — OAuth

`[FATO]` `videos.insert` exige OAuth 2.0 com escopo `https://www.googleapis.com/auth/youtube.upload`.
API key não serve.

`[SECUNDÁRIO]` Refresh tokens de apps com a tela de consentimento em modo **"Testing"**
expiram em ~7 dias. Para um cron semanal, isso significa reautenticar sempre.
**Publique o app** (mesmo sem verificação) para obter refresh token duradouro.
Verifique em: <https://developers.google.com/identity/protocols/oauth2>

#### Armadilha nº 4 — upload resumível

`[FATO]` Limite de 256 GB por arquivo. Mas o problema é a rede: um arquivo de
centenas de MB numa conexão residencial brasileira pode levar horas, e uma queda
reinicia tudo. **Use upload resumível** (`resumable=True` no `MediaFileUpload` da
lib Python) com `next_chunk()` em loop e retry com backoff exponencial.

```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

yt = build("youtube", "v3", credentials=creds)

body = {
  "snippet": {
    "title": roteiro["titulo"],
    "description": roteiro["descricao"],
    "tags": roteiro["tags"],
    "categoryId": "22",
    "defaultLanguage": "pt-BR",
  },
  "status": {
    "privacyStatus": "private",          # SEMPRE private no upload
    "selfDeclaredMadeForKids": False,
    "containsSyntheticMedia": True,      # ⚠️ confirmar nome exato do campo na doc
  },
}

req = yt.videos().insert(
    part="snippet,status",
    body=body,
    media_body=MediaFileUpload("final.mp4", chunksize=8*1024*1024, resumable=True),
)
resp = None
while resp is None:
    status, resp = req.next_chunk()
    if status:
        print(f"{int(status.progress()*100)}%")
```

> ⚠️ **`containsSyntheticMedia`**: não confirmei que este é o nome do campo na
> Data API v3. A divulgação de conteúdo sintético é garantida no Studio; via API
> pode não estar exposta. **Verifique em
> <https://developers.google.com/youtube/v3/docs/videos> e, se não existir, faça a
> divulgação manualmente no Studio como parte do gate.**

Depois do upload: `thumbnails.set`, `captions.insert` (por idioma) e `videos.update`
com `localizations` para títulos/descrições traduzidos.

---

## 6. Estimativa de custo

Cenário: **3 vídeos/semana ≈ 13/mês**, 60 min de narração + 2 h de ambiente cada,
6 idiomas de legenda.

| Item | Por vídeo | Por mês (13) |
|---|---|---|
| Roteiro (Claude Sonnet, ~10k tokens out) | ~$0,15 | ~$2 |
| TTS 43k chars @ Azure Neural (~$16/M) | ~$0,69 | ~$9 |
| Imagens (bg 4K + thumb) | ~$0,08 | ~$1 |
| Tradução de legendas × 6 idiomas | ~$0,20 | ~$3 |
| Áudio ambiente (gerado, FFmpeg) | $0 | $0 |
| Render (CPU local) | $0 | $0 |
| Upload / API YouTube | $0 | $0 |
| **Total** | **~$1,12** | **~$15** |

Trocando TTS para ElevenLabs Multilingual v2: ~$5,16/vídeo → **~$68/mês**.

`[SECUNDÁRIO]` Todos os valores derivam dos preços de blog citados na seção 5.
**A conclusão robusta não é o número, é a proporção: TTS domina o custo variável
(60–90%). É lá que a otimização vale a pena, não no resto.**

Custos não incluídos: energia/hardware, banda de upload, e o seu tempo de revisão —
que na arquitetura recomendada é o insumo mais caro do projeto.

---

## 7. Estrutura de repositório sugerida

```
canal-sono/
├── CLAUDE.md                    # contexto persistente p/ o Claude Code
├── config/
│   ├── banco_premissas.yaml     # VOCÊ escreve. é o ativo do canal.
│   ├── estruturas.yaml          # 5–8 arquétipos narrativos
│   └── vozes.yaml               # mapa idioma → voz TTS
├── pipeline/
│   ├── s1_roteiro.py
│   ├── s2_tts.py
│   ├── s3_imagens.py
│   ├── s4_legendas.py
│   ├── s5_render.py             # wrapper fino sobre ffmpeg
│   ├── s6_upload.py
│   └── orchestrator.py          # idempotente, retomável por etapa
├── state/
│   └── jobs.sqlite              # estado por vídeo: qual etapa concluiu
├── output/<slug>/
│   ├── script.json  narracao.wav  ambiente.flac  mix.m4a
│   ├── bg_4k.png  thumb.png  loop60.mp4  final.mp4
│   └── captions/{pt-BR,en,es,...}.srt
├── logs/
└── tests/
```

**Regra de ouro do `orchestrator.py`:** cada etapa checa se o artefato de saída já
existe e válido; se sim, pula. Isso torna o pipeline **retomável** — cai no meio do
upload, você roda de novo e ele só refaz o upload. É a diferença entre um pipeline
que você confia e um que você baby-sitta.

---

## 8. Roadmap sugerido

| Fase | Escopo | Objetivo |
|---|---|---|
| **0** | 3 vídeos **100% manuais** | Descobrir o que retém público. Sem isso, você automatiza o produto errado. |
| **1** | `s5_render.py` + `s2_tts.py` | Automatizar o trabalho mecânico. Ainda escreve roteiro à mão. |
| **2** | `s1_roteiro.py` + banco de premissas | Semi-automático com revisão obrigatória. |
| **3** | `s6_upload.py` (sempre `private`) + gate manual | Você só aperta "publicar". |
| **4** | Legendas multi-idioma | Só depois que o canal tem tração em pt-BR. |
| **5** | Auditoria da API do YouTube | Só quando o volume justificar. |

**Não pule a Fase 0.** O maior risco deste projeto não é técnico — é construir uma
fábrica muito eficiente de conteúdo que ninguém assiste e que o YouTube desmonetiza.

---

## 9. Skills e plugins que encontrei

Procurei no catálogo disponível. Resultado honesto:

- **Nenhuma skill específica** de vídeo/FFmpeg/YouTube existe no seu catálogo atual.
- **`postiz`** (plugin, não instalado) — CLI de automação de redes sociais com
  agendamento de posts, upload de mídia e analytics em 28+ plataformas incluindo
  YouTube. É o único item do catálogo diretamente relevante. Pode substituir o
  estágio [8] se você não quiser lidar com OAuth e cota você mesmo — ao custo de
  depender de terceiro para as credenciais do seu canal.
- **`Adobe for Creativity`** (plugin, não instalado) — ferramentas Creative Cloud
  para imagem/vetor/vídeo. Relevante só se você optar pelo caminho de editor de
  vídeo, que eu recomendo evitar.

Vale a pena criar uma skill própria (via `skill-creator`) encapsulando os comandos
FFmpeg e as convenções do seu pipeline, para o Claude Code não reinventar a roda a
cada sessão.

---

## 10. O que eu NÃO sei / precisa verificação

Lista explícita, para você não tomar decisão em cima de coisa que eu não confirmei:

1. **Custo de quota atual do `videos.insert`** — fontes conflitam (1, 100 ou 1.600
   unidades). Consultar a calculadora oficial.
2. **Custo de quota do `captions.insert`** — não verifiquei. Pode ser o gargalo real
   da estratégia multi-idioma.
3. **Campo de divulgação de conteúdo sintético na Data API v3** — não confirmei que
   existe. Pode ser exclusivo do Studio.
4. **API de scripting do DaVinci Resolve na versão gratuita** — fonte secundária diz
   que exige Studio; não confirmei na Blackmagic.
5. **Comportamento exato da normalização de loudness do YouTube** (atenua mas não
   amplifica) — amplamente relatado, nunca vi confirmação oficial.
6. **Expiração de refresh token OAuth em modo Testing** — documentado pelo Google,
   mas não reverifiquei a redação atual.
7. **Todos os preços de API** — são de blogs comparativos datados de 2026. Mudam
   rápido.
8. **Elegibilidade e lista de idiomas do auto-dubbing** — muda com frequência;
   verifique no seu próprio Studio, não em artigo.

---

## 11. Referências

**Claude Code / API**
- <https://code.claude.com/docs/en/scheduled-tasks>
- <https://code.claude.com/docs/en/routines>
- <https://code.claude.com/docs/en/cli-reference>
- <https://docs.claude.com/en/api/overview>

**YouTube — API**
- <https://developers.google.com/youtube/v3/getting-started>
- <https://developers.google.com/youtube/v3/docs/videos>
- <https://developers.google.com/youtube/v3/docs/videos/insert>
- <https://developers.google.com/youtube/v3/docs/captions/insert>
- <https://developers.google.com/youtube/v3/determine_quota_cost>
- <https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits>

**YouTube — políticas**
- <https://support.google.com/youtube/answer/1311392> (conteúdo inautêntico)
- <https://support.google.com/youtube/answer/14328491> (divulgação de conteúdo sintético)
- <https://support.google.com/youtube/answer/7300965> (vídeos travados como privados)
- <https://support.google.com/youtube/answer/6013276?hl=pt-BR> (Content ID)
- <https://support.google.com/youtube/answer/3376882?hl=pt-BR> (Biblioteca de Áudio)
- <https://support.google.com/youtube/answer/15577610?hl=pt-BR> (música sem restrições)
- <https://support.google.com/youtube/answer/13338784> (faixas de áudio multi-idioma)

**Ferramentas**
- <https://ffmpeg.org/ffmpeg-filters.html>
- <https://trac.ffmpeg.org/wiki/Concatenate>
- <https://resolvedevdoc.readthedocs.io/en/latest/API_intro.html>

**Cobertura secundária (política e preços)**
- <https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/>
- <https://www.auditsocials.com/blog/youtube-inauthentic-content-policy-2026-mass-produced-ai-generated-monetization-creators-brands>
- <https://www.forasoft.com/blog/article/synthetic-voice-library-apps>
- <https://texttolab.com/blog/best-text-to-speech-api>
- <https://awesomeagents.ai/pricing/image-generation-pricing/>
- <https://www.digitalapplied.com/blog/ai-image-generation-api-pricing-comparison-2026>
