---
name: qualidade-producao-video
description: Lições de produção acumuladas no canal de sono automatizado (prompt de imagem, mixagem de áudio, movimento de câmera em pixel art) — problemas já resolvidos uma vez que não podem ser redescobertos a cada vídeo novo. Carregar ao escrever ou revisar prompts de cena em plano.json, ao mexer em pipeline/s3_imagens.py ou pipeline/s5_render.py, ou ao produzir/corrigir qualquer vídeo do canal.
---

# Qualidade de produção — canal de sono automatizado

Cada regra aqui custou uma rodada real de erro-e-correção no vídeo 2 (Moby Dick,
27/08/2026). O objetivo deste arquivo é não pagar esse custo de novo no vídeo 3,
4, 5... Quando uma regra deixar de valer (motor de imagem trocado, ffmpeg
atualizado), apague-a ou corrija-a — não deixe a lista virar folclore.

## Como formular um prompt de cena NOVO (checklist, antes de escrever)

Fórmula geral de prompt de imagem (Sujeito + Ação + Ambiente + Estilo +
Iluminação + Câmera + Detalhes) adaptada ao que `s3_imagens.py` já monta
automaticamente. Preencher cada campo de propósito em vez de escrever a
frase de uma vez — é isso que evita ficar vago ("legal", "dramático") em vez
de visual.

1. **Contexto narrativo** — `obra` + `personagem` + `titulo` da cena. Já é
   montado automaticamente pelo código (ver regra abaixo); só precisa
   preencher `personagem` no plano.json com uma frase curta e concreta.
2. **Sujeito** — quem/o quê está na cena, com qualquer traço físico raro
   (prótese, tatuagem, cicatriz) descrito de forma literal (ver regra
   "traço físico raro" abaixo) — nunca só o nome do objeto.
3. **Ação** — o que a figura está fazendo, um verbo concreto (segurando,
   sentado, remando), não um estado vago.
4. **Ambiente** — onde, com 2-3 elementos físicos concretos do cenário
   (não "um lugar assustador", e sim "capela vazia, bancos de madeira,
   luz cinza pelas janelas").
5. **Câmera/enquadramento — SEMPRE explícito, nunca acidental.** Decidir de
   propósito entre plano geral (a cena inteira, a figura de corpo inteiro),
   plano médio, ou close num detalhe específico — e escrever isso como a
   PRIMEIRA cláusula do prompt visual, não embutido no meio de uma frase
   sobre outra coisa.
   - Por quê: "close view of a tall gaunt sea captain's peg leg: ..." foi
     escrito como ênfase ("repara nessa perna"), mas o modelo tratou como
     instrução de enquadramento literal e cortou a cabeça de fora. Se o
     objetivo é mostrar um detalhe SEM sacrificar o corpo inteiro, escrever
     o enquadramento desejado primeiro ("full-length view from head to
     boots of...") e só depois descrever o detalhe dentro dessa cena maior.
   - Vocabulário útil: `full-length view` / `wide shot` (corpo/cena
     inteira), `close view` / `extreme close-up` (só quando for mesmo pra
     cortar o resto de propósito, como a cena 16), `at water level` /
     `from behind` / `low angle` / `bird's eye view` / `worm's eye view` /
     `rule of thirds` / `center-framed` (ponto de vista e composição).
6. **Iluminação/mood** — já vem em parte do `estilo_base` (paleta âmbar/azul
   escura), mas reforçar por cena o que é a FONTE de luz específica dessa
   cena (lanterna, lareira, luar, vela) ajuda o modelo a posicionar sombra
   e realce direito.
7. **Estilo** — não repetir por cena. Fica só no `estilo_base` (trocar ali
   quebraria consistência entre as 20 imagens).
8. **Detalhes finais** — textura/qualidade (grão de pixel, traço pintado)
   também já vêm do `estilo_base`; não precisa repetir por cena.

Se o resultado sair errado depois de seguir isso, **simplificar antes de
empilhar mais detalhe** — cortar o prompt pro sujeito+ação+câmera mínimos,
confirmar que aquilo sai certo, e só depois adicionar ambiente/luz de volta
uma coisa de cada vez. Enfiar mais adjetivo em cima de um prompt que já está
saindo errado raramente resolve.

**Corrigir mudando UMA variável por vez, não reescrevendo o prompt inteiro.**
Trocar só o enquadramento, ou só a seed, ou só uma frase — nunca as três
juntas — é o que permite saber qual mudança resolveu (ou qual reabriu outro
problema, ver regra de resolução acima). Foi assim que a cena 16 (baleia) se
resolveu: prompt igual, só a seed mudou.

**Prompt muito longo dilui a atenção no traço que importa.** A faixa prática
costuma ser ~30-60 palavras de descrição visual (fora o contexto
narrativo); prompts de uma frase só com 6+ cláusulas encadeadas (como o
"o velho no cais" original) tendem a deixar o primeiro ou o traço mais raro
com menos peso que o resto. Quando um traço sumir, considerar não só
reescrevê-lo de forma mais concreta (regra acima) mas também ENCURTAR o
resto do prompt, não só adicionar ênfase por cima.

**Se trocar a seed não resolver um viés persistente (raro, mas pode
acontecer), o próximo degrau é trocar de MODELO de geração, não insistir em
mais uma frase.** Diferentes modelos herdam vieses diferentes do próprio
conjunto de treino; hoje o pipeline está travado no Z-Image-Turbo via
fal.ai (`pipeline/s3_imagens.py`), então essa opção não está disponível sem
mudar `MODELO` e aceitar o custo de trocar de provedor — registrar aqui só
para não esquecer que existe, não para usar sem necessidade real.

## Prompt de imagem — regras que sempre valem

**Nunca nomear o que não se quer.** Difusão não processa negação: "a chuva parou"
contém "chuva" e o modelo desenha chuva. Descrever só o que EXISTE.

**Nunca nomear objeto quando se quer luz.** "lantern accents" no estilo base fazia
o modelo desenhar lanternas boiando em mar aberto. Descrever cor, não objeto.

**Gerar em 1280×720.** A fal.ai empurra qualquer dimensão abaixo de 512 para 512
sem avisar. 1280×720 é múltiplo inteiro do preset nativo (1024×576), é honrado, e
deixa 640×360px de margem para o `crop` deslizante do pan depois da escala ×2 —
sem margem não há movimento. Validar a dimensão recebida contra o que o render
assume (`s5_render._confere_fonte`).

**`enable_prompt_expansion: False`.** Ligado, o LLM do provedor reescreve o prompt
a cada chamada e destrói a consistência entre cenas.

**Viés de treino não se vence descrevendo mais forte.** "Baleia" puxa jubarte.
Sai-se pelo contexto histórico e pelo nome científico, não pela anatomia.

→ Detalhe, exemplos e o caso da baleia: `references/prompt-imagem.md`

## Movimento de cena / pixel art (`pipeline/s5_render.py`)

**Nunca Ken Burns/zoompan contínuo em pixel art.** Reamostra em subpixel e
borra a grade. Único caminho seguro: `crop` (seleção de pixel, nunca
reamostra) numa janela que escala pro tamanho final por um FATOR INTEIRO
exato, seguido de `scale=...:flags=neighbor`.

**Pra abrir margem de movimento sem cortar a composição: gerar a imagem
MAIOR que o quadro visível, não a janela de corte MENOR.**
- Por quê: cortar 480×270 de uma imagem de 640×360 (pra caber 960×xxx→1920
  por escala ×4) ampliava o pixel (bloco 4×4) E cortava enquadramento
  pensado pro quadro cheio. Gerar em 768×432 e recortar sempre 640×360
  (parado, centralizado; em movimento, deslizando nos 128×72px de margem) e
  escalar ×3 preserva a densidade de pixel original E a composição inteira.
- Como aplicar: a resolução de geração É a resolução visível + margem, nunca
  um corte menor que o pretendido.

**Movimento lento e "travado" não é causado pelo passo ser inteiro — é
causado pela TAXA de atualização ser baixa demais.**
- Por quê: deslizar 128px ao longo de uma cena de 80-130s dá 1 passo a cada
  ~0,8s, que lê como "parado, depois pula" em vez de fluido.
- Como aplicar: desacoplar o período do movimento da duração da cena — usar
  um vaivém de período curto e FIXO (ex.: 40s) via seno, não um percurso
  linear que varre a cena inteira uma vez só. Seno também evita o solavanco
  de direção nas pontas que um triângulo/ping-pong linear teria.

## Mixagem de áudio — regras que sempre valem

**Conteúdo de sono quer dinâmica plana.** O ambiente é cobertor acústico contínuo
e nunca pode sumir sob a voz. É o oposto da regra de podcast.

**A relação voz/ambiente importa mais que o LUFS integrado**, porque a
normalização do YouTube é de ganho global e a razão sobrevive a ela.

**Reusar label de filtro falha se houver vídeo no mesmo filtergraph.** Usar
`asplit` explícito.

**Ambiente é sintetizado, nunca gravado** (`pipeline/ambiente.py`). Não é escolha
estética: som gerado é a única fonte que o Content ID não consegue casar. E o mar
é feito de **eventos de onda**, não de ruído com modulação de amplitude — ruído
modulado soa pulsando, não rebentando.

**Ambiente é por CENA, não trilha única.** A troca acontece no mesmo instante do
fade para preto, então soa intencional em vez de soar como corte.

**`ambiente_reverb` fica em 0.** O eco no ambiente foi a causa da granulação na
cauda — cinco hipóteses medidas falharam antes, e quem achou foi o ouvido. Se
alguém subir esse valor, tem que ouvir a **cauda**, onde não há voz mascarando.

**Correção achada num vídeo tem que subir para o padrão do código, não ficar só
como override no `plano.json`.** Foi exatamente assim que a granulação voltou: a
correção ficou no plano do video-02, o `MIXAGEM_PADRAO` continuou errado, e o
video-03 herdou o defeito e só foi descoberto depois de renderizado.

→ Cadeia completa, valores medidos, síntese do ambiente e o debate de LUFS:
`references/mixagem-audio.md`

## Não fugir da ideia que a obra tem

**Filosofia não é o narrador ser sábio — é o episódio encarar o que o assunto
levanta.** Em 05/09/2026 o roteiro do video-04 passava duas horas sem dizer por
que quarenta pessoas estavam atravessando o deserto: eu tinha posto Sykes-Picot
"fora de quadro" e com isso tirei a razão da história.

**O tell:** quando o narrador anuncia que está se recusando a contar alguma
coisa, a covardia já está na página.

A distinção: **fato documentado com data é história; atribuir culpa hoje é
opinião.** Dizer que a promessa é de 1915 e o acordo de repartição é de 1916 não
toma partido. Dizer quem foi vilão, sim.

Verificação obrigatória em roteiro novo: **ele diz POR QUE as pessoas fazem o
que fazem?** Se não diz, falta o principal. Detalhe em [`docs/roteiro.md`](../../../docs/roteiro.md) §2.

## O que faz dormir — a regra que vem antes das outras

**O sono vem da ENTREGA, não do enredo.** História boa contada devagar faz
dormir; história sem nada em jogo só é chata.

Um aviso de "isto pode acordar o ouvinte" sobre um ACONTECIMENTO quase sempre
está errado — vale sobre a entrega (grito, estouro, aceleração, vinheta, pedido
de inscrição), não sobre o conteúdo. Em 05/09/2026 eu amaciei cinco passagens
do video-04 por causa de uma lista dessas, e quatro eram as melhores do
roteiro. Detalhe e exemplo em [`docs/roteiro.md`](../../../docs/roteiro.md) §1.

**E não anunciar o que a história não tem.** "Não tem batalha, não tem herói" é
pedir desculpa pelo produto nos 90 segundos em que o espectador decide ficar.

## Ritmo de narração — regras que sempre valem

**Quem controla o ritmo é o TAMANHO DA FRASE, não o parâmetro de pausa.**
Achado em 05/09/2026 com o Chirp3-HD: a marca `[pause]` cai em fim de frase,
então roteiro de frase curta recebe mais pausas por palavra e sai mais lento.

| | marca a cada | ppm medido |
|---|---|---|
| video-03 | 6,8 palavras | 124–127 |
| video-04 | 9,7 palavras | **141** |

Projetar o video-04 pelos 127 do video-03 errou **11 minutos**. O padrão do
estúdio passou a ser 135, que é o meio da faixa — e a projeção honesta só
existe depois do `s2_tts`, que grava o `duracoes.json` com o número real.

**Consequência para quem escreve:** existem DOIS controles de duração, não um.
Mais palavras alonga; frase mais curta também alonga. E frase curta é o que o
contrato de voz já pede por outro motivo.

**Ritmo lento vem de PAUSA maior, não de `speed` baixo.** `speed` baixo estica a
articulação e degrada a pronúncia — verificado transcrevendo o áudio de volta.

**O Kokoro ignora reticências.** A pausa é inserida por código, cortando o texto
e emendando silêncio.

→ Valores, medições e o mecanismo: `references/ritmo-narracao.md`

## Processo

**Verificação técnica (LUFS, espectro, frame extraído) não substitui ouvir/
assistir de verdade.** É a melhor aproximação disponível quando não há
alguém revisando ao vivo, mas sempre que possível prefira uma ferramenta que
deixe o humano ouvir e ajustar direto (ver mixer em `estudio/`) a decidir
parâmetro de áudio/vídeo só por número.

**Ao corrigir algo, verificar se a correção não reabre um problema já
resolvido em outro lugar** (ex.: o contexto narrativo que resolveu o Ahab
quase estragou a baleia). Regenerar e checar visualmente/tecnicamente antes
de dar como certo, mesmo quando a mudança parece isolada.
