---
projeto: Canal de Sono Automatizado
assunto: TTS pago — pesquisa para decisão de compra
data: 2026-09-04
status: pesquisa concluída; NADA contratado. Falta a prova cega.
---

# Voz paga: o que existe, quanto custa na nossa escala, e o que testar

> Reescrito em 04/09/2026 quando o Samuel decidiu pagar e pediu **vozes
> diferentes** e **inglês**. A versão anterior deste documento usava um volume
> errado — 15 mil caracteres por vídeo. O vídeo cresceu para 75 min e o número
> real é **34 mil**. Isso dobra a conta e muda qual plano serve.
>
> O contrato de escrita continua em [voz.md](voz.md) e não muda com o provedor.

## O nosso volume, medido

| | palavras | caracteres |
|---|---|---|
| video-02 (41 min) | 3.222 | 17.618 |
| video-03 (75 min) | 6.375 | **34.248** |

Como o formato agora é 75 min, **34 mil caracteres por vídeo** é a base. E o
inglês **dobra**, porque é roteiro reescrito, não tradução — decisão registrada
em [voz.md](voz.md).

| cadência | só pt-BR | pt-BR + inglês |
|---|---|---|
| quinzenal | 68 mil/mês | **137 mil/mês** |
| 1 por semana | 137 mil | **274 mil** |
| 2 por semana | 274 mil | **548 mil** |

A pesquisa de mercado ([mercado.md](mercado.md) §1) aponta para **cadência
baixa**: os dois canais de referência têm seis vídeos cada e ~80 mil inscritos.
Então a faixa realista é **137 a 274 mil caracteres/mês**.

---

## Os três candidatos, com o custo na nossa faixa

Câmbio de 04/09/2026: US$ 1 ≈ R$ 5,10. `[SECUNDÁRIO]`

| | preço | 137 mil/mês | 274 mil/mês | vozes | pt-BR |
|---|---|---|---|---|---|
| **Fish Audio** | US$ 15/milhão | **R$ 11** | **R$ 21** | 4.000+ | Tier 2, com localização pt-BR em 2026 |
| **Cartesia** Startup | US$ 49/mês, 1,25 M inclusos | **R$ 250** | **R$ 250** | clonagem instantânea | **Brasil é o locale PRIMÁRIO** |
| **ElevenLabs** Pro | US$ 99/mês, 600 mil | **R$ 505** | **R$ 505** | 4.000+ | um entre 70+ idiomas |

Duas observações que a tabela esconde:

**O Fish Audio cobra por uso, não por assinatura.** Nos nossos volumes ele sai
por menos que o plano fixo de US$ 15/mês deles. É de longe o mais barato, por
uma ordem de grandeza.

**O ElevenLabs não tem degrau útil.** O plano Creator (US$ 22, 121 mil) não
cobre nem a cadência quinzenal bilíngue. Quem sobe, sobe direto para o Pro.

---

## A qualidade: três alegações que se contradizem

| fonte | alega | credibilidade |
|---|---|---|
| Artificial Analysis Speech Arena, ago/2026 | **Cartesia Sonic-3.6 lidera as duas arenas** | terceiro independente, e é o dado mais recente |
| Fish Audio, teste cego de 10 dias, 71 mil comparações | **Fish S2 Pro vence 60%** contra o ElevenLabs | teste do próprio fornecedor sobre si mesmo |
| comparativos gerais | ElevenLabs lidera qualidade e clonagem | consenso repetido, sem número |

O teste do Fish Audio é grande e bem desenhado, **mas foi conduzido por eles
sobre o próprio produto**. Não desqualifica; pede desconto.

**E nada disso responde a nossa pergunta.** Essas arenas medem
predominantemente inglês. Continua valendo o que este documento já dizia:
qualidade em inglês não transfere para português — nasais, `ão`/`ãe`/`õe`, e a
palatalização de /t/ e /d/ antes de /i/ são exatamente onde TTS multilíngue
quebra.

O único sinal específico de pt-BR que apareceu é do Cartesia, e é de arquitetura,
não de marketing: **o Brasil é o locale primário do português** deles, com
"best-in-class pronunciations". Não é português herdado de Portugal.

---

## Vozes diferentes, que era o pedido

Hoje as 4 personas de `estudio/dados/personas.json` dividem **3 vozes** do
Kokoro. Duas personas usam a mesma (`pm_santa`), e isso foi decisão forçada, não
escolha.

| | como resolve |
|---|---|
| Fish Audio | biblioteca de 4.000+ vozes da comunidade |
| ElevenLabs | biblioteca de 4.000+ · clonagem profissional |
| Cartesia | **clonagem instantânea a partir de 3 segundos**, já no plano de US$ 5 |

A clonagem instantânea do Cartesia é a que dá mais controle: cada persona ganha
timbre próprio, e não um timbre sorteado de biblioteca compartilhada com
milhares de outros canais.

> **Cuidado de licença.** Clonar a voz de uma pessoa real exige autorização
> dela. O caminho limpo é clonar a partir de **voz sintética** já licenciada, ou
> gravar alguém que consinta por escrito. Isto é da mesma família da decisão que
> já tirou o XTTS-v2 do projeto: um canal automatizado não pode ter um estágio
> que morre por questão de direito.

---

## Recomendação

**Testar antes de assinar, e o teste é grátis.** Os três têm camada gratuita
suficiente para gerar o mesmo trecho:

| | camada grátis |
|---|---|
| Cartesia | 20 mil créditos (uso não comercial — serve para teste) |
| ElevenLabs | 10 mil créditos |
| Fish Audio | camada gratuita disponível |

O protocolo já está escrito em
[`fase0/_vozes-candidatas/README.md`](../fase0/_vozes-candidatas/README.md) e já
foi rodado uma vez, contra o Chatterbox. O que ele exige e que quase se perde:
**nivelar o loudness antes de comparar.** Na rodada anterior o Chatterbox saiu
10 dB mais alto que o Kokoro, e sem normalizar eu teria "descoberto" que ele era
melhor quando só estava mais alto.

O texto de teste é o da cena 2 do video-03, que contém `manhã` e `água` — as
duas palavras que o Samuel apontou como erradas no Kokoro. A pergunta deixa de
ser "qual voz é mais bonita" e passa a ser **"qual acerta o defeito que eu
ouvi"**.

### Se for para apostar sem testar

**Cartesia Startup, US$ 49/mês.** Motivos, em ordem:

1. Lidera o benchmark **independente** mais recente (ago/2026), e os outros dois
   sinais de qualidade são autodeclarados ou sem número.
2. **Brasil é o locale primário** do português — é o único sinal específico de
   pt-BR que apareceu em toda a pesquisa.
3. 1,25 milhão de caracteres cobre **qualquer** cadência nossa com folga, então
   o preço não muda se o canal acelerar.
4. Clonagem instantânea resolve o pedido de vozes diferentes com controle.

**O Fish Audio é 12× mais barato** (R$ 21 contra R$ 250 na cadência semanal) e
pode muito bem ganhar a prova cega. Se ganhar, é ele — a diferença de preço
paga um ano de fal.ai várias vezes.

**O ElevenLabs só se ganhar de ouvido por margem clara.** A R$ 505/mês ele
precisa provar que a diferença é audível **em português** e que ela se converte
em retenção — coisa que nenhum dado que eu achei demonstra.

---

## Para o inglês

Os três atendem, e o inglês é onde todos são mais fortes. A decisão de motor
provavelmente será a mesma dos dois idiomas, o que simplifica.

O que **não** simplifica, e está em [mercado.md](mercado.md) §6: a faixa em
inglês exige roteiro reescrito, não traduzido, com outra lista de tiques
(`delve`, `tapestry`, `testament to`). O custo do inglês é de escrita e de
julgamento, não de TTS — o TTS apenas dobra, e dobrar R$ 21 é irrelevante.

E vale lembrar o argumento que as consultas externas levantaram e continua de
pé: **em conteúdo de sono a voz é o produto.** Se a narração em inglês for ruim,
o canal não converte e não dá para saber se foi a voz, o roteiro ou o algoritmo.
Por isso a prova cega deveria ser feita **nos dois idiomas** antes de assinar.

---

Fontes `[SECUNDÁRIO]`:
[MarkTechPost — Sonic-3.6](https://www.marktechpost.com/2026/08/18/cartesia-ships-sonic-3-6-a-streaming-tts-model-that-now-leads-both-artificial-analysis-speech-arenas/) ·
[Cartesia Brasil](https://www.cartesia.ai/regions/brazil) ·
[TextToLab — preços Cartesia](https://texttolab.com/blog/cartesia-pricing) ·
[TextToLab — Fish vs ElevenLabs](https://texttolab.com/blog/fish-audio-vs-elevenlabs) ·
[Fish Audio — modelos](https://docs.fish.audio/developer-guide/models-pricing/models-overview) ·
[Gradium — comparativo 2026](https://gradium.ai/content/best-ai-voice-generators-2026)
