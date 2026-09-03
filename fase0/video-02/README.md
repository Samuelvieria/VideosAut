# Vídeo 02 — Moby Dick (30 min)

Primeiro vídeo do formato definitivo: **narração + sequência de cenas ilustradas**,
sem vídeo real. Se este sair bem e depois sair de forma automatizada, o caminho está
validado.

## Conceito

Um velho baleeiro aposentado, no cais, sob chuva, reconta a história do Pequod.
A moldura do velho **é nossa** — não está no livro. É ela que:

- cria obra original por cima de um texto em domínio público;
- justifica a persona da voz (`pm_santa`, masculina e idosa);
- dá abertura e fecho ao vídeo (cenas 1 e 19).

## PUBLICADO em 03/09/2026

https://www.youtube.com/watch?v=103_aYlJr4o  (`103_aYlJr4o`)

Primeiro vídeo do canal SleepPowder. Doze dias do primeiro roteiro até aqui.

Os números a acompanhar, em ordem de importância:

1. **Novos vs recorrentes** — só no Studio, a API não dá. É o ativo do nicho.
2. Retenção em 30, 60 e 90 s — diz se cortar a moldura funcionou.
3. Duração média **absoluta** — 11% de 41 min pode ser sucesso: a pessoa dormiu.
4. Origem do tráfego — busca é o único canal controlável partindo do zero.

## Estado (03/09/2026)

Pronto para publicar. Falta só render final e o upload manual.

- [x] `plano.json` — 20 cenas, 41,2 min, prompts e perfil de ambiente por cena
- [x] `estilo.yaml` — identidade visual travada, 1024×576 → janela 960×540 → ×2
- [x] `roteiro.md` — 3.467 palavras. **Moldura movida da abertura para o fecho**
- [x] Narração — Kokoro `pm_santa` 0.60, 32,2 min, 102 ppm, 19 cenas consistentes
- [x] Imagens — 20 em 1024×576
- [x] Ambiente — chuva + mar por cena, estéreo decorrelado
- [x] Legendas — `legendas.pt-BR.srt`, 313 blocos
- [x] Título, descrição, 16 tags, metadados de publicação
- [x] Thumbnail — `thumbnails/thumb_B.png` (o velho com a lanterna)
- [ ] **Render final** — refazer, tudo mudou desde o último
- [ ] **Upload manual** — ver checklist em `docs/monetizacao.md`

### Limitação conhecida

Cena 16, a baleia branca, sai **jubarte** e não cachalote. Seis tentativas,
quatro estratégias, incluindo a técnica que quatro consultas externas
convergiram. É viés de treino do Z-Image-Turbo, não erro de prompt. Saídas
registradas no `plano.json`: outro modelo só nessa imagem, ou img2img de gravura
em domínio público com denoising 0,30–0,55.

A thumbnail escolhida não tem baleia, então o problema não aparece no ativo mais
visível.

## Como gerar

```
python -m pipeline.s2_tts       fase0/video-02
python -m pipeline.s4_legendas  fase0/video-02
python -m pipeline.s5_render    fase0/video-02
```

Os scripts avulsos que existiam aqui foram absorvidos pelo `pipeline/`.

**Antes de renderizar na workstation:** `git pull`. Os últimos commits mudaram a
resolução das imagens, o alvo de duração e a abertura do roteiro. Sem eles a
cauda volta para 1 minuto e o corte come o rodapé das cenas.
