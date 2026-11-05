# Etapa 2: teste de desenho no Moho e caminho de arte pintada

## 1. Teste no Moho (cabeça frontal)
- Gerador: `tools/moho/gerar_teste_cabeca.py` → `04_personagens/pastor_jovem/05_revisao/teste_moho/teste_cabeca_moho_v002.moho`
  (uma camada vetorial nativa, `cabeca_teste`, com 103 formas: preenchimentos chapados, sombras de borda dura recortadas
  na forma, luz de borda, fundo em faixas).
- Prévia das formas (raster local, não é o render do Moho): `previa_formas_v002.png`. Lado a lado: `comparacao_v002.png`.
- Render feito pelo próprio Moho: pendente. Abra o arquivo no Moho e use *Scripts ▸ Estudio ▸ Renderizar quadro (PNG)*
  (script em `tools/moho/estudio_renderizar_quadro.lua`, já copiado para a pasta de scripts do usuário).

### Comparação com a referência (minha avaliação)
| Critério | Referência | Teste vetorial |
| --- | --- | --- |
| Volume | modelado por tons pintados, transição suave no osso da face, nas olheiras e no pescoço | blocos chapados; a face lê como um recorte plano |
| Bordas | bordas duras **e** suaves misturadas; o contorno varia de espessura | todas as bordas iguais, geométricas |
| Cabelo | mechas pintadas com luz e sombra | massa escura com "cês" carimbados; não lê como cacho |
| Olhos | íris com gradação, pálpebra com volume, luz refletida | adesivos planos |
| Textura | grão de pintura no fundo e na pele | nenhuma |
| Conclusão | | **não alcança** o nível pintado. Fica no mesmo patamar da folha v2 reprovada |

Os efeitos do Moho 14.5 (degradê, sombreado, halo, textura, manchado, pincéis de linha) melhorariam um pouco, mas não
substituem a pintura à mão. O gargalo também é meu: desenhar por coordenadas não chega a uma ilustração pintada.
**O Moho fica para rig e animação.**

## 2. Caminho de arte pintada (escolha sua)
| Opção | O que verifiquei | Prós | Contras |
| --- | --- | --- | --- |
| A. Gerador de imagem que você já usa: ChatGPT, Gemini ou Grok | atalhos na sua área de trabalho; a folha que você mandou tem cara de ter sido gerada assim (não verificado) | rápido; já chega no estilo | rosto inconsistente entre vistas; resolução de ~1536 px; nada vem em camadas; a IA não opera esses apps nesta sessão (você cola os prompts) |
| B. Você pinta no Krita 5.3.4.1 (instalado) | Krita instalado | controle total; PSD nativo com camadas | tempo e habilidade de pintura |
| C. Ilustrador | — | melhor qualidade e consistência | custo e prazo |
| Geração local de imagem | **inviável**: gráficos integrados, sem GPU dedicada | — | — |

Recomendação: **A para a folha de modelo e as expressões** e, depois de aprovada, **A + Krita** para as partes do PSD.
Eu separo as camadas e reconstruo as articulações; você retoca no Krita o que eu não conseguir deixar limpo.

## 3. Prompts (cole no gerador e anexe a folha de referência como imagem de ESTILO)
Personagem = ficha da `BIBLIA_VISUAL.md` (cabelo cacheado com cordão de couro, colete de pele de carneiro, cinto de corda,
bolsa, cajado com gancho). Estilo = a folha enviada. Não copie rosto, cabelo, estola nem figurino da folha.

**Folha frontal**
> Use the attached image ONLY as a reference for painting technique, lighting and finish, not for the character design.
> Original character: a slender 15-year-old Judean shepherd boy, 1st century. Tight dark curly hair, voluminous on top,
> half covering the ears, a thin leather cord tied around the forehead. Narrow elongated oval face, long heavy nose with a
> rounded tip, large attentive almond eyes with heavy upper eyelids, thick eyebrows with the inner ends slightly raised,
> small mouth, faint first fuzz on the upper lip and chin, long thin neck, large hands. Sand-colored raw wool tunic below the knees with
> one woven brown vertical stripe, wide sleeves; open sheepskin vest with light fleece edges; rope belt with hanging ends;
> leather pouch on his right hip; irregular wooden shepherd's crook with a hook in his left hand; crossed-strap leather
> sandals. NO scarf. Painted 2D animated-film character art, hard-edged cel shadows with soft painted transitions, warm
> light from the upper left, thin dark outlines in the color of each material, subtle brush texture, earthy palette.
> Full body, front view, relaxed A-pose with arms slightly away from the body, plain gray gradient background, long
> cast shadow on the floor to the right. Single character, no text.

**Variações** (sempre anexando a frontal aprovada como referência de personagem): troque *front view* por
*three-quarter front view* e depois *side profile view*. Expressões: *head close-up expression sheet, same character:
neutral, smiling, sad, frightened, talking*. Bocas: *mouth shapes for lip sync: rest, A, E, I, O, U, M-B-P, F-V, L*.

### Como eu vou revisar cada geração
1. O personagem segue a ficha (cachos, cordão, colete, corda, bolsa, gancho, sem estola).
2. É original em relação às pranchas de terceiros.
3. O rosto é o mesmo entre as vistas e as expressões.
4. Mãos com cinco dedos, pés e sandálias corretos.
5. Resolução: o briefing pede 3000 px de altura. Os geradores costumam entregar menos. Para 1080p, ~2000 px de corpo inteiro bastam.
