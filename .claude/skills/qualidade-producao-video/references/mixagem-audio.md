# Mixagem de áudio — referência completa

Carregado sob demanda pela skill `qualidade-producao-video`.

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
distância) junto. VALE PARA A VOZ; foi DERRUBADO para o ambiente.**
- Por quê valia: sem isso o ambiente só fica "mais baixo em primeiro plano",
  não "mais longe". Simulado com múltiplos taps de `aecho` (esse build de
  ffmpeg não tem `afreeverb`) + `lowpass` na faixa de 5000-6000Hz.
- **Por que caiu para o ambiente (03/09/2026):** era o `aecho` do ambiente a
  causa da granulação na cauda. Confirmado de ouvido num A/B
  (`teste/audio/B_rampa_sem_eco`) depois de CINCO hipóteses medidas falharem.
  Passar `decay=0,001` não resolve — o filtro recusa 0 e o eco continua
  audível; o jeito é não instanciar o `aecho`, que é o que
  `usar_eco_amb = ambiente_reverb >= 0.05` faz.
- Por que a cauda e não o vídeo todo: durante a narração a voz mascara o eco.
  Nos 9 min finais não há voz, e o artefato fica exposto. **Qualquer teste de
  ambiente tem que incluir a cauda** — julgar pelo meio do vídeo não vê nada.
- `voz_reverb` continua ligado (0,5 no padrão): a regra original segue de pé
  para a voz, que é onde a "sala" ajuda. O que caiu foi o eco no ambiente.

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



## Síntese do ambiente (`pipeline/ambiente.py`)

**Por que sintetizar e não gravar:** áudio no YouTube passa por Content ID, que
casa por impressão digital independentemente da licença comprada. Som gerado não
tem referência para casar — é a única fonte impossível de reivindicar.

**O mar não é ruído com modulação de amplitude.** Isso soa como ruído pulsando,
não como rebentação. Uma onda real é um evento discreto de três partes:

    grave que cresce -> estouro de banda larga -> cauda sibilante decaindo

Cada trem de ondas é uma envoltória ataque-decaimento com período próprio, e os
períodos são **incomensuráveis** (8,3 / 11,7 / 17,1 s) de propósito: somados, as
ondas nunca recaem em fase, então não existe loop audível e o ritmo fica
irregular como surf de verdade. O mesmo desenho serve o fogo, com períodos muito
mais curtos (1,7 / 2,9 / 4,3 s) e ataque bem mais seco — estalo, não onda.

**Cada camada tem um fundo constante** (o mar não some entre as ondas: `0.16 *
intensidade`). Ambiente que zera entre eventos vira sequência de sustos.

**Os dois canais são destoados**, não copiados: o canal direito multiplica os
períodos por 1,061 (mar), 1,037 (fogo) e usa seeds diferentes. A mesma onda não
chega igual nos dois ouvidos, e a imagem estéreo anda em vez de colar no centro.

**`chuva(abafada=True)`** troca a banda de 600–7000 Hz para 120–1400 Hz: é a
chuva ouvida de dentro, através de parede ou janela. É o que a chave `abafado`
do `ambiente` da cena liga.

Camadas: `mar`, `chuva`, `fogo`, `vento`, mais `abafado` (booleano) e `_`
(descrição em texto do lugar, só para leitura humana).

## Os valores de mixagem que cada vídeo usou

`MIXAGEM_PADRAO` em `s5_render.py` é o ponto de partida; o bloco `mixagem` do
`plano.json` sobrepõe, e o mixer do estúdio edita esse bloco sem tocar em código.

| | padrão | video-02 | |
|---|---|---|---|
| `voz_ganho` | 1.0 | 0.6 | |
| `voz_reverb` | 0.5 | 0.45 | |
| `voz_deesser` | 0.4 | 0.25 | |
| `ambiente_ganho` | 1.0 | 0.3 | |
| `ambiente_reverb` | **0.0** | 0.0 | corrigido de ouvido |
| `ambiente_lowpass_hz` | 5500 | 3500 | |
| `duck_threshold` | 0.05 | 0.05 | |
| `duck_ratio` | 2 | 2.0 | |
| `duck_attack_ms` | 200 | 170 | |
| `duck_release_ms` | 2000 | 1600 | |

A divergência de NÍVEL é intencional: os dois conjuntos entraram no mesmo commit
da remasterização para −14 LUFS, e o video-02 ficou preso aos valores dele para
não mudar de som depois de aprovado. **Não promova esses números para o padrão
sem ouvir** — eles foram calibrados para `pm_santa` a `speed` 0.60.

O `ambiente_reverb` é outra história, e é a lição desta seção: ele foi corrigido
**só no plano do video-02** em 03/09/2026 e o padrão ficou em 0.7. O video-03
herdou 0.7 e foi renderizado com a granulação de volta — descoberta só depois do
render, quando o vídeo já estava pronto para publicar. Desde então o `preflight`
avisa quando o eco do ambiente está ligado.
