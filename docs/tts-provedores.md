---
projeto: Canal de Sono Automatizado
assunto: TTS — provedores, preço, licença e o que realmente sabemos
data: 2026-09-03
status: pesquisa de mercado + medição nossa; NADA contratado
---

# Voz sintética: quanto custa, o que é bom, e o que ainda não sabemos

> Este documento é sobre o **motor** de voz. O contrato de escrita — ritmo de
> frase, termos banidos, concretude — está em [voz.md](voz.md) e não muda com
> o provedor.

## A conclusão, antes dos detalhes

**Nenhum benchmark público responde a nossa pergunta.** Todos os rankings de
2026 que encontrei medem **inglês**. O nosso produto hoje é pt-BR, e a
qualidade de um modelo em inglês não transfere para português — timbre,
prosódia e, principalmente, o tratamento das nasais (`ão`, `ãe`, `õe`) e da
palatalização de /t/ e /d/ antes de /i/ são exatamente onde TTS multilíngue
costuma quebrar.

Então a recomendação não é "compre X". É: **rode uma prova cega em pt-BR com o
nosso próprio roteiro antes de assinar qualquer coisa.** O método já provou ser
o que funciona neste projeto — o Samuel achou de ouvido o `aecho` que cinco
medições minhas declararam limpo.

## Volume real, medido (é o que define a faixa de preço)

| | caracteres |
|---|---|
| video-02 (Moby Dick, 41 min) | 18.007 |
| video-03 (farol grego, 30 min) | 11.979 |
| **média por vídeo** | **~15.000** |

A 10–13 vídeos/mês: **150–195 mil caracteres/mês** em pt-BR.
Bilíngue pt+en: **300–390 mil/mês**.

Esse número importa porque quase todo provedor cobra por caractere, e as faixas
de assinatura caem bem perto dele.

## Preço, a 13 vídeos/mês

Câmbio de 03/09/2026: **US$ 1 ≈ R$ 5,10**. `[SECUNDÁRIO — confirmar]`

| opção | licença | pt-BR? | US$/mês | R$/mês |
|---|---|---|---|---|
| **Kokoro-82M** (atual, local) | Apache-2.0 | 3 vozes | **0** | **0** |
| **Chatterbox** (local) | MIT | sim (`language_id="pt"`) | **0** | **0** |
| **Fish Audio** API | comercial no plano pago | sim | ~2,90 | ~15 |
| Fish Audio Plus (250k) | idem | sim | 15 | ~77 |
| ElevenLabs Creator (121k) | comercial | sim | 22 | ~112 |
| **ElevenLabs Pro (600k)** | comercial | sim | 99 | ~505 |

Duas observações que mudam a leitura da tabela:

**O Creator não serve.** 121 mil créditos não cobrem nem os 150–195 mil de
pt-BR sozinho. Quem sobe de degrau no ElevenLabs sobe direto para o Pro, de
US$ 99 — não existe meio-termo útil para o nosso volume.

**O Fish Audio cobra por uso, não por assinatura.** US$ 15 por milhão de
caracteres. Nos nossos 195 mil/mês isso dá **US$ 2,90** — 34× mais barato que o
ElevenLabs Pro. Mesmo bilíngue (390 mil) fica em US$ 5,85.

## O que os benchmarks de 2026 dizem — e o que eles não dizem

**ElevenLabs** continua sendo a referência de qualidade em inglês. MOS 4,6,
descrito como indistinguível de locutor humano em teste cego, e apontado como o
melhor especificamente em **narração longa**, que é o nosso caso.

**Fish Audio S2 Pro** aparece em 1º lugar num teste A/B cego, com pontuação
Bradley-Terry 1,7× a do segundo colocado, custando 11× menos que o ElevenLabs
Multilingual v2. Se esse resultado se sustentar em português, é a melhor
relação custo-benefício do mercado por uma margem grande.

**Chatterbox** (Resemble AI, **MIT**) marcou 63,75% de preferência contra o
ElevenLabs em teste cego. É local, gratuito e sem amarra de licença.

**Kokoro-82M**, o que já usamos, aparece com 1.060 de Elo — à frente de Maya1
(3B), Higgs Audio V3 (4B), Chatterbox e VibeVoice 7B — com apenas 82M de
parâmetros.

**Higgs Audio V3** tem 100+ idiomas e WER publicado, mas **licença não
comercial**. Fora, pelo mesmo motivo que o XTTS-v2/Coqui ficou fora.

### As duas contradições que eu não vou esconder

1. Uma fonte põe o Kokoro **à frente** do Chatterbox em Elo; outra põe o
   Chatterbox batendo o ElevenLabs em preferência. São benchmarks diferentes
   medindo coisas diferentes, e nenhum é auditável por nós.
2. Todos são **em inglês**. Nenhum diz nada sobre pt-BR.

Isso não é ruído a ser resolvido lendo mais artigo. É o motivo pelo qual a
próxima ação é testar, não comprar.

## O que já temos construído para testar

- `fase0/video-01/test_chatterbox.py` — Chatterbox multilíngue com
  `language_id="pt"`, rodando em `mps` (a GPU do próprio Mac). **Já funcionou.**
- `fase0/video-01/test_chatterbox_clone.py` — clonagem de voz.
- `estudio/dados/personas.json` — 4 personas, todas com `en: TBD`.
- `pipeline/s2_tts.py` — já tem `FATOR_PAUSA_INICIO`/`FIM`, o mecanismo de
  lentidão por pausa crescente que substituiu o `speed` baixo.

Falta: `fase0/_vozes-candidatas/`, que o `personas.json` cita e **não existe**.

## A prova cega proposta

Barata e decisiva. O critério é o seu ouvido, não o meu medidor.

1. Escolher **um trecho de 90 s** do roteiro do video-02 — já aprovado de
   ouvido, então serve de linha de base honesta.
2. Gerar o mesmo trecho em: Kokoro `pm_santa` (atual), Chatterbox pt,
   Fish Audio, ElevenLabs. Os dois pagos têm camada gratuita suficiente para
   90 s.
3. Nomear os arquivos `A`, `B`, `C`, `D` — **sem dizer qual é qual**.
4. Ouvir no fone e no celular, à noite, no volume em que se usa para dormir.
5. Só depois revelar os nomes.

O que julgar, em ordem: **respiração e pausa** (é o que separa "leitura" de
"contação"), **nasais e sibilância** (onde português quebra), **estabilidade ao
longo do trecho** (modelo que degrada aos 60 s é inútil para 40 min), e só por
último timbre.

## Recomendação

**Não assinar nada agora.** Fazer a prova cega. Se o Kokoro perder feio, o
próximo passo é o **Fish Audio**, não o ElevenLabs — porque a US$ 2,90/mês o
erro é barato de desfazer, e a US$ 505/ano o ElevenLabs precisa provar que a
diferença é audível **em português** e que ela se converte em retenção.

E há um argumento de arquitetura que vale mais que os dois preços: Kokoro e
Chatterbox rodam **offline, com licença livre**. Um canal automatizado que
depende de API de voz tem um estágio que morre se o fornecedor mudar de termos —
a mesma lógica que já tirou o XTTS-v2 do projeto.

---

Fontes de preço e benchmark (todas `[SECUNDÁRIO]`, comparativos de terceiros):
[Notevibes](https://notevibes.com/best-ai-voice-generator-for-audiobooks) ·
[Flexprice](https://flexprice.io/blog/elevenlabs-pricing-breakdown) ·
[Smallest.ai](https://smallest.ai/blog/fish-audio-pricing-plans-api-billing-commercial-use-in-2026) ·
[TextToLab](https://texttolab.com/blog/fish-audio-pricing) ·
[Pinggy](https://pinggy.io/blog/best_open_source_self_hosted_text_to_speech_models/) ·
[FindSkill](https://findskill.ai/blog/best-open-source-tts-2026/) ·
[localaimaster](https://localaimaster.com/blog/best-local-tts-models)
