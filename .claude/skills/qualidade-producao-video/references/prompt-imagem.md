# Prompt de imagem — referência completa

Carregado sob demanda pela skill `qualidade-producao-video`.
Cada regra aqui custou uma rodada real de erro-e-correção.

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

**Não pedir linguagem de "arte de jogo" — ela convém tela de título.** O cue
`painterly game background art` no `estilo_base` do vídeo 2 fez o modelo
escrever o nome da história DENTRO da imagem: "Moby-Dolk" na cena 2 e
"Moby-Dik / Herman Melville" na cena 20, essa última saindo photorealista de
quebra. A causa não é óbvia — arte de fundo de jogo, no conjunto de treino,
vem com título sobreposto e moldura de menu. Restaurar `no text` nos negativos
NÃO resolveu (testado: o título voltou), porque o modelo não estava
desobedecendo, estava atendendo ao que foi pedido. O que resolveu foi tirar o
cue e fechar o enquadramento da cena, reduzindo a área vazia que convida
tipografia.

Corolário medido em 03/09/2026: essa regra não estava escrita aqui, e o
video-03 — planejado depois da correção, mas a partir do template de antes —
nasceu com o mesmo cue no `estilo_base`. Achado pelo `--seco`, antes de gastar.
Regra que não vira documento volta.

**A negação vale para o campo `obra` também, não só para o prompt da cena.** O
`obra` entra no prompt POSITIVO (ver o formato na regra seguinte). O video-03
veio com `obra: "A Luz da Baía Quieta — história original ambientada na Grécia
Antiga, sem mitologia, sem deuses, sem monstros"`: três negações pedindo
exatamente mitologia, deuses e monstros. A intenção negativa mora em
`estilo.yaml/prompt_negativo`, que é registro humano e não chega ao modelo
(Z-Image-Turbo não aceita `negative_prompt`); a defesa real é o `estilo_base`
explícito.

**Título de obra só ajuda quando o modelo já conhece a obra.** "Moby-Dick,
Herman Melville" carrega associação visual de treino — século XIX, baleeiro,
mar — e paga o próprio custo. Um título que nós inventamos, "A Luz da Baía
Quieta", o modelo nunca viu: carrega zero informação visual e só adiciona o
risco de ser desenhado como texto na tela, em português, com acento. Em obra
original, pôr no `obra` a era e o tema, nunca o título:
`original story set on the ancient Greek coast — a lighthouse keeper's tale`.

**Não fixar hora do dia no `estilo_base`.** A base vale para todas as N cenas;
hora do dia não. O video-03 tinha `ancient Mediterranean Greek coast at night`
e contradizia três cenas — a 6 (memória diurna, `soft overcast daylight`), a 20
e a 21 (amanhecer). Medido: as 21 cenas já traziam a própria luz no prompt, a
base não precisava fixar nada. Na base vai só o invariante do vídeo — traço,
paleta, era, enquadramento.

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

