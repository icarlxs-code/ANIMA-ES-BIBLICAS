# Guia de estilo e de camadas dos personagens

## Técnica de ilustração (a partir das pranchas em `01_referencias/estilo/`)

- **2D, cel shading de duas tonalidades** com borda dura. Luz principal vinda da **esquerda-alto**; a sombra divide rosto, pescoço e roupas em blocos (metade do rosto em sombra).
- **Sem contorno preto.** As formas se separam pelo valor; no máximo, uma borda fina no tom da sombra.
- **Rosto**: nariz longo e marcado, que é o traço mais característico; olhos amendoados com pálpebra superior pesada e íris escura; sobrancelhas grossas; boca pequena.
- **Proporções alongadas**: cabeça pequena (cerca de 1/7,5 da altura), membros longos, mãos grandes com dedos articulados e pés com sandálias de tiras.
- **Roupas**: túnicas com dobras verticais longas, escurecendo em **degradê até a barra**; tecidos pesados (estolas, mantos) com as pontas pendentes.
- **Paleta terrosa** (areia, linho, marrom, oliva). Cores nobres só para reis e sacerdotes (púrpura, ouro, azul).
- **Fundo** cinza em degradê (escuro no alto) e **sombra projetada** longa no chão.
- Em pose de personagem, braços levemente afastados do corpo (A-pose relaxada), o que ajuda o rig.

> As pranchas são de uma produção de terceiros. Elas servem como **referência de técnica**. Nossos
> personagens devem ser **desenhos originais** nessa técnica, e não cópias ou decalques das figuras
> das pranchas.

## Nomes: sempre em português

Personagens, pastas, arquivos, animações, expressões e cenas ficam em português (`pastor_jovem`,
`caminhada_frente`, `conversa`, `alegre`). **Exceção técnica:** os nomes das **camadas** (e, portanto,
dos ossos e slots) seguem a convenção do AutoRig, que só reconhece inglês. Eles não aparecem na história.

| Camada (Krita) | Parte | Camada (Krita) | Parte |
| --- | --- | --- | --- |
| `head` | cabeça (com orelhas) | `upperarm_l` / `_r` | braço |
| `hair`, `hair_back` | cabelo da frente / de trás | `forearm_l` / `_r` | antebraço / manga |
| `eye_l`, `eye_l_closed` | olho aberto / fechado | `hand_l` / `_r` | mão |
| `pupil_l` | íris/pupila | `thigh_l` / `_r` | coxa |
| `brow_l` | sobrancelha | `shin_l` / `_r` | canela |
| `nose` | nariz | `foot_l` / `_r` | pé + sandália |
| `mouth_rest`, `mouth_A`, `_E`, `_I`, `_O`, `_U`, `_MBP`, `_FV`, `_L` | 9 bocas (visemas) | `skirt` | túnica abaixo da faixa |
| `neck` | pescoço | `belt` | faixa/cinto |
| `torso` | túnica acima da faixa | `scarf` | estola/echarpe |
| `beard` (futuro) | barba | `staff` | cajado |

Regras: `_l`/`_r` = lado **do personagem** (o esquerdo dele fica à direita da imagem). Sobreponha
as articulações (desenhe um pouco a mais por baixo). Camadas soltas, sem grupos. Bocas e olho
fechado podem ficar ocultos. Exporte do Krita como **.psd**.

## Biblioteca de personagens (nomes em português)

| Arquivo de referência | Personagens / variações |
| --- | --- |
| `pastores.jpg` | pastor adulto, **pastor jovem (piloto)**, pastor idoso |
| `maria_e_jose.jpg`, `maria_casa_trabalho_viagem.jpg` | Maria: casa, trabalho, viagem |
| `jose_trabalho_viagem_dormir.jpg` | José: trabalho, viagem, dormir |
| `jesus_comum_disfarce_glorificado.jpg` | Jesus: comum, com manto (disfarce), glorificado |
| `maria_madalena.jpg` | Maria Madalena: atormentada, véu escuro, restaurada |
| `herodes_pilatos_caifas.jpg` | Herodes, o Grande; Pôncio Pilatos; Caifás |
| `soldados_romanos.jpg` | soldado com lança, soldado de túnica, centurião |
| `magos_do_oriente.jpg` | magos do Oriente e servo (a Bíblia não diz quantos eram: Mt 2:1-11) |

Plano (ainda não testado): as variações de roupa do mesmo personagem viram **skins** do mesmo rig, para reaproveitar todas as animações.
