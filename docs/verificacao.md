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
