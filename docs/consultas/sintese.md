---
projeto: Canal de Sono Automatizado
assunto: síntese das consultas a modelos externos
data: 2026-09-02
fontes: 7 arquivos (1 descartado por ser de outra conversa)
---

# Síntese das consultas externas

Seis análises úteis (Qwen, Gemini, DeepSeek e três sem assinatura clara).
`seila.md` era sobre computação em nuvem para PMEs — arquivo errado, descartado.

Critério aplicado: consenso entre modelos independentes é sinal; divergência é
onde a incerteza real mora; contradição com medição nossa exige método.

---

## 1. Consenso forte — agir

### CORTAR a moldura do narrador dos primeiros 60 s — **5 de 6**

O único ponto em que quase todos convergiram, e é sobre a peça de que eu mais
me orgulhava. O argumento repetido de formas diferentes:

> Quem busca conteúdo para dormir não pergunta "quem está falando?". Ele quer
> ancoragem acústica imediata. Apresentar uma persona nos primeiros 60 s gasta o
> trecho de maior risco cognitivo explicando a existência do narrador.

Um deles resumiu o efeito pretendido: cortar transforma o vídeo de *"alguém
conta uma história"* em *"você está dentro da história"*.

**Nuance importante:** ninguém disse para matar a moldura. Disseram para tirá-la
do começo. Ela pode ficar no fecho (cena 19 já faz isso), virar texto de
descrição, ou existir só visualmente — o velho aparece na imagem sem se
apresentar em narração.

O dissidente (Qwen) propôs manter e ajustar a prosódia: o narrador deve
"lembrar", não "contar". Vale como plano B se o corte piorar.

### PARAR de construir e publicar — **4 de 5**

O segundo consenso, e o mais desconfortável. Formulações independentes:

> "~2.200 linhas de Python, uma interface web, pipeline de 5 estágios, e zero
> espectadores. Qualquer nova automação é otimização de uma função cujo valor
> ainda não foi demonstrado."

> "Nenhuma linha de código nova até o vídeo 1 estar público e ter 1.000 views
> orgânicas. O render 'pendente' é um bloqueio autoimposto. Publique com o que
> tem."

Dois apontaram especificamente o `estudio/` como otimização prematura.

E um fez a conexão que ninguém mais fez, e que é a mais afiada do lote:

> Quanto melhor você constrói a fábrica antes de provar o produto, maior fica a
> tentação de produzir exatamente aquilo que a política chama de problemático.

### 33,5 min está errado — **6 de 6**, mas sem acordo sobre o certo

| resposta | votos |
|---|---|
| 45–60 min | 3 |
| 120 min | 2 |
| manter e esticar a cauda | 1 |

O argumento comum: 33 min é "vale da morte" — curto demais para quem usa como
rotina noturna, longo demais para quem quer só o gatilho de sono.

O melhor argumento veio de quem escolheu 45:

> Eu não aumentaria de 33 para 120 minutos antes de saber se as pessoas
> conseguem passar dos primeiros 2 minutos.

Nossa cauda de ambiente tem **1 minuto**. Praticamente todos apontaram que ela
é curta demais: se o ouvinte desperta levemente na transição do primeiro ciclo
de sono e encontra silêncio ou autoplay, o microdespertar é completo.

### Títulos: função primeiro, obra depois — **6 de 6**

Ninguém procura "Moby Dick pixel art" às 23h. Procura "história para dormir",
"som de chuva para dormir", "narração calma". Nosso título atual lidera com a
obra. Deve liderar com a função e usar a obra como qualificador.

### Descoberta: busca é o único mecanismo controlável no zero — **consenso**

O motor de crescimento é sugestão/sessão noturna: o espectador adormece, o
autoplay continua, o YouTube registra sessão longa e aprende o padrão. Mas esse
motor precisa de dados que um canal zerado não tem.

> Para um canal novo, search é o único mecanismo controlável. Browse e suggested
> dependem de dados de sessão que você ainda não tem.

Um citou um canal de sono cujo ponto de inflexão foi em **80 vídeos**. Ordem de
grandeza útil: 2–3/semana por 6 meses ≈ 60–70 vídeos.

---

## 2. Divergência real — testar, não escolher pela prosa

### Ducking: o lote se dividiu

| recomendação | quem |
|---|---|
| reduzir para 0–1 dB | 1 |
| reduzir para 2–3 dB | 1 |
| manter profundidade, alongar release para 4–6 s | 2 |
| aumentar para 8–10 dB | 1 |

Maioria: **não mexer na profundidade, alongar o release.** O efeito descrito é
eliminar a sensação de "o mar sumiu / o mar voltou" entre frases.

### LUFS: dividido, mas com uma síntese que resolve

| recomendação | quem |
|---|---|
| −18 a −22 | 2 |
| −14 está certo | 2 |
| −14 não é dogma, −16 serve | 1 |

A formulação que reconcilia:

> O que importa não é o LUFS integrado, é a **relação interna** entre voz e
> ambiente. O YouTube normaliza o ganho global, então a razão voz/ambiente
> sobrevive à normalização. Alvo: ambiente a −20/−22 LUFS, voz a −14, dando
> 6–8 dB de separação.

Isso é mensurável no nosso mix e não depende de escolher um lado.

### O erro que só aparece depois de 20 min: três hipóteses distintas

1. **Periodicidade perceptível.** Se depois de 15–20 min você consegue prever
   conscientemente quando vem a próxima onda, o ambiente está estruturado
   demais e vira "objeto auditivo" em vez de ambiente.
2. **Fadiga por decorrelação estéreo.** Correlação L/R ≈ 0 impede o sistema
   auditivo de construir imagem estéreo estável. Dois modelos levantaram isso
   independentemente.
3. **Fadiga espectral.** Chuva e mar juntos ocupam o espectro inteiro de forma
   contínua. Correção proposta: passa-alta ~120 Hz na chuva, deixando o mar
   carregar os graves.

A primeira é a que mais me preocupa, porque é falsificável e aponta direto para
a nossa implementação: os trens de onda usam períodos **fixos** de 8,3 / 11,7 /
17,1 s. São incomensuráveis entre si, mas cada um é perfeitamente periódico.

### Bilíngue: 3 × 2, e a minoria tem documentação

| arquitetura | votos | tipo de argumento |
|---|---|---|
| canais separados | 3 | teoria de sinal algorítmico |
| faixa de áudio no mesmo vídeo (MLA) | 2 | **documentação oficial do YouTube** |

Os dois a favor de MLA citam a página oficial do recurso e um dado do blog do
YouTube: criadores que usaram múltiplas faixas tiveram **>25% do watch time
vindo de idiomas não primários**.

### Começar pelo inglês? 3 sim, 2 não — e o "não" argumenta melhor

Os "sim" citam RPM 3–5×. Um deles com um contra-argumento engenhoso: começar
pelo inglês força validação cega, porque o dono não pode confiar no próprio
ouvido e precisa confiar nos dados.

Os "não" desmontam isso:

> Em conteúdo de sono, a qualidade da voz **é** o produto. Se a narração em
> inglês for ruim, o canal não converte e você nunca vai saber se foi a voz, o
> roteiro ou o algoritmo. RPM maior não compensa dados contaminados por um
> produto que você não consegue avaliar.

---

## 3. Correções ao que eu afirmei

**"Som procedural não tem referência para casar" ≠ imunidade a copyright.**
Content ID não é o único mecanismo. A vantagem real do som sintetizado é outra:
não dependemos de uma biblioteca cujo áudio milhares de outros criadores também
usam. Continua sendo boa decisão — mas eu vendi como garantia, e não é.

**Seed fixa não cria identidade visual.** Ela só torna a trajetória estocástica
reproduzível. Para consistência real a hierarquia é: imagem de referência →
estrutura espacial (ControlNet/depth) → prompt → seed → prefixo de estilo. Eu
tratei seed como se fosse âncora de estilo; não é.

**A política tem uma cláusula favorável que eu não tinha lido.** Ferramentas
automatizadas e templates são permitidos *desde que o produto final demonstre
visão criativa e ofereça valor*, e o exemplo dado é justamente IA usada para
visualizar um personagem e uma narrativa únicos. Isso descreve o projeto melhor
que "AI slop". Foi o que puxou a nota de risco para baixo.

**Risco de política: mediana 2,5/5** (notas: 2, 2, 2.5, 3, 3.5). Menor do que
eu vinha tratando.

---

## 4. Ganhos técnicos diretos

### `enable_prompt_expansion: false`

Parâmetro real da API da fal.ai que **nunca configuramos**. Se o LLM interno do
provedor está expandindo nossos prompts, ele injeta adjetivos diferentes a cada
chamada — o que sabotaria a consistência de estilo entre as 20 cenas por baixo
dos panos. Uma linha, custo zero.

### A baleia: ancoragem por contexto histórico

Convergência de quatro modelos, e a lógica é boa: na iconografia baleeira do
século XIX o **cachalote é o protagonista** — jubarte quase não aparece. Então
em vez de brigar com a anatomia, ativa-se a região certa do espaço latente pelo
contexto.

- `Physeter macrocephalus` — nome científico ativa dados com legenda taxonômica
- `19th century whaling scene`, `scrimshaw engraving`, `natural history plate`
- `leviathan` em vez de `whale`; `Nantucket`, `Pequod`, `Melville` como âncoras
- descrever geometria sem nomear: bloco retangular, mandíbula estreita, sem
  pregas na garganta, sem nadadeira dorsal proeminente
- img2img só com denoising **baixo** (0,30–0,55) — acima disso o viés retorna
- alternativa: gerar a cena e fazer inpainting só na região da baleia

### Consistência entre cenas

- **direção de luz fixa** em todas as cenas ancora estilo mais forte que o assunto
- **paleta explícita** com 3–4 cores nomeadas no prompt
- prompt em 4 camadas: sujeito + ambiente + luz + técnico

### Nota sobre o modelo

Z-Image-**Turbo** é a variante destilada de ~8 passos. A família tem Z-Image
base, voltada a maior diversidade e controle. A dificuldade anatômica pode ser
trade-off do Turbo, não erro do nosso pipeline.

---

## 5. O que fazer, em ordem

**Antes de publicar** (barato, reversível):

1. Cortar a moldura dos primeiros 60 s — começar dentro da história
2. Reescrever o título liderando pela função
3. Estender a cauda de ambiente de 1 min para 8–10 min
4. `enable_prompt_expansion: false`

**Publicar.** Sem mudar mais nada.

**Medir**, nesta ordem: retenção em 30 s, 60 s, 90 s, 5 min, 10 min; duração
média absoluta; dips e spikes; origem do tráfego; retenção por origem; novos vs
recorrentes; dispositivo.

**Só depois** mexer em duração, voz, ducking, LUFS e estéreo — **um de cada
vez**. A recomendação mais importante do lote:

> Não mudaria simultaneamente duração + voz + áudio + estrutura + imagens.
> Porque aí vocês perdem justamente aquilo que fizeram bem nos últimos 10 dias:
> usar evidência para tomar decisões.

---

## 6. A frase que resume

> O projeto não está em fase de construir. Está em fase de **medir**.

E a pergunta que nenhuma consulta responde:

> Uma pessoa que quer dormir realmente quer ficar 45 minutos ouvindo isso?
