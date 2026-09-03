# Análise do canal de Sleep Stories — Pré-mortem, Descoberta, Política, Áudio, Bilíngue e Imagem

## A. Retenção e formato — pré-mortem

### Diagnóstico

Se esse vídeo terminou com **340 views, 11% de retenção média e maioria abandonando antes de 90 s**, minha hipótese nº 1 não seria “33 minutos é longo”.

Seria:

> **o vídeo não entregou rapidamente a experiência que o espectador achou que tinha clicado para receber.**

E, especificamente, eu suspeitaria da **moldura do velho baleeiro + introdução narrativa**.

O YouTube define o indicador de *Intro* como a porcentagem que permanece depois dos primeiros 30 segundos, e recomenda observar exatamente onde aparecem quedas, picos e trechos estáveis.

### Ordem das hipóteses

| # | O que provavelmente aconteceu | Número que confirma/derruba |
|---|---|---|
| **1** | O início é lento demais para a promessa de “sleep story” | **Retenção em 0–30 s, 30–60 s e 60–90 s** |
| **2** | A moldura do velho baleeiro é percebida como história *sobre a história*, quando o usuário queria simplesmente dormir ouvindo Moby Dick | **Queda exatamente nos trechos da moldura** |
| **3** | 20 imagens trocando a cada ~100 s introduzem estímulo visual demais para uma experiência de sono | **Dips exatamente nos cortes/trocas de imagem** |
| **4** | A cadência narrativa é interessante demais para dormir — ou desinteressante demais para continuar ouvindo | **Retenção por segmentos + dips/spikes ao longo da narrativa** |
| **5** | 33,5 min não é suficiente para uma sessão completa de sono | **Watch time absoluto + porcentagem que chega ao final**, mas isso é menos provável como explicação para uma fuga nos primeiros 90 s |
| **6** | O vídeo simplesmente não encontrou ainda o público correto | **Traffic source + retenção segmentada por origem**, especialmente Browse/Suggested/Search |

A hipótese **#5 é particularmente importante**: duração inadequada pode prejudicar o produto, mas **não explica sozinha uma debandada antes dos 90 segundos**.

Se alguém entra esperando dormir e abandona em 40–80 segundos, o problema aconteceu **antes de a duração de 33 minutos importar**.

### O número mais importante seria a curva dos primeiros 90 segundos

**Cenário 1 — abertura problemática:**

```text
100%
  |
  |\
  | \
  |  \____
  |       \__________
  |
  +--------------------> tempo
     30   60   90
```

**Cenário 2 — queda inicial menor e estabilização:**

```text
100%
  |
  |\
  | \______
  |        \___
  |            \____
  |
  +-------------------->
     30   60   90
```

No primeiro caso, eu suspeitaria de **abertura problemática**. No segundo, suspeitaria mais de **seleção de audiência** ou de uma queda normal associada ao formato.

O próprio YouTube diz que uma queda específica (*dip*) indica que espectadores abandonaram ou pularam aquele trecho.

---

## A duração certa: **45 minutos**

Minha escolha é:

> **45 minutos.**

Não 2 horas.

Não 30 minutos.

Não 90 minutos.

**45 min é o ponto que eu testaria como formato-base para esse produto.**

O motivo não é uma suposta “duração mágica do algoritmo”. Não existe evidência para isso.

Existe uma razão de produto: o conteúdo é simultaneamente **história narrada + auxílio para adormecer**.

A literatura sobre intervenções de áudio para sono trabalha frequentemente com sessões na faixa de dezenas de minutos; uma revisão recente de *Sonic Sleep Aids* ressalta que há evidência para algumas formas de áudio, mas que a evidência específica para conteúdo narrado ainda é limitada.

Um RCT publicado em 2026 avaliou especificamente três categorias de intervenção de áudio, incluindo **Bedtime Stories**, **Sleep Sounds** e **Sleep Skills**.

Isso não prova que 45 minutos seja clinicamente superior. **Não é isso que estou afirmando.**

Estou dizendo que, para um produto narrativo, 45 minutos dá espaço suficiente para:

- atravessar a introdução;
- criar progressão;
- permitir que o ouvinte adormeça durante a história;
- ter conteúdo suficiente depois do início;
- sem obrigar o usuário a entrar numa sessão de 1–3 horas.

E o ponto fundamental:

**eu não aumentaria de 33 para 120 minutos antes de saber se as pessoas conseguem passar dos primeiros 2 minutos.**

---

## A moldura do velho narrador: **corta**

Minha decisão:

> **Corta os primeiros 60 segundos.**

Não porque a ideia seja ruim.

Pelo contrário: como conceito autoral, ela é boa.

O problema é **onde** ela está.

Para um canal de histórias convencionais, um velho baleeiro dizendo “vou lhe contar uma história...” pode criar expectativa.

Para **sleep content**, você está gastando justamente o trecho de maior risco cognitivo explicando a existência do narrador.

Eu começaria **já dentro da experiência**.

A moldura pode continuar existindo conceitualmente na obra, mas **não deve exigir que o espectador espere a história começar**.

---

# B. Descoberta — onde realmente vai travar

Aqui eu escolheria **um mecanismo**:

> ## **Suggested / Up Next alimentado por audiência adjacente.**

Não Search.

Não inscritos.

Não Shorts.

Não “volume”.

O mecanismo mais interessante para esse produto é:

**alguém que já está assistindo conteúdo de sono → continua assistindo → YouTube aprende que seu vídeo satisfaz aquele tipo de espectador → seu vídeo passa a aparecer para espectadores com comportamento semelhante.**

O próprio YouTube explica que seu sistema usa histórico de visualização, afinidade de interesse e comportamento de espectadores semelhantes; para recomendações de vídeos seguintes, o vídeo atualmente assistido é um sinal especialmente importante.

Isso é muito diferente de pensar:

> “Como faço o algoritmo descobrir meu canal?”

A pergunta correta é:

> **“Em qual população de espectadores o meu vídeo consegue produzir uma sessão satisfatória?”**

Para um canal de sono, existe uma vantagem estrutural:

**o comportamento de consumo é fortemente baseado em rotina.**

A pessoa não necessariamente está procurando *você*.

Ela está procurando **algo para ouvir enquanto dorme**.

Isso torna o vídeo potencialmente substituível por outros vídeos de sono — mas também permite que o sistema encontre pessoas com comportamento semelhante.

---

## O problema do canal zero

Com zero inscritos, você não tem:

```text
inscritos
   ↓
views iniciais
   ↓
dados
   ↓
recomendação
```

Você precisa de outra fonte de amostra.

O YouTube diz explicitamente que recomendações são baseadas em **personalização + performance quando o conteúdo é oferecido**.

Então os primeiros vídeos funcionam quase como **experimentos de identificação de audiência**.

O primeiro vídeo não precisa provar que o canal funciona.

Ele precisa permitir que o sistema descubra:

> “Que tipo de pessoa gosta disso?”

---

# Os 3 títulos que eu usaria

Não vou tratar isso como SEO. São **posicionamentos editoriais diferentes**.

### 1. **Moby Dick — Uma História para Dormir**

O mais direto.

Está dizendo:

> isto é Moby Dick + isto é sleep content.

Não tenta vender uma promessa intelectual.

### 2. **A Baleia Branca — Moby Dick para Dormir**

Aqui eu tentaria explorar **o imaginário da obra**, não o nome do produto.

“A Baleia Branca” é mais evocativo que simplesmente “Moby Dick”.

### 3. **Moby Dick, Contado à Luz da Chuva | História para Dormir**

Esse é o mais autoral.

Está tentando transformar:

**obra clássica**

em

**experiência atmosférica específica**.

É provavelmente o que eu escolheria depois de o canal ter alguma identidade.

---

# Uma coisa que o projeto NÃO deveria estar fazendo agora

> **Investir mais na automação do pipeline.**

Essa é a coisa que mais chama atenção.

Você já tem:

- TTS automatizado;
- geração de imagem;
- Whisper;
- render;
- mixer;
- FastAPI;
- execução por estágio;
- idempotência;
- workstation;
- ~2.200 linhas.

Mas ainda tem:

> **zero espectadores.**

Portanto, qualquer nova automação que reduza 20 minutos do processo de produção é, neste momento, uma otimização de uma função cujo valor ainda não foi demonstrado.

E isso não é só uma crítica de produto.

Tem uma conexão direta com a política do YouTube: o risco aparece quando o resultado começa a **parecer conteúdo produzido em massa, genérico, repetitivo ou intercambiável**.

Ou seja, existe uma ironia:

**quanto melhor vocês construírem a fábrica antes de provar o produto, maior fica a tentação de produzir exatamente aquilo que a política chama de problemático.**

---

# C. Política — aqui a situação é melhor do que parece

A atualização de **15 de julho de 2025** renomeou “repetitious content” para **“inauthentic content”** e esclareceu que a política inclui conteúdo **repetitivo ou produzido em massa**.

A política oficial diz que conteúdo monetizado deve ser original e não ser:

> **“mass-produced, generic, repetitive, or manipulative”**

E especifica como problema conteúdo que:

> **“appears to be produced using a template”**

Mais importante para vocês: o próprio YouTube coloca explicitamente entre os exemplos não monetizáveis:

> **“AI-generated content made with generic or unoriginal templates”**

Mas há uma parte muito mais favorável ao projeto.

A mesma política diz que ferramentas automatizadas e templates podem ser usados **desde que o produto final demonstre visão criativa e ofereça valor**, e dá como exemplo conteúdo que utiliza IA para visualizar **um personagem e uma narrativa únicos**.

Isso descreve seu projeto muito melhor do que “AI slop”.

---

## Minha nota de risco: **2/5**

Para **desmonetização especificamente por conteúdo inautêntico**, eu colocaria:

> **2/5 hoje.**

Não 1/5 porque o formato possui uma vulnerabilidade real.

Não 3/5 porque vocês fizeram várias coisas que afastam o projeto do exemplo clássico da política.

### O que reduz o risco

- roteiro original/adaptação própria;
- narrativa substancial;
- imagens diferentes;
- narrativa coerente;
- ambiente sonoro próprio;
- intervenção humana;
- revisão antes da publicação;
- ausência de automação de upload;
- ausência de produção ilimitada;
- frequência moderada;
- identidade estética definida.

E há uma frase da política particularmente importante:

> “the substance of each video should be materially varied and deliver creative, educational, or other value.”

---

# O aumento de risco que eu mais temeria

É este:

> **transformar o formato atual em um template rígido e escalá-lo.**

Imagine daqui a seis meses:

```text
Título X
↓
roteiro automático
↓
20 imagens
↓
cada imagem = 100 s
↓
mesma voz
↓
mesmo velho
↓
mesma abertura
↓
mesma estrutura
↓
mesma música/ambiente
↓
novo tema
```

Tecnicamente, isso seria maravilhoso.

Do ponto de vista de monetização, **é exatamente a direção errada**.

A política inclusive diz que conteúdo com o mesmo intro/outro pode ser monetizado **quando o corpo é diferente**, enquanto conteúdos que parecem intercambiáveis são problemáticos.

Então o maior perigo não é:

> “usar IA”.

É:

> **usar IA para transformar a identidade artística em uma linha de montagem perceptivelmente intercambiável.**

---

## Sobre a divulgação de IA

Vocês estão fazendo a coisa certa ao divulgar quando aplicável.

Mas há uma distinção importante.

O YouTube exige divulgação quando conteúdo sintético/alterado **parece realista**, enquanto conteúdo claramente irreal/animado geralmente não precisa.

E o YouTube afirma explicitamente que a divulgação **não limita a audiência nem impede monetização por si só**.

Portanto:

**não trataria o disclosure como ameaça ao crescimento.**

---

## E o Content ID?

Aqui eu corrigiria uma pequena premissa do projeto.

Vocês estão certos de que o Content ID trabalha com **impressões digitais de áudio e vídeo** e verifica uploads automaticamente.

Mas:

> **“som procedural não tem referência para casar” não significa que o risco de copyright desaparece.**

O Content ID não é o único mecanismo de copyright.

A vantagem real do som procedural é outra:

**vocês não dependem de uma biblioteca cujo áudio também possa estar sendo usado por milhares de outros criadores.**

É uma excelente decisão operacional, mas eu não transformaria isso em uma garantia de “imunidade a Content ID”.

---

# D. Áudio — o primeiro teste que eu faria

## Mudança nº 1

Você atualmente está em:

> **ducking: 4–6 dB**

Eu testaria:

> **4–6 dB → 2–3 dB**

Mantendo o release.

### O que eu esperaria ouvir

Menos sensação de:

```text
voz entra
↓
oceano desaparece
↓
voz termina
↓
oceano volta
```

E mais:

```text
VOZ
~~~~~~~~~~~~~~~~~~~~~~~~
MAR
~~~~~~~~~~~~~~~~~~~~~~~~
```

Isso é particularmente importante para o produto de sono porque o ambiente não é simplesmente “trilha de fundo”.

Ele é parte da experiência.

A literatura sobre áudio para sono é interessante justamente porque **os resultados para ruído/sons ambientais são menos conclusivos do que para algumas intervenções musicais**; uma revisão sistemática encontrou evidência insuficiente/heterogênea para afirmar um benefício robusto de ruído branco/rosa.

Portanto, vocês não querem que o ambiente pareça uma trilha sonora que entra e sai.

---

## O problema que provavelmente só aparece depois de 20 minutos

> **fadiga de modulação / periodicidade perceptível do ambiente.**

Especialmente:

- eventos de onda;
- ataques;
- padrões repetidos;
- pequenas diferenças de nível;
- distribuição estéreo excessivamente constante;
- envelope repetindo com frequência semelhante.

Nos primeiros 30 segundos:

> “Nossa, que som de mar legal.”

Depois de 20 minutos:

> “Tem alguma coisa repetindo.”

E assim que o cérebro começa a perceber o padrão, ele deixa de funcionar como **ambiente** e vira **objeto auditivo**.

Para sono, isso é péssimo.

Eu suspeitaria particularmente de **periodicidade estatística**, não necessariamente de repetição literal.

O teste seria escutar:

- 5 min;
- 15 min;
- 30 min;

**sem olhar para a tela**.

Se depois de 15–20 minutos você consegue prever conscientemente quando virá a próxima onda, o ambiente provavelmente está estruturado demais.

---

# −14 LUFS está certo?

## **Não.**

Não como requisito de produto.

−14 LUFS pode ser um ponto de partida razoável para entrega, mas **“YouTube normaliza para −14 LUFS” não significa que −14 LUFS seja o nível correto que todo conteúdo deveria masterizar**.

A normalização da plataforma e a escolha do nível de master são problemas diferentes.

Para sleep content, eu priorizaria:

1. ausência de clipping;
2. true peak seguro;
3. ausência de ruído/artefatos;
4. conforto perceptual;
5. dinâmica extremamente estável;
6. consistência entre episódios.

Não perseguiria −14 como número sagrado.

Se o seu master soa confortável a **−16 LUFS**, isso não é um erro.

O YouTube vai fazer sua própria reprodução/normalização conforme seu sistema.

---

# E. Bilíngue — eu escolheria uma arquitetura

## **Faixas de áudio no mesmo vídeo.**

Hoje, eu não criaria dois canais.

O próprio YouTube possui **Multi-language Audio**, que permite colocar diferentes faixas de áudio no mesmo vídeo, e o sistema pode selecionar a faixa de acordo com a preferência de idioma do espectador.

Mais interessante:

O YouTube informa que criadores que usam múltiplas faixas obtiveram **mais de 25% do watch time vindo de visualizações em idioma não primário**, em média.

Então, para seu formato:

```text
Moby Dick
│
├── Português
│
└── English
```

faz muito mais sentido operacionalmente do que:

```text
Canal PT
│
└── Moby Dick

Canal EN
│
└── Moby Dick
```

Você mantém:

- uma obra;
- uma URL;
- um histórico;
- uma biblioteca;
- uma identidade;
- um conjunto de métricas;
- duas experiências linguísticas.

---

## O modo de falha da arquitetura que eu NÃO escolheria

Se você criar dois canais, o problema não aparece no dia 1.

Aparece depois de algumas dezenas de vídeos.

Você começa a ter:

```text
PT:
vídeo 01
vídeo 02
vídeo 03
...

EN:
vídeo 01
vídeo 02
vídeo 03
...
```

E passa a dividir:

- dados;
- audiência;
- comentários;
- histórico;
- autoridade;
- esforço de produção;
- manutenção;
- decisões editoriais.

Pior: o mesmo material visual passa a ser replicado entre dois catálogos.

Isso não necessariamente viola a política, mas **aumenta o caráter de fábrica** do projeto.

Com áudio multilíngue, a própria plataforma recomenda concentrar esforços em um ou dois idiomas e permite analisar o desempenho separado por idioma.

---

## Começar em inglês por causa do RPM?

**Não.**

Eu começaria em **português**.

E isso não é uma decisão sentimental.

O problema operacional é:

> **você é o principal controle de qualidade humano do produto.**

Você consegue detectar em português:

- pronúncia;
- ritmo;
- frase estranha;
- adaptação ruim;
- erro semântico;
- entonação inadequada;
- palavra que soa artificial.

Em inglês você mesmo disse que não consegue garantir isso.

Isso cria uma assimetria perigosa:

```text
PT
qualidade controlável
↓
feedback confiável

EN
qualidade não controlável
↓
feedback contaminado
```

RPM maior não compensa dados contaminados por um produto que você não consegue avaliar.

**O inglês deveria entrar depois, como segunda faixa.**

---

# F. Imagem — viés de treino

O problema da baleia é real e não é simplesmente:

> “o prompt está ruim”.

O que você está encontrando é uma forma de **priorização/associação estatística do conceito**.

Você escreve:

> cachalote

mas o modelo tem uma representação visual extremamente forte de:

> whale → humpback-like whale

e os atributos que você descreve não necessariamente conseguem vencer essa associação.

Em modelos text-to-image, o texto não é uma consulta a um banco de dados anatômico.

Ele é uma condição para uma distribuição generativa.

---

# 1. A técnica que eu usaria

> ## **Decomposição do conceito + referência visual**

Não tentaria vencer o viés apenas aumentando a quantidade de anatomia no prompt.

Eu faria:

```text
REFERÊNCIA
   ↓
estrutura visual
   +
PROMPT
   ↓
semântica / época / atmosfera
```

Essa é precisamente a lógica por trás de técnicas como **IP-Adapter**: uma imagem fornece condicionamento visual separado do texto. O trabalho original introduz uma arquitetura de atenção desacoplada para permitir que texto e imagem controlem a geração simultaneamente.

A implementação do Diffusers também permite combinar **IP-Adapter + ControlNet**, usando a imagem para aparência/identidade e ControlNet para estrutura.

---

# 2. Vocabulário sem dizer “baleia”

Sim.

Mas não existe uma “palavra mágica” garantida.

Eu exploraria **descrições visuais semanticamente próximas da forma**, em vez de repetir a taxonomia.

### Anatomia

- massive blunt rectangular head
- enormous squared forehead
- sharply truncated snout
- head disproportionately large relative to body
- narrow lower jaw
- compact pectoral fins
- small dorsal fin set far back
- dark charcoal-gray skin

### Contexto histórico

- 19th-century whaling engraving
- sperm-whaling vessel
- Nantucket whaling scene
- engraved natural history plate
- maritime naturalist illustration
- 19th-century zoological illustration

### Composição

- side profile
- full body silhouette
- head occupying approximately one third of total body length

O interessante é que isso cria uma **representação distribuída**:

```text
"cachalote"
      ↓
[conceito lexical]

"massive squared forehead"
"small dorsal fin"
"narrow lower jaw"
"19th-century whaling engraving"
      ↓
[conjunto de atributos visuais]
```

Isso pode escapar parcialmente da associação dominante de “whale”.

Mas, novamente:

**não há garantia.**

---

# 3. Img2img resolve?

## **Pode resolver muito — se a referência realmente carregar a anatomia.**

Mas eu não diria:

> “img2img resolve.”

Diria:

> **img2img desloca o problema de geração para preservação de estrutura.**

Se você fornece uma gravura de cachalote:

```text
gravura correta
      ↓
estrutura visual forte
      ↓
img2img
      ↓
pixel-art
```

o modelo não começa mais do espaço inteiro de:

> “qual é a aparência de uma baleia?”

Ele recebe uma configuração visual já existente.

Isso é exatamente a direção de pesquisa em edição/condicionamento.

ControlNet, por exemplo, foi criado para fornecer condições espaciais como **edges, depth, segmentation e pose**, mantendo o backbone de geração.

Prompt-to-Prompt mostrou que a atenção cruzada controla fortemente a relação entre palavras e regiões espaciais da imagem, permitindo alterações preservando estrutura.

### Mas há uma ressalva importante

Se o modelo de destino não tem um bom mecanismo de referência/edição, ele pode **reinterpretar** a baleia durante a difusão.

Ou seja:

```text
gravura correta
      ↓
██████████
difusão
      ↓
"eu conheço baleia"
      ↓
jubarte
```

Portanto, a referência precisa ter **peso suficiente** no processo.

---

# 4. Consistência das 20 cenas

Além de prefixo + seed:

## **um “reference bible” visual.**

Eu criaria uma imagem-mestre que define:

- paleta;
- escala de pixel;
- proporção de personagens;
- desenho de rostos;
- iluminação;
- contraste;
- arquitetura;
- tratamento do mar;
- tratamento da chuva;
- textura;
- enquadramento;
- tipo de horizonte;
- densidade de detalhes.

E então cada cena seria:

```text
STYLE BIBLE
     +
CHARACTER / OBJECT REFERENCE
     +
SCENE DESCRIPTION
```

Não:

```text
PROMPT UNIVERSAL
     +
SCENE
```

---

# O que realmente funciona melhor

A hierarquia que eu usaria seria:

### **1. referência visual**
Mais importante para aparência.

### **2. estrutura espacial**
ControlNet / depth / edge / layout quando disponível.

### **3. prompt**
Para semântica e conteúdo.

### **4. seed**
Para reprodutibilidade, não para consistência semântica.

### **5. prefixo de estilo**
Para manter vocabulário visual.

Essa distinção é importante.

**Seed fixa não cria identidade.**

Ela só torna a trajetória estocástica reproduzível.

---

# Uma observação importante sobre Z-Image

O repositório oficial do Z-Image confirma que **Z-Image-Turbo é uma versão destilada para cerca de 8 NFEs**, enquanto o Z-Image base é descrito como a variante destinada a maior diversidade, controle e fine-tuning.

O próprio projeto separa:

- Z-Image-Turbo;
- Z-Image;
- Z-Image-Omni-Base;
- Z-Image-Edit.

Isso é relevante para o problema porque vocês estão usando justamente a variante **Turbo**, cuja grande vantagem é velocidade/eficiência.

Portanto, eu **não interpretaria a dificuldade anatômica como evidência de que seu pipeline está errado**.

Pode ser simplesmente uma consequência do trade-off do modelo.

---

# Material técnico recomendado

## 🔴 Prioridade máxima

### YouTube — política de monetização

**YouTube — Channel Monetization Policies**

https://support.google.com/youtube/answer/1311392

Especialmente:

- Generic or Repetitive Content
- Reused Content
- Unsatisfying or Off-putting Content
- Creator Integrity

A política atual deixa bastante claro que **produção em massa + template + conteúdo intercambiável** é o verdadeiro perigo.

---

### YouTube — Recommendation System

**YouTube — Recommendation System**

https://support.google.com/youtube/answer/16533387

É provavelmente o documento mais importante para entender o problema de descoberta.

A própria plataforma reduz o problema a:

**personalização + performance + satisfação.**

---

### YouTube — Audience Retention

**YouTube — Measure key moments for audience retention**

https://support.google.com/youtube/answer/9314415

É o documento que eu usaria quando chegar o primeiro vídeo.

Ele explica:

- Intro;
- Dips;
- Spikes;
- Top moments.

---

## 🟠 IA / produção

### Z-Image oficial

**Tongyi-MAI/Z-Image — GitHub oficial**

https://github.com/Tongyi-MAI/Z-Image

É a primeira fonte que eu usaria para qualquer mudança no gerador.

---

### Manual comunitário de prompting para Z-Image

**Z-Image Prompting Manual**

https://github.com/fabiodemartin/z-image-turbo/blob/main/z-image-prompt-en.md

É útil especificamente para o comportamento do Turbo e para a abordagem de **positive constraints**, já que o Turbo não usa o mecanismo convencional de negative prompting.

---

### IP-Adapter — paper

**IP-Adapter — arXiv**

https://arxiv.org/abs/2308.06721

Esse é provavelmente o paper **mais diretamente relevante para o problema de consistência visual**.

---

### IP-Adapter — Diffusers

**Hugging Face Diffusers — IP-Adapter**

https://huggingface.co/docs/diffusers/main/using-diffusers/ip_adapter

Especialmente interessante porque mostra na prática a combinação:

**IP-Adapter + ControlNet**.

---

### ControlNet — paper

**ControlNet — arXiv**

https://arxiv.org/abs/2302.05543

Fundamental para entender como preservar:

- estrutura;
- pose;
- profundidade;
- edges;
- layout.

---

### ControlNet — GitHub

**lllyasviel/ControlNet**

https://github.com/lllyasviel/ControlNet

Implementação original e enorme ecossistema.

---

### Prompt-to-Prompt

**Prompt-to-Prompt — arXiv**

https://arxiv.org/abs/2208.01626

Vale estudar para entender **por que mudar uma palavra pode destruir a imagem inteira** e como a cross-attention influencia isso.

---

### Concept bleeding

**Isolated Diffusion — arXiv**

https://arxiv.org/abs/2403.16954

Relevante porque trata explicitamente de **concept bleeding**, ou seja, interferência entre conceitos durante a geração.

---

## 🟡 Sono / áudio

### Revisão sistemática de estimulação auditiva

**Systematic Review — Auditory Stimulation and Sleep**

https://pmc.ncbi.nlm.nih.gov/articles/PMC9163611/

Boa para separar:

> “parece relaxante”

de

> “há evidência experimental”.

---

### Bedtime Stories especificamente

**USleep — Bedtime Stories, Sleep Sounds and Sleep Skills**

https://pubmed.ncbi.nlm.nih.gov/42223503/

Particularmente importante porque **não estuda apenas música**: inclui explicitamente *Bedtime Stories*.

---

### Sonic Sleep Aids

**Between Sound and Sleep — Sonic Sleep Aids**

https://pubmed.ncbi.nlm.nih.gov/41056369/

Boa visão geral do estado atual da literatura sobre:

- música;
- ambiente;
- histórias;
- áudio guiado.

A conclusão importante é que a evidência para **narrated content** ainda é relativamente limitada.

---

## 🟢 Multilíngue

### Multi-language Audio — documentação oficial

**YouTube — Add Multi-language Features**

https://support.google.com/youtube/answer/13338784

Esse documento praticamente resolve a discussão arquitetural para este caso: uma obra, várias faixas.

---

### Expansão do Multi-language Audio

**YouTube Blog — Multi-language Audio**

https://blog.youtube/news-and-events/multi-language-audio/

Contém o dado de **>25% do watch time vindo de idiomas não primários** entre criadores que utilizaram o recurso.

---

# Leitura final do projeto

Depois de cruzar tudo, eu resumiria o estado atual assim:

```text
                 PROJETO
                    │
        ┌───────────┴───────────┐
        │                       │
     TÉCNICA                 PRODUTO
        │                       │
     resolvida              NÃO VALIDADO
        │                       │
        │              ┌────────┴────────┐
        │              │                 │
        │          retenção          descoberta
        │              │                 │
        │          desconhecida      desconhecida
        │
        └──────────────┐
                       │
                 POLÍTICA YT
                       │
                    2/5 hoje
```

E existe uma conclusão que considero **mais importante que todas as outras**:

### O projeto não está em fase de construir.

Ele está em fase de **medir**.

Você já passou da fronteira em que adicionar tecnologia necessariamente melhora o produto.

Agora o ativo mais valioso é:

> **o primeiro conjunto de dados reais de espectadores.**

Eu publicaria o primeiro vídeo **sem mudar a arquitetura**, mas com a abertura sem os 60 segundos da moldura.

E os primeiros números que eu salvaria seriam:

1. retenção em **30 s**;
2. retenção em **60 s**;
3. retenção em **90 s**;
4. retenção em **5 min**;
5. retenção em **10 min**;
6. retenção média;
7. duração média assistida;
8. dips/spikes;
9. Browse/Suggested/Search;
10. retenção por origem;
11. novos vs. recorrentes;
12. dispositivo;
13. idioma do espectador.

**Não mudaria simultaneamente duração + voz + áudio + estrutura + imagens.**

Porque aí vocês perdem justamente aquilo que fizeram muito bem nos últimos 10 dias:

> **usar evidência para tomar decisões.**

E, no momento, a maior incógnita do projeto não é Kokoro, Z-Image, FFmpeg ou FastAPI.

É simplesmente:

> **“Uma pessoa que quer dormir realmente quer ficar 45 minutos ouvindo isso?”**

Essa pergunta só o primeiro upload consegue responder.
