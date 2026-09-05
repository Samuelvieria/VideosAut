---
projeto: Canal de Sono Automatizado
assunto: inglês — canal separado, mesmo canal, ou faixa de áudio?
data: 2026-09-05
metodo: medição pela YouTube Data API, 9 termos de busca, 225 vídeos, ~70 canais
---

# Inglês: canal separado?

A pergunta tem três respostas possíveis, não duas — e a medição mudou qual
delas eu recomendaria antes de medir.

---

## O que a medição mostrou

Nove buscas, 225 vídeos, agrupadas por segmento. Números do dia 05/09/2026.

| segmento | duração mediana | views/vídeo | quem domina |
|---|---|---|---|
| **PT — "história para dormir"** | **25 min** | 215 mil | **infantil**: José Totoy (21,8 M), Os Amiguinhos (10,2 M), AQUARELA KIDS (4,2 M) |
| **PT — "adulto" explícito** | 65 min | 215 mil | **meditação**: Cassio Toledo (8,6 M), Easy Zen (1,45 M), Meditar para Despertar |
| **PT — som/ambiente** | **482 min** | **1,47 M** | Soothing Relaxation (12,1 M), Filtr Music Brasil |
| **EN — história adulto** | **147 min** | 240 mil | Get Sleepy (716 mil), **Sleepless Historian (713 mil)**, Good Knights Sleep |

### A conclusão que dói

**O nosso produto — história original narrada para adultos — praticamente não
tem segmento estabelecido em português.**

Buscar o termo óbvio devolve canal infantil. Buscar com "adultos" na frase
devolve **meditação**. E meditação é justamente a única categoria que a política
do YouTube marca como não monetizável quando narrada por persona de IA
("conselho de saúde"). O espaço adulto em pt-BR está ocupado pela coisa que não
podemos ser.

Em inglês o mesmo produto tem **vários canais maduros**, e um deles —
**Sleepless Historian, 713 mil inscritos, 347 vídeos, 128 mil views por vídeo**
— é quase exatamente o que estamos construindo: história narrada, ambientação
histórica, formato longo.

> **Limite honesto desta medição.** "Não existe segmento" pode significar *não
> há demanda* ou *há demanda não atendida*. Estes dados não separam as duas
> coisas — busca mostra o que existe, não o que se quer. Um contra-argumento
> real: o segmento adulto de **som puro** em pt-BR é enorme (mediana de **8
> horas** por vídeo e 1,47 milhão de views), o que prova que existe público
> brasileiro adulto usando YouTube para dormir. Ele só não está consumindo
> história.
>
> Também: apareceram canais em espanhol nos resultados em português, então o
> filtro de idioma da API é frouxo. A amostra é de 225 vídeos, não de um censo.

---

## As três opções

### A) Canal separado em inglês

**A favor:** o público é outro, e canal com dois idiomas embaralha o sinal de
"para quem isto é". Metadado, palavras-chave e seção Sobre não servem dois
idiomas ao mesmo tempo. RPM em inglês/EUA é bem maior.

**Contra, e é pesado:** **dois canais são dois patamares de YPP.** Faltam ~5
meses até 01/02/2027, quando a barra dobra para 8.000 horas. Temos **3
inscritos e 2 vídeos**. Dividir o esforço agora é arriscar não fechar nenhum dos
dois. E tudo duplica — Sobre, playlists, miniaturas, comunidade, leitura de
métricas.

### B) Mesmo canal, vídeos em inglês misturados

**Não recomendo.** Reúne o pior dos dois: o brasileiro que se inscreveu recebe
notificação de vídeo que não entende, e o americano vê um canal cuja metade não
é para ele. Abandono nos dois lados, que é o pior sinal que existe.

### C) Faixa de áudio em inglês no MESMO vídeo

O YouTube permite **até 6 faixas de áudio por vídeo**, e o player escolhe pela
preferência do espectador. Título e descrição também localizam. O mesmo vídeo
aparece como *"História para Dormir…"* para um e *"Sleep Story…"* para outro.

**Por que isso encaixa em nós especificamente:** o vídeo é imagem + narração +
ambiente. **A imagem não tem idioma e o ambiente também não.** Só a narração
muda. E as quatro vozes que você aprovou existem em pt-BR e en-US **com o mesmo
timbre** — o narrador não muda de identidade ao trocar de idioma.

**E o ponto que decide, dado o prazo:** um vídeo com duas faixas acumula horas
das **duas** audiências para **um** patamar de YPP.

**O custo real, e ele existe:** a faixa de áudio precisa bater a duração do
vídeo **com tolerância de 1 segundo**. Isso obriga o texto em inglês a ser
**adaptação presa ao tempo das cenas**, não roteiro reescrito livremente — o que
contraria a decisão registrada em [mercado.md](mercado.md) §6.

Essa decisão, porém, foi tomada por um motivo específico: prosa em inglês gerada
por IA tem tiques próprios (*delve*, *tapestry*, *testament to*). Isso é
problema de **qualidade de escrita**, não de estrutura — e escrita cuidadosa
presa a um tempo continua sendo escrita cuidadosa. **Legendar não vale**: em
vídeo de sono, ler é contraproducente.

**Requisito:** Recursos Avançados ativados (a mesma etapa que destrava o teste
A/B de miniatura).

---

## Recomendação

**Não abra o segundo canal agora. Faça a faixa de áudio.** Três razões, em
ordem de peso:

1. **O prazo.** Cinco meses, um patamar. Dois canais são duas montanhas, e
   nenhuma delas está começada — 3 inscritos.
2. **O catálogo tem dois vídeos.** Não há o que dividir. A pergunta "canal
   separado?" é boa e vem cedo demais.
3. **O custo marginal é quase zero.** A imagem, o ambiente, o render e a
   miniatura já existem. Falta o texto adaptado e uma chamada de TTS de R$ 12.

**E o gatilho para reabrir a decisão, definido agora para não ser decidido no
calor:** quando a analytics por faixa de áudio mostrar que **o público em inglês
supera o em português em horas assistidas**, o canal separado deixa de ser
divisão de esforço e passa a ser reconhecimento de um público que já existe.
Aí ele se justifica sozinho.

### E se a medição estiver certa sobre o português?

Este é o incômodo que a medição deixa, e não vou embrulhar: **é possível que o
produto esteja no idioma errado.** História narrada para adultos tem mercado
provado em inglês e quase nenhum em português.

Isso **não** é argumento para abandonar o pt-BR — é argumento para que a faixa
em inglês exista **desde o próximo vídeo**, e para tratar a comparação entre as
duas como o experimento mais importante dos próximos meses. Ela custa R$ 12 por
vídeo e responde uma pergunta que nenhuma quantidade de pesquisa responde.

---

## O que fazer no próximo vídeo

- [ ] Ativar **Recursos Avançados** (destrava faixa de áudio e teste A/B)
- [ ] Escrever o roteiro em pt-BR normalmente
- [ ] **Adaptar** para o inglês preso ao tempo de cada cena — não traduzir
      literal, não reescrever livre
- [ ] Gerar a narração com a mesma voz em `en-US` (Algieba, preferida dele)
- [ ] Conferir a duração final: tolerância de **1 segundo**
- [ ] Subir a faixa e localizar título e descrição
- [ ] Ler a analytics **por faixa de áudio** depois de 30 dias
