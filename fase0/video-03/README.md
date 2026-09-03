# Vídeo 03 — A Luz da Baía Quieta (30 min)

Segundo episódio do formato definitivo. Diferente do video-02: **história
original**, não adaptação de obra existente — de propósito, pra fugir de
histórias muito difundidas (mitologia grega, épicos conhecidos).

## Conceito

Demétrio, um velho contador de histórias grego (persona `filosofo-grego`,
voz `pm_alex`), narra uma noite específica da própria juventude como
guardião de um farol numa ilha pequena — tende o fogo, pensa no filho
(Míron) que foi pro mar há anos, vê dois navios passarem em segurança na
baía. Sem deuses, sem monstros, sem batalha — só um homem, um fogo, e uma
baía quieta.

## Estado

- [x] `roteiro.md` — 2.147 palavras, história original, 20 cenas narradas + 1 cauda
- [x] `plano.json` — 21 cenas, 1800s alvo, prompt de imagem por cena
- [x] `estilo.yaml` — identidade visual (mesma base do canal, ambientação grega)
- [ ] **Roteiro em revisão humana — não rodar TTS/imagens até aprovar**
- [ ] Narração (`s2_tts`) — voz `pm_alex`/0.95 nunca foi calibrada por ouvido
- [ ] Imagens (`s3_imagens`)
- [ ] Mix + render (`s5_render`)
- [ ] Legendas (`s4_legendas`)
- [ ] Thumbnails

## Como gerar (depois da revisão do roteiro)

```
python -m pipeline.s2_tts       fase0/video-03
python -m pipeline.s3_imagens   fase0/video-03
python -m pipeline.s5_render    fase0/video-03
python -m pipeline.s4_legendas  fase0/video-03
```

## Correções de prompt aplicadas em 03/09/2026

O plano veio da outra máquina montado a partir do template de **antes** das
correções do video-02. O `s3_imagens --seco` pegou três regressões antes de
gastar um centavo:

1. `estilo_base` tinha `painterly game background art` — o cue que escreveu
   "Moby-Dolk" na tela do video-02. Removido.
2. `estilo_base` fixava `at night`, contradizendo a cena 6 (memória diurna),
   a 20 e a 21 (amanhecer). Removido — as 21 cenas já trazem a própria luz.
3. `obra` estava em português e com negações (`sem deuses, sem monstros`), que
   em prompt positivo pedem o que negam. Reescrito em inglês, sem o título
   original, que não carrega informação visual e só arrisca virar texto na tela.

As quatro regras que saíram disso estão em
`.claude/skills/qualidade-producao-video/references/prompt-imagem.md`.
