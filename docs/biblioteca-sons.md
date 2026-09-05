---
projeto: Canal de Sono Automatizado
assunto: biblioteca de sons ambiente — avaliação técnica
data: 2026-08-27
---

# Biblioteca de sons

12 arquivos baixados em 27/08/2026, todos com nomenclatura do Pixabay
(`autor-nome-ID.mp3`). Ficam em `sons/`, **não versionados** (88 MB) — este doc é o
manifesto. Ao migrar de máquina, copiar a pasta junto.

## Licença

Pixabay Content License permite uso comercial sem atribuição. **Mas licença e
Content ID são coisas separadas** — o Content ID casa por impressão digital,
independentemente do que a licença diz, e há casos conhecidos de terceiros
registrando material de biblioteca livre. Para *ambiente de natureza* o risco é
baixo (fingerprint funciona mal em ruído de banda larga e quase ninguém registra
chuva), bem menor que para música. `[HIPÓTESE]`

Mitigação prática: usar os arquivos como **camada** sobre a base sintética, nunca
sozinhos e nunca em primeiro plano. Ambiente sintético + camada gravada por cima é
muito mais difícil de casar do que a gravação limpa.

## Avaliação

`estab` = desvio do envelope em janelas de 1 s. Baixo = textura contínua (bom para
cama de fundo). Alto = eventos marcados (usar pontual, nunca em loop).

| arquivo | dur | LUFS | grave/médio/agudo | estab | loop | uso |
|---|---|---|---|---|---|---|
| `soul_serenity_sounds-ambient-noise` | 104s | −34,6 | 91/38/16 | **1,1 dB** | médio | **melhor cama de fundo** |
| `freesound_community-ambient` | 98s | −17,1 | 100/10/0 | 2,3 dB | médio | rumor grave puro; 24 kHz mas sem agudo, não faz diferença |
| `enternalrainsounds-light-rain-ocean-mix` | **900s** | −30,0 | 68/43/60 | 3,4 dB | ruim | espectro equilibrado, e 15 min cobrem 30 com 2 voltas |
| `stereogenicstudio-beach-02` | 156s | −29,8 | 54/79/30 | 3,8 dB | **bom** | melhor loop do lote |
| `loswin23-thunderstorm-2` | 194s | −24,5 | 80/57/19 | 3,7 dB | ruim | trovão *contido*, o único usável em sono |
| `soundsforyou-ocean-sea-soft-waves` | 180s | −25,8 | **6**/84/53 | 5,2 dB | médio | fino demais, só 6% de grave — precisa de EQ |
| `universfield-atmospheric-cinematic` | 92s | −17,4 | 45/89/7 | 4,9 dB | bom | **drone tonal, provavelmente musical — evitar** |
| `voicebosch-creaking-wood` | 38s | −31,0 | 36/66/66 | 21,2 dB | médio | **madeira rangendo — achado** |
| `freesound_community-wood-creaking` | 60s | −23,5 | 73/65/23 | 6,8 dB | ruim | idem, mais grave |
| `masterandmargarita-thunderstorm` | 728s | −16,5 | 84/54/3 | 7,3 dB | ruim | longo, mas com eventos |
| `pwlpl-heavy-thunderstorm` | 20s | −13,8 | 84/50/18 | 5,8 dB | ruim | curto, one-shot |
| `freesound_community-thunderstorm` | 121s | −17,6 | 82/57/4 | **59,6 dB** | ruim | estouros secos — **inutilizável em sono** |

## Conclusões

**A madeira rangendo é o melhor achado do lote.** Navio no mar range, e isso não dá
para sintetizar de forma convincente. Entra nas cenas de convés e de interior do
Pequod — camada que hoje não existe.

**Trovão é quase todo inadequado.** `freesound_community-thunderstorm` tem 59,6 dB de
desvio de envelope: são estouros secos. A pesquisa de áudio para sono é explícita
sobre dinâmica plana — trovão assim acorda quem estava adormecendo. Só o
`loswin23` (3,7 dB) é contido o bastante, e ainda assim distante e comprimido.

**`universfield-atmospheric-cinematic`**: 89% da energia no médio com pouco agudo é
assinatura de drone tonal, não de ambiente. Provavelmente é música. Fora, por ser
exatamente a categoria que o Content ID pega bem.

**Nada substitui a base sintética.** Nenhum arquivo tem `estab` abaixo de 1 dB nem
loop realmente limpo. O papel deles é **camada**, sobre o mar e a chuva de
`pipeline/ambiente.py`.

## Integração — implementada em 27/08/2026

`pipeline/s5_render.py::_escolher_gravado()` mistura uma camada gravada sobre a
sintética por CENA, a partir do `mar`/`chuva` que o `plano.json` já tem (sem
precisar de campo novo — o `ambiente.fonte_externa` no nível do vídeo continua
`null`, virou irrelevante). Regra: `chuva ≥ 0.5` usa `loswin23-thunderstorm-2`
(o único trovão "usável em sono" do lote); senão `mar ≥ 0.3` e não abafado usa
`enternalrainsounds-light-rain-ocean-mix` (mais longa e equilibrada, 900s). Nunca
os dois juntos. O ponto de início do arquivo varia por cena (`n * 137 % 400`)
pra não repetir sempre o mesmo trecho entre cenas.

Motivo da mudança: depois de ouvir a narração completa do video-02, a síntese
100% procedural soava "muito sintética" — camada gravada resolve isso sem abrir
mão da defesa de Content ID (ela é só camada, nunca sozinha, nunca em primeiro
plano — ver seção "Licença" acima).

`stereogenicstudio-beach-02` não está em `sons/` (só 11 dos 12 arquivos foram
recuperados) — não é usado na regra atual.

---

## Lote de deserto — 05/09/2026

Três arquivos baixados pelo Samuel depois da conversa sobre diversificar o
ambiente, para o video-04 (Lawrence da Arábia).

| arquivo | dur | LUFS | g/m/a | estab | veredito |
|---|---|---|---|---|---|
| `tanweraman-desert-wind-2` | 32s | −23,6 | 53/100/12 | 2,5 dB | **usar** — médio dominante, que é vento |
| `freesound_community-desert-monolith` | 85s | −35,2 | 100/93/17 | 8,6 dB | reserva — muito quieto e com eventos |
| `dragon-studio-desert-sand-dunes` | 282s | −30,2 | 100/6/1 | **1,1 dB** | **DESCARTADO — tonal** |

### O descarte é o achado do lote

O `sand-dunes` tinha **a melhor estabilidade de toda a biblioteca** (1,1 dB,
empatado com o `soul_serenity_sounds`) e 282 s de duração, que cobriria uma cena
inteira sem repetir. Era o melhor arquivo por todos os critérios antigos.

E é tonal: **1600 Hz com harmônicos em 3200 e 4800**. Isso é uma série
harmônica, que é a assinatura de um tom — provavelmente um pad sintetizado, não
uma gravação de campo. Mesmo caso do `universfield-atmospheric-cinematic`, que
este documento já mandava evitar.

**Content ID casa música, e drone tonal é o que ele casa.** Um arquivo de
biblioteca livre não protege contra reivindicação de terceiro que registrou o
material.

### A medição que quase deixou passar

O primeiro teste comparou cada pico contra a **mediana global** do espectro e
deu o veredito ao contrário: acusou o `sand-dunes` de tonal pelo motivo errado
(concentração larga de grave em 60–72 Hz, que é rumor) e absolveu o
`desert-monolith`.

O teste que serve compara o pico contra a **envoltória local** e depois procura
**harmônicos em 2×, 3× e 4×**. Tom tem harmônicos; rumor não. Sem essa segunda
passada o arquivo tonal teria entrado e o arquivo bom teria sido descartado.

Fica como regra: **avaliar tom por estrutura harmônica, nunca por altura de
pico.**
