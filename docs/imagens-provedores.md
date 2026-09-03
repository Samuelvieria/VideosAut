---
projeto: Canal de Sono Automatizado
assunto: geração de imagem — provedores, preço e recomendação
data: 2026-08-27
status: pesquisa de 27/08/2026 — a RECOMENDAÇÃO abaixo foi superada pelos fatos.
         Ver a nota no topo e docs/estado-e-direcao.md § custo.
---

# Geração de imagem: quanto custa e o que escolher

> **NOTA DE 03/09/2026 — leia antes do resto.** Este documento é da pesquisa de
> 27/08 e a decisão real divergiu dele em dois pontos:
>
> 1. **O caminho é a API da fal.ai, não auto-hospedar.** O Draw Things + SD 1.5
>    citado abaixo era o plano para o M2 sem GPU e nunca foi o caminho real.
> 2. **A resolução NÃO é 640×360.** Medido em 02/09: a fal.ai não entrega
>    dimensão abaixo de 512px num eixo — 640×360 voltava como 640×512, fora de
>    16:9, e o render cortava a cena em silêncio. É **1280×720**, escala
>    inteira **×2**. Onde este texto disser 640×360 ou ×3, está errado.
>
> O custo medido hoje é R$ 0,56–1,41 por vídeo. Ver
> [estado-e-direcao.md](estado-e-direcao.md).

> Todos os preços abaixo são `[SECUNDÁRIO]` — vêm de comparativos de terceiros
> datados de 2026. **Confirmar na página oficial do fornecedor antes de depender.**

## Volume real do projeto

| | |
|---|---|
| Imagens por vídeo | 20 cenas + 3 thumbnails = **23** |
| Vídeos por mês | 10–13 (cadência de 2–3/semana) |
| Imagens finais/mês | ~250–300 |
| Com retentativas (pixel art consistente pede ~2,5× por aproveitada) | **~700 gerações/mês** |

A conta que importa é a de **gerações**, não a de imagens finais. Estilo travado com
seed fixa reduz, mas não elimina, o descarte.

## Preço por imagem e custo mensal a 700 gerações

| Provedor / modelo | US$/imagem | US$/mês | Nota |
|---|---|---|---|
| **Z-Image-Turbo** (Alibaba Tongyi) — auto-hospedado | **0** | **0** | Apache 2.0; precisa de GPU |
| Z-Image-Turbo — API hospedada | ~0,005 | ~3,50 | mais barato do levantamento |
| GPT Image 1 Mini | ~0,005 | ~3,50 | |
| Ideogram 3.0 Turbo | ~0,03 | ~21 | |
| Seedream 5.0 Lite (ByteDance) | ~0,032 | ~22 | até 2048×2048 |
| Flux Pro | 0,04–0,06 | 28–42 | |
| GPT Image 1.5 / Imagen 4 Standard | ~0,04 | ~28 | |
| DALL·E 4 / Midjourney API | 0,03–0,20 | 21–140 | |

Agregadores (fal.ai, Replicate, Together, Fireworks) rodando modelos abertos ficam
na faixa de US$ 0,008–0,04. Fal.ai costuma sair mais barato que Replicate porque
cobra por imagem; o Replicate cobra por **segundo de GPU** (A100 80 GB a
US$ 0,0014/s), o que penaliza modelos lentos.

Você tinha razão sobre os chineses: o levantamento indica **30–70% mais barato que
Midjourney** para qualidade comparável.

## Recomendação

**Z-Image-Turbo, auto-hospedado na máquina nova.**

O motivo não é só preço — é a **licença Apache 2.0**, que permite uso comercial sem
amarra e sem depender de política de fornecedor. É a mesma lógica que já levou o
projeto ao Kokoro em vez do XTTS-v2 (CPML, proíbe comercial). Um canal automatizado
não pode ter um estágio que morre se um provedor mudar os termos.

E casa exatamente com a migração em curso: hoje o Draw Things + SD 1.5 é imposição
dos 8 GB de RAM. Com GPU, Z-Image-Turbo roda local, o custo de imagem vai a **zero**
e some a dependência de API do pipeline.

**Caminho prático:**

1. Prototipar as 20 cenas via **API hospedada** (~US$ 3,50/mês) enquanto a
   workstation não está pronta. Barato o suficiente para não valer otimizar.
2. Migrar para auto-hospedado assim que houver GPU.
3. Manter a API configurada como fallback — se a GPU estiver ocupada renderizando,
   o estágio de imagem não trava.

**Segunda opção, se a qualidade do Z-Image não convencer:** Seedream 5.0 Lite a
~US$ 22/mês. É o mais barato entre os que entregam 2048×2048 pronto para uso.
Irrelevante para nós — pixel art é gerado em 640×360 — mas relevante se o canal um
dia mudar de estilo visual.

**Descartado: Midjourney.** Melhor estética do mercado e sem API oficial. Vira
gargalo manual permanente, o que mata a Fase 1.

## O que NÃO muda com dinheiro

A resolução de geração continua **640×360**. É decisão estética: pixel art é
upscalado com `flags=neighbor` em escala inteira ×3. Provedor melhor gera melhor
composição naquele tamanho — não autoriza gerar em 1080p nativo, que produz
pseudo-pixel-art com grade inconsistente. Ver `fase0/video-02/estilo.yaml`.
