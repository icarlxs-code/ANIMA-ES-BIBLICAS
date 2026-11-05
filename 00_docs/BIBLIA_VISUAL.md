# Bíblia visual da produção

As pranchas de `01_referencias/estilo/` são **referência de linguagem visual** (produção de terceiros, sem
licença). Todos os personagens da produção são **originais**: seguem a técnica descrita abaixo, mas
com rostos, figurinos e silhuetas próprios.

## 1. Linguagem visual (análise das pranchas)

**Proporção**
- Figura adulta com cerca de 7,5 cabeças; o jovem tem 7. Crânio pequeno, rosto alongado, pescoço fino e longo.
- Ombros estreitos nos jovens e largos nos trabalhadores. Membros longos, mãos e pés **grandes** (expressivos), pernas finas.
- Postura de prancha: em pé, peso levemente num dos lados, braços afastados do corpo e mãos semiabertas.

**Rosto**: o traço de identidade.
- **Nariz longo e pesado**, do meio das sobrancelhas até perto da boca, com a ponta arredondada. É o elemento dominante.
- Olhos amendoados pequenos, **pálpebra superior grossa e escura**, íris castanha grande, olhar um pouco "cansado". Olheiras discretas.
- Sobrancelhas grossas e retas, próximas dos olhos.
- Boca pequena, o lábio inferior marcado por sombra; queixo estreito.
- Orelhas médias, baixas, muitas vezes parcialmente cobertas.

**Luz e cor**
- Luz principal **da esquerda-alto**. Sombra própria em **bloco de borda dura**: metade do rosto, um lado do pescoço, as dobras.
- Duas ou três tonalidades por material (luz, sombra, oclusão), sem degradê suave na pele.
- Tecidos: **degradê vertical** que escurece até a barra, mais **arrastos verticais de pincel** (textura de pintura).
- Contorno **fino e escuro**, no tom da sombra do material (não preto puro). Uma luz de borda clara aparece às vezes na silhueta.
- Paleta terrosa: linho, areia, ocre, marrom, oliva acinzentado. Saturação só em reis e sacerdotes (púrpura, azul, ouro).
- Fundo cinza em degradê (escuro no alto) e **sombra projetada longa** no chão, para a direita.

**Figurino**
- Túnicas de lã ou linho com dobras verticais longas; mangas largas que caem do antebraço.
- Camadas: túnica, manto ou colete, cinto de corda ou faixa, bolsa de couro. Sandálias de tiras com os dedos à mostra.
- Tecidos pesados: as pontas pendem, e a sobreposição gera sombra de contato.

## 2. Ficha do personagem-piloto: PASTOR JOVEM (original)

| Item | Definição |
| --- | --- |
| Idade / tipo | 15 a 16 anos, magro, ainda crescendo; ombros estreitos, braços longos |
| Proporção | 7 cabeças; mãos grandes para o corpo (traço de adolescente) |
| Rosto | Rosto oval alongado; nariz longo com a ponta arredondada; olhos grandes e atentos (curiosidade, timidez); sobrancelhas grossas com a parte interna levemente erguida; buço e primeira penugem no queixo |
| Cabelo | Cacheado, escuro, volumoso no alto, cobrindo as orelhas pela metade; **cordão de couro** na testa |
| Figurino | Túnica de lã crua (areia) até abaixo do joelho, com uma **faixa vertical tecida** em marrom; **colete de pele de carneiro** (lã clara na borda); **cinto de corda** com as pontas pendentes; **bolsa de couro** no quadril direito |
| Objeto | **Cajado com gancho** (cajado de pastor) na mão esquerda |
| Calçado | Sandálias de couro com tiras cruzadas |
| Paleta | pele `#c68a5c` / sombra `#8e5532`; túnica `#d8c6a0` / `#a08a63`; colete `#efe5cf` / `#b8a582`; couro `#6e4527` / `#45291a`; cabelo `#2a1b12` |
| Personalidade | Atento, gentil, um pouco inseguro; reage com o corpo inteiro (quem se espanta primeiro) |

## 3. Camadas para o Moho (nomes em português)

O Moho não depende de nomes de camada, então todas ficam em português. Cada parte é uma camada de imagem
num PSD, agrupada por região:

```
pastor_jovem.psd
├─ sombra_chao
├─ braco_esq/  (lado do PERSONAGEM)  braco_sup_esq, antebraco_esq, mao_esq
├─ cajado
├─ perna_esq/  coxa_esq, canela_esq, pe_esq      perna_dir/ coxa_dir, canela_dir, pe_dir
├─ tunica_saia,  tunica_tronco,  faixa_tunica,  colete,  cinto,  pontas_cinto,  bolsa
├─ pescoco
├─ cabeca/     cabelo_tras, cabeca_base, orelha_esq, orelha_dir,
│              olho_esq (switch: aberto, semicerrado, fechado), iris_esq, palpebra_esq, sobrancelha_esq,
│              (idem _dir), nariz,
│              boca (switch: repouso, A, E, I, O, U, MBP, FV, L, sorriso, triste, susto),
│              cabelo_frente, cordao
└─ braco_dir/  braco_sup_dir, antebraco_dir, mao_dir (switch: relaxada, aberta, apontando, punho)
```

Regras de corte (fidelidade): as partes se **sobrepõem** nas articulações (ombro, cotovelo, punho, joelho)
com a forma redonda desenhada por baixo; o que fica escondido pela roupa é pintado também, para não abrir
buracos no movimento. A sombra de contato fica na camada de cima.

## 4. Critério de aprovação do piloto

1. A silhueta e as proporções leem como a linguagem das pranchas, e não como um desenho educativo infantil.
2. O nariz, os olhos e a luz lateral dão personalidade ao rosto.
3. As roupas têm dobras, volume, degradê e textura.
4. O mesmo rosto se mantém reconhecível nas 5 expressões.
5. Só depois disso: vistas 3/4 e lateral, separação final em camadas e rig no Moho.
