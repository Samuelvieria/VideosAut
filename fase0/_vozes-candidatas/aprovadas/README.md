# Configurações aprovadas de ouvido

Guardadas porque foram julgadas pelo Samuel, não por medição minha.

## B — escolhida para o video-03 (04/09/2026)

`B_escolhida_video03.wav`

```
voice pm_santa · speed 0.75
pausa_respiro_s   0.45   (padrão, como o video-02)
pausa_paragrafo_s 0.30   (padrão, como o video-02)
pausa_frase_s     1.2
vogal_final_pt    true   (æ -> ɐ)
```

Ela existe porque ele disse que *"a voz do video 2 estava melhor"*. Ao comparar
as cinco diferenças entre os dois vídeos, apareceu que eu tinha **triplicado**
`respiro` e `parágrafo` sem nunca pedir julgamento — foi mudança minha para
comprar duração, e ele só havia avaliado a pausa entre frases.

Custo de voltar ao padrão: **3%** de duração. Os respiros de `...` e de
parágrafo são poucos comparados a fronteiras de frase, então quase não pesam.

## D — guardada a pedido

`D_padrao_v02_speed075.wav`

```
voice pm_santa · speed 0.75
pausa_respiro_s   0.45
pausa_paragrafo_s 0.30
pausa_frase_s     0.0    <- sem pausa entre frases
vogal_final_pt    false  <- mantém o æ do espeak
```

É o video-02 inteiro, só com a velocidade nova. Palavras dele: *"salva a d pq
ficou bom também"*. Não foi escolhida para o video-03 porque sem a pausa entre
frases o vídeo cairia de 76 para ~50 min, abaixo do piso de 65 que
`docs/mercado.md` §2 encontrou.

**Serve como ponto de partida para um vídeo curto**, se o canal um dia testar
esse formato — aí a duração não é restrição e a fluidez contínua é vantagem.
