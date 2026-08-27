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

## Estado

- [x] `plano.json` — 20 cenas, 1800 s, com prompt de imagem por cena
- [x] `estilo.yaml` — identidade visual travada
- [x] `roteiro.md` — 3.285 palavras, adaptação nossa
- [ ] Thumbnails — 3 variantes
- [x] Ambiente — chuva + mar procedurais, estéreo decorrelado (no `s5_render`)
- [x] Narração — Kokoro `pm_santa` 0.75, 25,4 min (`s2_tts`)
- [x] Mix + render (`s5_render`) — validado com placeholders
- [ ] Legendas (`s4_legendas`)
- [ ] **Imagens reais — único bloqueio**

## Registrar aqui depois de publicar

Retenção, ponto de abandono, e se as cenas duraram o certo (a sensação de "imagem
parada tempo demais" é o risco número um deste formato).


## Como gerar

```
python -m pipeline.s2_tts       fase0/video-02
python -m pipeline.s4_legendas  fase0/video-02
python -m pipeline.s5_render    fase0/video-02
```

Os scripts avulsos que existiam aqui foram absorvidos pelo `pipeline/`.
