---
projeto: Canal de Sono Automatizado
assunto: como verificar trabalho que parece certo
data: 2026-09-03
---

# Verificação

Falha perigosa não é a que quebra. É a que **entrega um resultado plausível**.

Ideia adaptada do checklist de modos de falha de pesquisa com IA do repositório
`imbad0202/academic-research-skills`, que por sua vez parte das limitações
documentadas por Lu et al. em *The AI Scientist*. O conteúdo abaixo é nosso e
trata dos nossos modos de falha, não de artigos acadêmicos.

## Os quatro que já aconteceram aqui

### 1. Ler o artefato errado e confirmar a própria expectativa

Aconteceu em 02/09: reportei "o render terminou, 30 min, 50 MB" lendo um
`final.mp4` da véspera. O tamanho e a duração eram plausíveis, então não conferi
a data. A tarefa que eu achava concluída nem tinha rodado.

**Detecção:** antes de afirmar que algo foi gerado, comparar `mtime` do artefato
com o das entradas. Se a saída é mais velha que a entrada, não foi regerada.

### 2. Código que funciona por acidente de contexto

O mix reusava o label `[voz]` em dois filtros. Funcionava — mas só porque aquele
filtergraph era só de áudio. O mesmo padrão quebra com vídeo no grafo. Passou
despercebido porque o resultado estava correto.

**Detecção:** quando algo funciona e você não sabe explicar por quê, isolar num
teste mínimo. Foram três casos (só áudio / com vídeo / com `asplit`) que
mostraram que a versão "funcionando" era frágil, não certa.

### 3. Pressuposto não validado entre estágios

O `s5_render` assumia imagens 768×432. A API entregava 768×512. O corte descartou
os 116px de rodapé de **toda cena**, por semanas, sem um aviso.

**Detecção:** todo estágio que assume forma de dado de outro estágio precisa
conferir e abortar. `_confere_fonte()` faz isso agora. Errar alto é melhor que
entregar 30 min com composição cortada.

### 4. Número plausível vindo de dados misturados

Medi "27,6 min de narração" quando as cenas 1–7 estavam em `speed=0.60` e as
8–19 em `speed=0.75`. O total era plausível e teria produzido um vídeo com a
narração acelerando na metade.

**Detecção:** ao agregar arquivos gerados, conferir se vieram todos da mesma
configuração. `ls -lT` na pasta responde em um comando.

### 5. Inspecionar a amostra em vez do lote

Gerei 20 imagens e abri 4. Duas das 16 que não abri tinham **título de livro
escrito na imagem, e escrito errado** — uma delas na cena que fica 9 minutos na
tela. Só apareceu porque o Samuel assistiu.

**Detecção:** folha de contato. Um comando mostra as 20 de uma vez:

```bash
cd fase0/video-02/imagens && ffmpeg -y -pattern_type glob -i "cena_*.png" \
  -vf "scale=480:270,tile=4x5:margin=4:padding=4" -frames:v 1 -update 1 /tmp/contato.png
```

Custa segundos e uma leitura. Abrir quatro arquivos "representativos" não é
inspecionar o lote — é confirmar expectativa.

E vale para o vídeo pronto também: extrair um frame de cada cena do
`final.mp4` prova que a correção chegou no arquivo, não só na pasta de imagens.

## Ao consumir análise de IA externa

Vale para as consultas em `docs/consultas/`. Duas coisas concretas do último lote:

- **Citação inventada.** Uma das análises usava marcadores `[cite: 1]`, `[cite: 9]`
  que não resolvem para lugar nenhum. Era a mais bem escrita das seis, e a
  aparência de rigor não era rigor.
- **Confiança uniforme.** Modelos escrevem igual quando sabem e quando chutam.
  Por isso os prompts em `briefing-externo.md` exigem rótulo
  `[OBSERVADO]/[INFERIDO]/[PALPITE]` — quem ignora a regra vale menos, não mais.

**Regra:** número redondo demais, resultado que confirma exatamente o que se
esperava, e afirmação sem fonte verificável são os três sinais de parar e conferir.

## A pergunta única

Antes de reportar que algo funcionou:

> **Que evidência eu tenho além de o resultado parecer certo?**

Se a resposta for "nenhuma", não funcionou — ainda não se sabe.

---

## 6. Medir o que se correlaciona com a coisa, em vez da coisa

Em 04/09/2026 o Samuel ouviu a narração do video-03 e disse: *"a ênfase nas
sílabas está errada"*. Eu tentei **quatro** medições antes de acertar, e as
quatro falharam do mesmo jeito.

| tentativa | o que mediu | por que não serviu |
|---|---|---|
| taxa de erro do whisper por velocidade | reconhecimento | 15,8% idêntico em 0.60 a 1.00. Um sintetizador pode acentuar a sílaba errada e continuar perfeitamente inteligível |
| energia RMS por sílaba | volume | acertava nos nomes próprios. Tonicidade é energia **+ duração + altura**, e eu media um terço dela |
| varredura de regra de tonicidade em 1.177 palavras | ortografia | 164 "divergências", quase todas bug meu: contei "ia" de *bacia* como ditongo e o `ɐ̃ʊ̃` de *carvão* como duas sílabas |
| F0 por sílaba, com e sem tônica secundária | altura, sem controle | 22% contra 67% parecia forte. Mas as palavras com `ˌ` são mais longas, e em palavra isolada a altura decai naturalmente. Controlando por posição da tônica, **a diferença sumiu** |

O que funcionou foi **teste pareado**: a mesma palavra, a mesma voz, mudando
só a velocidade. Aí o efeito apareceu limpo e grande.

> A regra: quando a variável de interesse está confundida com outra, o número
> vai parecer um achado. **Se você não consegue mudar só uma coisa, ainda não
> tem experimento** — tem correlação com nome de conclusão.

E a variável só ficou isolável depois de eu conseguir mexer no fonema direto,
envolvendo o `g2p` do Kokoro. Antes disso eu estava comparando palavras
diferentes e chamando isso de teste.

Nota de honestidade: a hipótese que eu testei primeiro (a tônica secundária do
espeak, `ˌ`, empurrando o acento) veio do Gemini e **estava errada** — removê-la
não mudou nada, 1 melhorou e 5 ficaram idênticas. O que a delegação de fato
entregou foi outra coisa, e mais útil: apontar que tonicidade é energia +
duração + F0, e que eu estava medindo só a primeira.
