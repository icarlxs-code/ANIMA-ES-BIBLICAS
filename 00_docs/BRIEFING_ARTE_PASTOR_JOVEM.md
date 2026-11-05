# Briefing de arte: PASTOR JOVEM (personagem original)

Pode ser enviado a um ilustrador ou usado como roteiro de prompts num gerador de imagem.

## 1. Nível de acabamento (o que é obrigatório)
Concept art profissional de animação 2D para cinema, **pintura digital**, NÃO vetorial:
- Rosto estreito e alongado, **nariz longo e pesado** dominando o rosto, olhos amendoados com pálpebra superior grossa, sobrancelhas grossas, boca pequena.
- Anatomia estilizada e magra: pescoço longo, mãos e pés grandes, dedos desenhados um a um.
- **Luz forte da esquerda**: sombra própria de borda dura dividindo rosto, pescoço e roupas; luz de recorte clara nas bordas iluminadas.
- Tecidos pesados com dobras longas, sobreposição, sombra de contato e degradê escurecendo até a barra. Textura de pincel discreta.
- Contorno fino escuro no tom do material. Paleta terrosa. Fundo cinza em degradê com sombra longa no chão.
- **Não** aceitar: aparência infantil, vetor geométrico, olhos genéricos, roupas lisas.

> Use as pranchas de referência apenas para **técnica e acabamento**. O personagem é **original**:
> não copiar rosto, cabelo ou figurino de nenhuma figura das pranchas.

## 2. O personagem
Pastor da Judeia do século I, 15 a 16 anos, magro, ainda crescendo, braços longos. Atento, gentil, um pouco tímido.
- **Cabelo** escuro e cacheado, cobrindo metade das orelhas, com um **cordão de couro** fino na testa. Primeira penugem no queixo.
- **Túnica** de lã crua cor areia até abaixo do joelho, com uma faixa vertical tecida em marrom; mangas largas.
- **Colete de pele de carneiro** aberto, com a lã clara visível na borda.
- **Cinto de corda** com as pontas pendentes; **bolsa de couro** no quadril direito.
- **Cajado de madeira com gancho**, irregular, na mão esquerda. Sandálias de couro de tiras cruzadas.
- Paleta: pele `#c68a5c`/`#8e5532`, túnica `#d8c6a0`/`#a08a63`, colete `#efe5cf`/`#b8a582`, couro `#6e4527`, cabelo `#2a1b12`.

## 3. Entregas, em ordem (aprovar cada uma antes da próxima)
1. **Folha de modelo**: frontal, 3/4 e perfil, de corpo inteiro, em pose A relaxada (braços afastados do corpo).
2. **Expressões** (cabeça frontal): neutro, sorrindo, triste, assustado, falando.
3. **Mãos**: relaxada, aberta (gesto), apontando, segurando o cajado.
4. **Bocas para lip-sync**: repouso, A, E, I, O, U, MBP, FV, L.
5. **PSD para animação** (vista frontal e 3/4), em 300 dpi e com altura mínima de 3000 px. Camadas soltas e nomeadas em português:
   `cabelo_tras, cabeca_base, orelha_esq/dir, olho_esq/dir (aberto, semicerrado, fechado), iris_esq/dir,
   sobrancelha_esq/dir, nariz, boca_* (as 9 acima + sorriso, triste, susto), cabelo_frente, cordao, pescoco,
   tunica_tronco, tunica_saia, colete_esq/dir, cinto, pontas_cinto, bolsa, braco_sup_esq/dir,
   antebraco_esq/dir, mao_esq/dir (variações), coxa_esq/dir, canela_esq/dir, pe_esq/dir, cajado, sombra_chao`.
   **As articulações devem ser pintadas por baixo**: ombro, cotovelo, punho, joelho e pescoço, nas partes cobertas pela roupa, sem buracos ao girar.

## 4. Roteiro para gerador de imagem (se for o caso)
Gere primeiro a **folha frontal**. Depois use a imagem aprovada como referência de personagem em cada nova
geração, para manter o rosto. Texto-base (adapte à ferramenta):

> 2D animated film character design sheet, original character: a slender 15-year-old Judean shepherd boy,
> 1st century, curly dark hair with a thin leather cord on the forehead, long heavy stylized nose, narrow
> elongated face, almond eyes with heavy upper eyelids, thick eyebrows, small mouth, long thin neck, large hands,
> sand-colored wool tunic below the knees with a woven brown vertical stripe, open sheepskin vest with light
> fleece edge, rope belt, leather pouch, wooden shepherd's crook, leather sandals. Digital painting, cel shading
> with hard-edged shadows, strong light from the left, rim light, thin dark outlines, earthy palette, heavy
> fabric folds, gray gradient background with long cast shadow, full body, front view, A-pose.

Variações: troque *front view* por *three-quarter view* e depois por *side profile view*, e peça
*head expression sheet: neutral, smiling, sad, frightened, talking*.
Gerações não costumam vir com as camadas separadas: a separação e a reconstrução das articulações ficam comigo.
