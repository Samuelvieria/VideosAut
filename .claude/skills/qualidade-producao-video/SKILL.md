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

## Prompt de imagem (fal.ai Z-Image-Turbo, `pipeline/s3_imagens.py`)

**A fal.ai não entrega dimensão abaixo de 512 — ela empurra para 512 sem
avisar, e a resposta traz o tamanho REAL, não o pedido.** Medido em
02/09/2026: pedir 640×360 devolvia 640×512 (razão 1,25) e pedir 768×432
devolvia 768×512 (razão 1,50) — nenhum dos dois em 16:9, apesar de o prompt
dizer "16:9". Gerar em **1024×576** (o preset `landscape_16_9` do próprio
modelo), que é honrado.

Isso passou despercebido por semanas porque nada conferia o tamanho recebido:
o `s5_render` assumia fonte 768×432 e recortava 640×360 em `y=36`, comendo em
silêncio os 116px de rodapé de toda cena. **Sempre validar a dimensão da
imagem contra o que o render assume** — `s5_render._confere_fonte` faz isso e
aborta. Errar alto é melhor que entregar 30 min com composição cortada.

**NUNCA nomear o que não se quer — modelo de difusão não processa negação.**
"a chuva parou" contém a palavra "chuva" e o modelo desenha chuva. Medido na
cena 19 do vídeo 2 (3 tentativas). Z-Image-Turbo não aceita
`negative_prompt`, então a única defesa é descrever só o que EXISTE na cena
("céu claro, madeira seca" em vez de "a chuva parou"). Confirma com a regra
geral de "positive framing" de qualquer guia de prompt de imagem: escrever
"rua vazia", nunca "rua sem carros".

**Contexto narrativo (obra + personagem + cena) ANTES da descrição visual
ajuda a reter o traço que define um personagem.**
Formato: `{obra}, {personagem}, scene: {titulo}. {estilo_base}, {prompt visual}`.
- Por quê: sem isso, a perna de marfim entalhada do Ahab sumiu duas vezes
  seguidas — o traço raro perdia pra descrição genérica do resto da cena.
  Nomear "Captain Ahab" antes resolveu de vez.
- Como aplicar: usar sempre que a cena tiver um personagem com traço físico
  incomum que precisa aparecer (prótese, tatuagem, cicatriz, deformidade).

**Mas o mesmo contexto narrativo pode REATIVAR um clichê de treino quando o
prompt visual já foi ajustado à mão pra fugir dele.**
- Por quê: nomear "the white whale" na cena 16 trouxe de volta a pose de
  salto completo (jubarte) que o prompt visual ("extreme close view of a
  vast wall of forehead breaking the surface") já evitava. Mesmo problema
  apareceu na cena 11 (a caça) mesmo sem nomear a baleia no contexto — o
  próprio prompt genérico "breaking the surface" já é suficiente pra puxar
  o viés.
- Como aplicar: se uma cena tem uma nota tipo "N tentativas saíram erradas,
  mudar a pose resolveu" — trate isso como sinal de que o prompt já é
  cirúrgico contra um viés específico. Nesse caso desligue o contexto
  narrativo pra essa cena (`"contexto_narrativo": false` no plano.json) e
  descreva a presença do elemento problemático de forma restrita e concreta
  (ex.: "only a low dark curved back and small puff of spray... mostly
  submerged", nunca só "breaking the surface" sozinho).

**Traço físico raro (prótese, tatuagem, anatomia incomum): descrever de
forma literal e concreta, não pelo nome comum do objeto.**
- Por quê: "a peg leg" sumiu do resultado repetidamente. "A carved wooden
  prosthetic leg shaped like a table leg with turned ridged rings, made of
  pale bone-white ivory, ending in a rounded tip planted into a hole in the
  deck" funcionou de primeira.
- Como aplicar: sempre que um traço definidor sumir 2x, pare de nomear o
  objeto e descreva a forma/textura/cor física dele.

**Cena com dois focos complexos ao mesmo tempo (ex.: navio afundando E
personagem sendo arrastado) o modelo não compõe bem.**
- Como aplicar: reduzir um dos dois a detalhe/silhueta de fundo, deixar só
  um foco dominante e concreto.

**Nunca empilhar duas instruções "close view of X" no mesmo prompt.**
- Por quê: confunde o enquadramento — testado e deu corte que não mostrava
  nem um nem outro assunto direito.

**`[ITEM NÃO VERIFICADO]` Consistência de personagem entre cenas via imagem
de referência (img2img), não só texto — possível melhoria futura, não
testada aqui.** Guias gerais de prompt de imagem (Nano Banana, OpenArt)
recomendam anexar imagem de referência quando precisão de identidade
importa, em vez de só descrever em texto. Isso já existe como conceito no
projeto (`docs/fontes-imagens.md`, `uso: referencia_img2img` pra imagens
históricas), mas `pipeline/s3_imagens.py` hoje manda só texto pro fal.ai —
não confirmei se o endpoint `fal-ai/z-image/turbo` aceita imagem de entrada.
Vale investigar se a consistência de um personagem recorrente (ex.: Ahab em
3+ cenas) virar problema real num próximo vídeo, antes de assumir que dá.

**Mesmo prompt + mesma seed = mesma imagem SÓ na mesma resolução.** Mudar
`LARG`/`ALT` de geração (ex.: 640×360 → 768×432 pra abrir margem de pan)
muda a grade de ruído e pode alterar composição mesmo com prompt e seed
idênticos — não é garantia de estabilidade entre resoluções diferentes.
- Por quê: ao mudar a resolução de geração (ver seção de movimento abaixo),
  3 cenas já corrigidas quebraram de novo sem eu ter tocado nos prompts
  delas: a cena 5 perdeu a figura sentada na capela, a cena 9 (Ahab) virou
  um close sem cabeça porque o prompt abria com "close view of...the peg
  leg" — instrução que era só ênfase em 640×360 virou enquadramento literal
  na resolução nova — e a cena 16 (baleia) voltou a saltar inteira apesar do
  prompt anti-viés continuar igual.
- Como aplicar: **depois de qualquer mudança na resolução/tamanho de
  geração, reveja as 20 imagens de novo, não só as que mudaram de prompt.**
  Pra recompor sem reescrever a cena inteira: (1) trocar frases tipo "close
  view of X:" que descrevem um objeto usando uma instrução de enquadramento
  ambígua — prefira "full-length view from head to boots" quando o objetivo
  é manter a figura inteira visível; (2) se o prompt já está correto e ainda
  assim voltou o resultado errado, mudar só a seed daquela cena
  (`"seed_de": <número arbitrário>` no plano.json) antes de reescrever o
  prompt de novo — resolveu a baleia depois de 3 tentativas de frase
  falharem.

Dentro da MESMA resolução, prompt+seed seguem determinísticos — útil pra
testar uma mudança de frase isolada sem variar o resto.

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

## Mixagem de áudio (`pipeline/s5_render.py::mixar`)

**Alvo de masterização final: -14 LUFS integrado / -1 dBTP, não -18.**
Mudou em 28/08/2026, com motivo novo (pesquisa de mercado, sem norma oficial
pra sono especificamente — ver referências no fim desta seção).
- Por quê: o YouTube normaliza TUDO pra -14 LUFS na entrega. Se o vídeo
  chega mais baixo, o espectador sobe o volume do APARELHO pra compensar —
  e leva um susto no próximo vídeo/anúncio (normalizado em -14, tocando bem
  mais alto que o volume que ele ajustou). Quem deve decidir "quão baixo" é
  o volume do aparelho do ouvinte, não o master. O conforto do formato vem
  de faixa dinâmica ESTREITA (LRA 3-6 LU), não de nível baixo.
- Como aplicar: ver `MASTER_I`/`MASTER_TP`/`MASTER_LRA` em `s5_render.py`.

**O `TP` pedido ao `loudnorm` tem que ficar ABAIXO do teto real desejado —
mesmo em 2 passos linear, ele overshoot.** Teto real do checklist de
publicação é -1,0 dBTP; `MASTER_TP` no código é **-1,5**, não -1,0.
- Por quê: medido no video-02 em 28/08/2026 — pedir `TP=-1.0` mediu -0,88
  dBTP no arquivo final (passou do teto). Pedir `TP=-1.5` mediu -1,40 dBTP
  de verdade, com margem. O overshoot ficou em ~0,1-0,4dB nos dois testes —
  não é bug de configuração, é imprecisão normal do limitador do loudnorm.
- Como aplicar: nunca configurar `TP` no `loudnorm` igual ao teto real que
  você precisa respeitar — sempre com ~0,5dB de colchão. Depois de qualquer
  mudança em `MASTER_TP`, medir o `final.mp4` de verdade com
  `ffmpeg -i final.mp4 -af loudnorm=print_format=json -f null -` e confirmar
  `input_tp` abaixo do teto, não confiar no valor pedido.

**`loudnorm` de 1 passo (modo dinâmico, o padrão) NUNCA pode ser o último
filtro do mix somado — usar 2 passos com `linear=true` pro alvo final.**
- Por quê: o modo dinâmico reage à loudness corrente e reinfla o volume
  geral (ambiente incluso) sempre que a soma fica baixa, desfazendo
  qualquer calibração de `ambiente_ganho` feita antes. `linear=true` aplica
  só um OFFSET fixo (medido antes, numa passada de análise) — preserva a
  relação voz/ambiente que o resto da cadeia já calibrou.
- Como aplicar: passo 1, roda `loudnorm=I=X:TP=Y:LRA=Z:print_format=json`
  em `-f null -` pra pegar `input_i/input_tp/input_lra/input_thresh` do
  stderr; passo 2, roda de novo com esses 4 valores em
  `measured_I=.../measured_TP=.../measured_LRA=.../measured_thresh=...:linear=true`.
  Ver `_masterizar_2passos()`. Isso é DIFERENTE do "leveler" de voz sozinha
  (`loudnorm=I=-18:...` dinâmico, sem `linear`, dentro do filtro complexo) —
  aquele mantém a voz consistente cena a cena; este aqui é só a
  masterização final, roda uma vez no arquivo já pronto.

**Pra medir o gap voz/ambiente de verdade, isolar cada stem SILENCIANDO O
OUTRO — nunca medir o mix combinado com um lado mudo.**
- Por quê: o gate relativo do BS.1770 (-10 LU abaixo da média não-gateada) é
  dominado por quem for mais alto. Se a voz for bem mais alta que o
  ambiente (o caso normal), silenciar o AMBIENTE e medir o mix não muda o
  `I:` medido — a voz sozinha já dominava a métrica antes, então o teste
  não prova nada sobre o ambiente. Medido em 28/08/2026: com
  `ambiente_ganho` em 0.1 e depois 0.42, silenciar o ambiente deu -17,0/
  -17,1 LUFS nos dois casos — parecia confirmar que o ambiente não
  importava, mas na verdade só confirmava que a voz dominava o gate.
- Como aplicar: pra medir o ambiente sozinho, silencie a VOZ
  (`voz_ganho=0`) e meça o `mix_bruto` (arquivo pré-masterização, antes do
  `loudnorm` final — a masterização final sempre normaliza pro mesmo alvo
  então mascara a diferença). O gap real = `I` da voz sozinha − `I` do
  ambiente sozinho, os dois medidos como sinal ISOLADO, nunca a diferença
  dentro do mix somado.

**O cálculo de ganho a partir do arquivo BRUTO (sem processar) subestima
quanto os filtros de EQ tiram depois — meça no sinal já processado.**
- Por quê: `ambiente.wav` cru mede -23,7 LUFS; um cálculo ingênuo pra bater
  ~13dB de gap da voz (~-17,75 LUFS processada) sugeria `ambiente_ganho`
  ≈0,42. Medido de verdade (sinal isolado, já com highpass, dip 1-4kHz e
  lowpass aplicados): 0,42 dava só ~-38,9 LUFS, um gap de ~21dB — os cortes
  de EQ tiram mais energia do que a matemática em cima do arquivo cru
  prevê. `ambiente_ganho=1,0` foi o valor que bateu ~13,6dB de verdade.
- Como aplicar: calibrar por tentativa medida (isolar+medir, ajustar,
  medir de novo), nunca só por conta de cabeça a partir do arquivo de
  entrada — o ganho "no papel" e o ganho real depois da cadeia de filtros
  podem divergir bastante.

**Ducking pra sono: redução pequena (4-6dB) e devagar (release 1,5-3s),
não redução forte e rápida.**
- Por quê: ducking forte+rápido fica audível como "evento" (o ambiente
  visivelmente subindo e descendo, "bombeando"); pra sono o objetivo é que
  o ouvinte nunca perceba o ambiente reagindo. Isso é o OPOSTO do que a
  correção anterior (release curto, ver `duck_release_ms`) resolveu — mas
  não contradiz: aquela correção era necessária porque a config antiga
  tinha ganho ALTO + ratio ALTO (redução grande); com o ambiente calibrado
  num nível mais baixo desde o começo (`ambiente_ganho`) e ratio baixo
  (redução pequena), um release mais longo não trava mais o ambiente
  durante a narração inteira — ele só se ajusta mais suave.
- Como aplicar: `duck_ratio≈2`, `duck_release_ms` na faixa de 1500-3000.

**O `release` do ducking (sidechain) tem que ser MENOR que a pausa de
respiração da narração — isso valia pra config ANTIGA (ganho/ratio altos);
ver a regra de cima pra config atual.**
- Por quê: com `release=1800ms`, `ambiente_ganho` alto (0.9) e `ratio=4`
  (redução grande), o ambiente nunca "voltava" durante a narração — ficava
  achatado por quase todo o vídeo. Isso é ortogonal ao alvo de release
  atual (1,5-3s): o que importa é o TAMANHO da redução, não só o tempo.
  Redução pequena + release longo não trava; redução grande + release
  longo trava.

**Pra um som de fundo parecer "atrás" da voz, baixar o volume sozinho não
basta — precisa de reverb (textura de espaço) e lowpass (perda de agudo por
distância) junto.**
- Por quê: sem isso o ambiente só fica "mais baixo em primeiro plano", não
  "mais longe". Simulado com múltiplos taps de `aecho` (esse build de ffmpeg
  não tem `afreeverb`) + `lowpass` na faixa de 5000-6000Hz.

**Camada de som GRAVADO por baixo da síntese procedural melhora realismo,
mas nomear o elemento genericamente na escolha do arquivo pode reativar o
mesmo tipo de viés de clichê que aparece no prompt de imagem** (ver seção
acima) — escolher o arquivo pelo PERFIL da cena (`mar`/`chuva` do
plano.json), não por uma categoria genérica tipo "baleia" ou "tempestade".

**Variar o ponto de início do arquivo gravado por CENA** (não só por vídeo)
evita que o ouvido reconheça sempre o mesmo trecho inicial se duas cenas
usam o mesmo arquivo de fundo.

**Pegadinha de canal no `loudnorm`**: sempre DEPOIS de
`pan=stereo|c0=c0|c1=c0` (mono → estéreo duplicado) num branch mono, nunca
antes — medir loudness num sinal ainda mono e só depois duplicar pros dois
canais sai ~3-4dB mais alto que o alvo real, porque o BS.1770 soma os dois
canais do estéreo "mono duplicado". Medido em 28/08/2026: alvo -18 LUFS
(config antiga), saiu -14,3 LUFS até mover o `loudnorm` pra depois do
`pan`. A voz sozinha nunca bate o alvo exato no modo dinâmico (fica ~1dB
de diferença) — imprecisão normal, não é bug.

**Cadeia de voz completa hoje** (`aformat=mono → highpass 80Hz → EQ -3dB em
~325Hz [abafado] → EQ -3dB em 3000Hz [aspereza] → treble shelf -2dB acima
de 9000Hz [ar/sibilância residual] → deesser → acompressor → volume →
aecho [sala] → apad → pan=stereo → loudnorm dinâmico [leveler, não é a
masterização final] → asplit`). O de-esser existe porque um "S"/"Ç"
estourado é o que mais desperta em fone de ouvido — mais importante que
qualquer EQ estático nessa faixa.

**Referências pros números de mixagem** (nenhuma é norma oficial ITU/EBU/AES
pra conteúdo de sono especificamente — são o mais próximo que existe:
loudness geral e WCAG são normas de verdade, o resto é prática de mercado):
YouTube/loudness (criticallisteninglab.com, loudfix.com, sweetwater.com);
WCAG G56 — separação de 20dB (w3.org/WAI/WCAG22/Techniques/general/G56.html);
balanço voz/música (pureaudioinsight.com, mytasker.com); ducking
(xiaomitoday.com); ambiências pra sono (slonoise.com, amix-design.com);
`loudnorm`/`ebur128` (ffmpeg.org/ffmpeg-filters.html).

## Ritmo de narração e velocidade de TTS (`pipeline/s2_tts.py`)

**WPM de indústria (ACX/audiolivro: 150-160 palavras/min) é medido em
INGLÊS e não atravessa pra português.** Português tem mais sílabas por
palavra (~2,3-2,5 contra ~1,4 do inglês) — copiar o número em pt-BR sai
rápido demais. Não existe benchmark de indústria de locução pt-BR
equivalente ao da ACX; os únicos dados encontrados são estudos
fonoaudiológicos de fala espontânea (90-126 wpm, metodologias divergentes
entre si). Fator de conversão usado (estimativa, não medição): `wpm_ptBR ≈
wpm_inglês × 0,60-0,70`.
- **Correção ao cálculo de roteiro:** 30 min a ~85 wpm bruto (não 110-130,
  que era calibrado em inglês) dá **~2.550 palavras**, não 3.600. Escrever
  3.600 palavras em português pra 30 min de vídeo sai a ritmo ~120 wpm —
  rápido demais pro formato.
- **Alvos pra história de dormir em pt-BR:** WPM bruto 80-95 · WPM
  articulado (só o tempo com fala, sem contar silêncio) 115-130 ·
  orçamento de pausa 25-35% da linha do tempo · 3,2-4,0 sílabas/s
  articuladas.

**Velocidade percebida tem dois componentes independentes — pra sono,
mexer só no segundo:**
| Componente | O que é | Onde mexer |
|---|---|---|
| Taxa de articulação | Sílabas/s enquanto há som | `speed` do Kokoro |
| Orçamento de pausa | % da linha do tempo em silêncio | `PAUSA_RESPIRO`/`PAUSA_PARAGRAFO`/pontuação do roteiro |

**Não usar `speed` baixo (multiplicador global) como mecanismo principal de
lentidão.** `speed<1.0` no Kokoro estica TUDO por igual — vogal, consoante,
plosiva — e isso produz a assinatura característica de "voz sedada"
(formantes borrados); o ouvinte percebe que é sintético mesmo sem saber
identificar por quê. `pm_santa` a `speed=0.60` (decisão do video-02, ver
CLAUDE.md) usa exatamente esse mecanismo — funcionou bem no julgamento de
ouvido do Samuel pra esse vídeo específico, então **não foi refeito**, mas
não é o caminho recomendado daqui pra frente: prefira `speed` mais alto
(perto do natural) e regule o ritmo pela pausa.
- Como aplicar: o pipeline já corta o texto em "..." e quebras de
  parágrafo e insere SILÊNCIO DIGITAL entre os pedaços (`sintetiza()` em
  `s2_tts.py`) — isso já é o jeito certo (Kokoro não tem SSML/`<break>`,
  então o silêncio manual substitui). O que faltava era não depender do
  `speed` por cima disso.
- **Densidade decrescente pela pausa, não pela fala:** `FATOR_PAUSA_INICIO`/
  `FATOR_PAUSA_FIM` em `s2_tts.py` escalam `PAUSA_RESPIRO`/`PAUSA_PARAGRAFO`
  de 1,0× na primeira cena até 1,6× na última — a história fica mais
  rarefeita ao longo do episódio sem que a voz mude de velocidade.

**Vozes pt-BR disponíveis no Kokoro-82M**: `pm_santa` (masc., em uso desde
o video-01), `pm_alex` (masc.), `pf_dora` (fem.) — só 3 no pacote oficial.
Personas novas devem escolher entre essas 3 (ou trazer outro engine de TTS)
e validar por audição antes de fixar `speed` — a avaliação objetiva
(duração, % de silêncio) não substitui ouvir.

**Medir ritmo de verdade em vez de estimar** — pausas via ffmpeg
(`silencedetect=noise=-35dB:d=0.30`, somar `silence_duration`) e WPM
bruto/articulado a partir de palavras e duração real do áudio, não do
roteiro escrito. Ver `duracoes.json` (já grava `ppm` por cena) como ponto
de partida — falta ainda separar bruto de articulado e medir % de silêncio
por lá.

**Referências**: ACX/9300 palavras-hora (karencommins.com); faixas de WPM
por contexto (podcastify.io); velocidade de fala em PB, SciELO/CoDAS
(scielo.br/j/codas) e RBCS/UFPB (periodicos.ufpb.br/index.php/rbcs).

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
