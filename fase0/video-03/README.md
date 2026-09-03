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
