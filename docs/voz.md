---
projeto: Canal de Sono Automatizado
assunto: contrato de voz para roteiros
data: 2026-09-03
base: medição do roteiro do vídeo 02 (3.467 palavras, 294 frases)
---

# Voz

Não é descrição de estilo — é **contrato verificável**. Todo roteiro novo, em
qualquer idioma, tem que passar nestes números antes de virar áudio.

As regras foram extraídas medindo o roteiro do vídeo 02, que já foi aprovado de
ouvido. Elas descrevem o que ele **é**, não o que eu gostaria que fosse.

## Ritmo de frase — a regra que mais importa

| faixa | alvo | vídeo 02 |
|---|---|---|
| fragmento (1–4 palavras) | 18–26% | 22% |
| curta (5–10) | 30–40% | 35% |
| média (11–20) | 25–33% | 29% |
| longa (21+) | ≤ 16% | 14% |

**Mediana de 9 palavras. 57% das frases com 10 palavras ou menos.**

É isso que produz o ritmo de fala. Um roteiro com mediana 15 lê bem no papel e
soa como locução de documentário — errado para dormir.

Frase acima de 25 palavras é permitida, mas precisa de marca de respiração
(`...`) num ponto de pausa. O `s2_tts` corta ali e insere o silêncio.

## Começar frase com "E"

45 das 294 frases começam com **"E"** — 15%. Não é descuido, é o marcador oral
mais forte do texto. Fala encadeia; escrita subordina.

Manter. Um revisor de gramática vai querer tirar; não deixe.

## Concretude

As 14 palavras de conteúdo mais frequentes do roteiro:

> navio, água, ficou, lado, homens, homem, coisa, anos, noite, cima, ninguém…

**Todas concretas.** Nenhum substantivo abstrato entra no top 14. Não há
"esperança", "destino", "solidão", "obsessão" — os temas existem, mas aparecem
por objeto e ação, nunca nomeados.

Regra: se o ouvinte não consegue ver, ouvir ou tocar a palavra, ela precisa
justificar sua presença.

## Tempo verbal

Pretérito perfeito (130) alternando com imperfeito (113), quase meio a meio. O
perfeito move a ação, o imperfeito segura a cena. Presente só na moldura.

## Pessoa

Vídeo 02 usa 2ª pessoa só 4 vezes e 1ª pessoa 6 vezes em 3.467 palavras — é
narrativa em 3ª pessoa, com a voz do narrador aparecendo apenas no fecho.

**Isso é escolha por vídeo, não regra do canal.** O roteiro da cabana (vídeo 01)
era 2ª pessoa do início ao fim, e estava certo para aquele formato. Sleep story
de imersão pede "você"; reconto de obra pede 3ª pessoa. Decidir antes de
escrever e não misturar dentro do mesmo vídeo.

## Termos banidos

O roteiro do vídeo 02 tem **zero ocorrências** dos 19 termos abaixo. Manter em
zero:

```
mergulhar (fig.)   jornada           transformador     é importante notar
vale ressaltar     não se trata      em suma           por fim
além disso         profundamente     verdadeiramente   essencialmente
crucial            fundamental       impactante        no entanto
portanto           dessa forma       ou seja
```

Os quatro últimos merecem nota: são conectivos corretos em português escrito e
**errados em fala**. Quem conta história diz "e", "aí", "mas" — não "portanto"
nem "dessa forma".

## Estruturas proibidas

- **Tricolon de adjetivos abstratos** — "sombrio, implacável e eterno". Um
  adjetivo concreto vale mais que três abstratos.
- **Pergunta retórica.** Ativa processamento, é o oposto do objetivo.
- **Antítese de fecho** — "não era X, era Y". Tique de LLM e de LinkedIn.
- **Enumeração com dois pontos** seguida de lista. Escrita, não fala.

## Como verificar um roteiro novo

```bash
python3 - <<'PY'
import re, statistics as st
t = open("ROTEIRO.md", encoding="utf-8").read()
c = "\n".join(l for l in t.split("\n") if not l.startswith(("#", ">", "-")))
p = " ".join(c.split())
fr = [f for f in re.split(r"(?<=[.!?])\s+", p.replace("...", "<R>")) if f.strip()]
n = [len(f.split()) for f in fr]
print(f"mediana {st.median(n):.0f} (alvo 8-10) | <=10 palavras: {100*sum(1 for x in n if x<=10)/len(n):.0f}% (alvo 55-62%)")
print(f"comeca com E: {100*sum(1 for f in fr if f.lower().startswith('e '))/len(fr):.0f}% (alvo 12-18%)")
banidos = "mergulh|jornada|transformador|é importante notar|vale ressaltar|não se trata|em suma|por fim|além disso|profundamente|verdadeiramente|essencialmente|crucial|fundamental|impactante|no entanto|portanto|dessa forma|ou seja"
print(f"termos banidos: {len(re.findall(banidos, p, re.I))} (alvo 0)")
PY
```

## Para a versão em inglês

O contrato traduz, os números não mudam: mediana de 9 palavras, 57% com 10 ou
menos, começar frase com "And", vocabulário concreto.

A lista de banidos é outra. Em inglês os tiques são `delve`, `tapestry`,
`testament to`, `navigate the complexities`, `it's worth noting`, `in the realm
of`, `furthermore`, `moreover`.

E a adaptação **não é tradução**. O texto em português foi escrito para ser
falado em português; traduzido vira prosa engessada — especialmente irônico num
livro cujo original é inglês. Reescrever a partir da mesma estrutura de 19 cenas.

---

Método convergente de duas fontes independentes: o post de RanTheBuilder sobre
escrever na própria voz e o repositório `tenfoldmarc/script-skill`. Ambos
prescrevem extrair um documento de voz, manter lista de banidos e fazer passada
de de-AI. A diferença aqui é que os números saíram de medição do nosso texto, não
de intuição.
