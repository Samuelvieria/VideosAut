---
projeto: Canal de Sono Automatizado
assunto: o que foi feito na sessão autônoma da madrugada de 04/09/2026
data: 2026-09-04
---

# A noite de 04/09

Samuel foi dormir e autorizou ~3 h de trabalho autônomo, com uso do Gemini
(`agy`) para revisão e delegação. Isto é o relatório.

Tudo está commitado e no `main`. Nada foi publicado no YouTube, nada foi gasto
em API paga, e nenhum arquivo seu foi sobrescrito.

---

## O canal se mexeu durante a noite

Quando comecei, o video-02 tinha **4 views**. Ao terminar, tem **253 views e 13
likes**.

Não vou vender isso como validação, porque não é:

- 253 continua sendo pouco, e a origem do tráfego ainda não dá para ver
- **retenção continua sem dado** — o Analytics atrasa até 48 h, e retenção é a
  única coisa que responde a pergunta do projeto
- 13 likes em 253 views é 5,1%, acima do típico de 2–4% — mas em amostra desse
  tamanho isso é ruído, não sinal

O que muda de verdade: a base do argumento "não temos dado nenhum" tinha 4
views. Agora tem movimento. **Vale voltar ao `s7_metricas` daqui a 24–48 h**,
quando a curva de retenção existir. É ela, e não a contagem de views, que diz
se o produto presta.

---

## O resumo em cinco linhas

Seis tarefas concluídas, todas do `docs/estado-e-direcao.md` §5 e do
`docs/mercado.md` §8. O estúdio agora **fecha o ciclo**: cria projeto, roda os
sete estágios, gera thumbnail. As lições de prompt que estavam em documento
viraram **recusa em código**. E delegar auditoria ao Gemini achou **sete erros
meus**, dos quais quatro eu não teria encontrado sozinho.

---

## O que foi feito

| | tarefa | onde |
|---|---|---|
| T1 | Personas carregam estética, e cue ruim é recusado | `estudio/db/personas.py` |
| T2 | Criar projeto pelo estúdio, a partir de uma persona | `estudio/db/projetos.py` |
| T3 | Estágio de thumbnail com as três candidatas | `pipeline/s5b_thumbs.py` |
| T4 | Título, tags e descrição do video-02 revisados | `fase0/video-02/metadados-revisados.md` |
| T6 | Amostras de ritmo de voz | `fase0/_vozes-candidatas/` |
| — | Auditoria da noite inteira pelo Gemini | commit `2d364ad` |

**T5 não foi feita**, e é a decisão que espera você — ver o fim.

---

## O que exige decisão sua

### 1. O video-03 vai para 75 min?

Ele está planejado com **30**. O mercado não tem um só caso de sucesso perto
disso: a faixa é 65–170 min. Mudar agora custa reescrever o roteiro; depois de
produzido, custa refazer tudo.

Se for, o roteiro precisa de **~7.650 palavras** (75 × 102 ppm medidos). Hoje
tem 2.157. Não é esticar o que existe — é escrever outro.

Não escrevi por conta própria: sete mil palavras de narrativa do seu canal é
decisão de gosto, e o `voz.md` foi extraído do *seu* texto aprovado, não do meu.

### 2. Ritmo da narração

Em `fase0/_vozes-candidatas/` tem quatro amostras do mesmo trecho:

| arquivo | ppm |
|---|---|
| `kokoro-speed060-atual.wav` | 123 |
| `kokoro-speed075.wav` | 152 |
| `kokoro-speed090.wav` | 195 |
| `kokoro-speed100-pausa.wav` | 205 |

A pergunta é uma só: **lentidão por esticar a fala, ou por pausar entre
frases?** A 0,60 o Kokoro estica vogal e consoante junto. A 1,00 com pausa
crescente a articulação fica natural e a lentidão vem do silêncio.

Ouça no fone, à noite, no volume de dormir.

### 3. Título e tags do video-02

Está pronto para colar em `fase0/video-02/metadados-revisados.md`. Não apliquei
porque nosso OAuth é só leitura.

### 4. Capítulos — ficou em aberto

O `monetizacao.md` diz não usar (a barra convida a pular). O Gemini levantou o
contrário, e o argumento é bom: capítulo deixa o **recorrente** achar onde
adormeceu, e recorrente é o único ativo real do nicho. Nenhum lado tem dado.

---

## O que a noite descobriu e contraria decisões nossas

**Nenhuma das duas referências tem cauda de ambiente.** A última legenda do
History at Night cai aos 75 de 75 min; a do Dreamoria, aos 169 de 169. As duas
narram até o fim. Nossa cauda de 9 min é invenção nossa, e o nosso "vídeo de 41
min" é um vídeo de **32 min com 9 de chuva**.

**Eles não desaceleram — só nós.** Medido por terço: −4,1% e −1,0%. Praticamente
reta. Nosso `FATOR_PAUSA` vai de 1,0 a 1,6 de propósito, e isso nunca foi
comparado com nada.

**Em pt-BR, o termo é ocupado por conteúdo infantil, e "adultos" não resgata.**
Busquei cinco termos: `história para dormir adultos` devolve Cinderela, Masha e
o Urso e Sapo Zé. E `audiolivro para dormir` traz Tolstói e Camus **em
espanhol**, sinal de que o segmento adulto narrado em português é fino o
bastante para o algoritmo buscar fora do idioma.

---

## Os erros meus que apareceram, e como

Registro porque o `docs/verificacao.md` existe para isso.

**Quatro achados pelo Gemini que eu não teria encontrado:**

1. **Validei três campos que não chegavam ao pipeline.** A persona guardava
   `resolucao`, `paleta` e `luz`, e o estúdio validava tudo — mas o
   `s3_imagens` usa constante chumbada e só lê `estilo_base`. Campo validado
   sem efeito é pior que campo ausente: dá impressão de configurar algo.
2. **Deixei `duracao_min * 80`** na meta de palavras do roteiro gerado — o
   número que eu mesmo corrigi para 102 três commits antes, na mesma sessão.
3. **Tirei "eles rodam perto do normal" de médias globais** sem testar se eles
   desaceleram. Era testável. Testei, e a conclusão se sustentou — mas por
   sorte, não por método.
4. **Generalizei "casos de sucesso produzem majoritariamente fracassos"** de um
   canal só. No History at Night a dispersão é 6,7×, não 350×.

**Três achados meus, olhando o resultado em vez de confiar que funcionou:**

5. Escrevi as regex de validação num heredoc não-raw, e **`\b` em Python é
   backspace**, não fronteira de palavra. Três das quatro regras viraram
   caractere invisível e aceitavam tudo. Só a primeira funcionava.
6. A primeira guarda de resolução **rejeitava 1280×720**, a nossa própria
   resolução de produção — modelei errado, achando que o render escala direto
   para 1920×1080, quando ele escala ×2 e recorta.
7. A posição fixa do texto da thumbnail **caía em cima da multidão** na variante
   C. Só apareceu olhando a folha de contato.

E um que quase custou caro: o estágio de thumbnail ia **sobrescrever as três
feitas à mão, incluindo a `thumb_B` publicada**. Agora ele se recusa a
sobrescrever arquivo que não foi ele que gerou.

---

## Como o Gemini foi usado

Pelo `agy` (Antigravity CLI), modelo `gemini-3.1-pro-high`, três vezes:

1. Revisão adversarial do validador de estética — achou 4 buracos
2. Crítica estratégica da proposta de título e tags — achou a contradição
3. Auditoria da noite inteira — os 4 achados acima

Nunca recebeu `.env`, chave, nem credencial. O método foi uma **caixa de saída
isolada**: copio para uma pasta só o que decidi enviar, e ele só enxerga
aquilo. Protocolo em `docs/consultas/README.md`.

Duas vezes ele errou um fato e eu peguei porque tinha a medição — disse que a
regra de resolução era 1024×576, quando é 1280×720 desde 02/09. Ele leu o
número velho **na nossa skill**, que estava desatualizada. Ou seja: a revisão
achou deriva de documentação de lambuja.

**A regra que usei:** revisão dele é entrada, não veredito. Onde ele discordou
de medição nossa, a medição ganhou. Onde ele apontou algo testável, eu testei
em vez de aceitar ou rejeitar pela prosa.

---

## O que continua bloqueado por você

- Escrever no YouTube (título, tags): OAuth é `youtube.readonly`
- Fish Audio e ElevenLabs: precisam de cadastro
- Gerar imagens na fal.ai: gasta dinheiro, e eu não gasto o seu dormindo
- `s1_roteiro.py` / `s6_upload.py`: proibidos até 2–3 vídeos publicados
- Workstation: a máquina não está aqui

O PC continua ligado. Ainda há trabalho desbloqueado na lista.
