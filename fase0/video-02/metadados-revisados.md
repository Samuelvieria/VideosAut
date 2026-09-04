# video-02 — título, tags e descrição revisados

Escrito em 04/09/2026 na sessão autônoma. **Nada aqui foi aplicado** — nosso
OAuth é `youtube.readonly` e escrever exige `youtube.force-ssl`, que precisa de
consentimento presencial. É para colar no Studio.

Base: [docs/mercado.md](../../docs/mercado.md) §4 e §5, mais uma medição nova
feita hoje (§ *O problema do termo*, abaixo).

---

## O problema do termo, medido hoje

Busquei cinco termos adultos em pt-BR, região BR, ordenado por views:

| termo | o que o topo devolve |
|---|---|
| `som de chuva para dormir` | ambiente puro — 1,3 bi, 230 M, 151 M |
| `narração para dormir` | meditação guiada e **desenho infantil** |
| `audiolivro para dormir` | afirmações, e **Tolstói e Camus em espanhol** |
| `história para dormir adultos` | **Cinderela, Masha e o Urso, Sapo Zé** |
| `podcast para dormir história` | contação infantil, e espanhol |

**A palavra "adultos" não resgata o termo.** E o espanhol aparecendo no topo de
`audiolivro para dormir` sugere que o segmento adulto narrado em português é
fino o bastante para o algoritmo buscar fora do idioma.

Consequência prática: **liderar por "história para dormir" nos coloca contra a
Masha e o Urso para um público que quer desenho.** Mesmo se ranquearmos, a
audiência está errada — e audiência errada abandona, o que é o pior sinal
possível.

O único termo pt-BR com demanda adulta comprovada é **som de chuva**. Ele já
está no nosso título — e, pela seção seguinte, precisa ir para a **frente**,
não ficar no sufixo, porque a busca no celular corta perto de 60 caracteres.

---

## Título

Atual: `História para Dormir com Som de Chuva e Mar | Moby Dick e a Baleia Branca` — 73 chars.

**A primeira versão desta proposta estava errada** e a revisão do
`gemini-3.1-pro` pegou o motivo: eu medi que a busca em pt-BR é movida por
*efeito* (chuva), não por curiosidade, e mesmo assim apliquei a fórmula do
mercado inglês. Diagnostiquei com evidência e prescrevi ignorando ela. A
proposta anterior tinha **96 caracteres** — mais longa que o título atual e que
todas as referências.

O que sobrevive à evidência, olhando os três vencedores:

| padrão | chars | o que aparece antes do corte de ~60 |
|---|---|---|
| `What It Was Like to Be a Pirate... \| History for Sleep` | 73 | a curiosidade inteira |
| `Boring History For Sleep \| Why You Wouldn't Last a Day...` | 70 | **o gênero inteiro** |
| `The ENTIRE Story of Greek Mythology` | **35** | tudo |

Não há ordem única. O que há é: **o termo que tem busca vem antes do corte.**
Em pt-BR esse termo é `som de chuva`, e é o único com demanda adulta provada.

**Recomendado** — 68 chars, o termo com busca na frente:

> Som de Chuva e Mar para Dormir | A viagem do Pequod, contada devagar

Alternativa mais curta, no padrão do vídeo de 5,50 M (35 chars, sem função) —
53 chars, aparece inteiro em qualquer tela:

> Som de Chuva e Mar | A História Completa de Moby Dick

O que **não** fazer, e aqui mudei de ideia com a medição de hoje:

- **Não** liderar por "História para Dormir". O termo entrega Masha e o Urso e
  Cinderela; liderar por ele nos põe contra desenho infantil para um público
  que quer desenho infantil.
- **Não** pôr "Moby Dick" na frente. Ninguém procura a obra às 23h para dormir.
- **Não** passar de ~60 caracteres antes do termo que importa.

---

## Tags

De 20 a 51 tags é o padrão das referências. Sem tag em inglês: vídeo em
português com tag inglesa atrai quem abandona nos primeiros segundos, e
abandono é o pior sinal que existe.

**Duas tags saíram depois da revisão**, por atrair o público errado — o mesmo
erro que eu apontei no título e repeti aqui:

- ~~`história para dormir`~~ — entrega desenho infantil; traz pai procurando
  desenho, que fecha em 5 segundos.
- ~~`moby dick resumo`~~ — traz estudante com pressa, que não fica 41 minutos
  numa narração lenta.

```
som de chuva para dormir
som de chuva e mar
som de mar para dormir
chuva para dormir profundamente
narração calma para dormir
voz calma para dormir
relaxar e dormir
insônia
sono profundo
ruído marrom
audiolivro para dormir
moby dick
herman melville
baleia branca
capitão ahab
história do mar
navio baleeiro
século 19
literatura clássica narrada
pixel art
```

---

## Descrição

Modelada nos dois canais de referência: parágrafo do conteúdo, nota de processo
declarando IA, e ressalva. O History at Night dedica três parágrafos a declarar
IA e tem 1,17 M de views — transparência não custou nada a ele.

```
Um velho baleeiro conta a viagem do Pequod, do cais de New Bedford até o
último dia de caça, com som de chuva e de mar por trás. Sem música, sem
interrupção — a narração vai devagar, e a chuva continua por mais nove minutos
depois que a história acaba, para você não acordar no silêncio.

Feito para ouvir deitado, no escuro, com o volume baixo.

──────────────

Sobre como este vídeo é feito

A adaptação foi escrita por nós a partir do texto de Herman Melville, que é de
domínio público. Não usamos tradução publicada — traduções são obra autoral
protegida, e o texto daqui é nosso.

A narração é gerada por síntese de voz, e as imagens são geradas uma a uma em
pixel art. O som de chuva e de mar é sintetizado, não é gravação de biblioteca.
A divulgação de conteúdo sintético está ativada neste vídeo.

Este é um vídeo de relaxamento, não uma fonte acadêmica. A história segue o
livro, mas foi condensada e adaptada para caber em uma noite.
```

---

## Capítulos — em aberto, e os dois lados têm argumento

O `docs/monetizacao.md` diz **não usar**: a barra de capítulos é interface
visível que convida a interagir, e interagir é o contrário de dormir.

O `gemini-3.1-pro` levantou o contrário, e o argumento é bom: capítulo deixa o
**espectador recorrente** achar o ponto onde adormeceu ontem — e recorrente é o
que o próprio `monetizacao.md` chama de único ativo real do nicho.

Nenhum dos dois lados tem dado. Fica em aberto, e é testável: um vídeo com,
um sem, comparando retenção e recorrência.

**Um fato objetivo dos dois lados:** capítulo no YouTube exige **pelo menos
três** marcações começando em `00:00`. Uma só não ativa nada. A versão anterior
desta proposta tinha uma marcação solta, que não faria efeito nenhum.

## Checklist ao aplicar

- [ ] Título trocado
- [ ] Tags substituídas
- [ ] Descrição substituída
- [ ] **Anúncios no meio: conferir se continuam DESATIVADOS** — o YouTube
      religa sozinho ao editar vídeo acima de 8 min
- [ ] Divulgação de conteúdo sintético continua ativada
- [ ] Capítulos: decisão em aberto (ver a seção acima). Se testar, precisa de
      **três ou mais** marcações começando em `00:00`, senão não ativa

## O que medir depois

Trocar título e tags de um vídeo com 4 views não vai provar nada sozinho — é o
tipo de mudança que só se lê em dias, e com tráfego. O número a observar é a
**origem do tráfego**: se busca subir, o termo pegou. Se continuar tudo em
"externo/direto", o problema não era o título.
