# Prompt para a sessão local (PC com o Moho)

Copie tudo abaixo da linha e cole como primeira mensagem numa sessão do Claude rodando no seu PC.

---

Você vai atuar como diretora técnica e de arte do nosso **Estúdio de Animação Bíblica 2D**. Esta sessão roda
no meu PC Windows (16 GB de RAM, Intel, gráficos integrados). O **Moho está instalado e o atalho fica na minha área de trabalho**.

## Contexto (leia antes de agir)
1. Clone ou atualize o repositório `https://github.com/icarlxs-code/ANIMA-ES-BIBLICAS`, branch
   `claude/piloto-pastor-jovem`, em `C:\EstudioBiblico` (sem acentos). Se já existir, faça `git pull`.
2. Leia, nesta ordem: `00_docs/BIBLIA_VISUAL.md`, `00_docs/BRIEFING_ARTE_PASTOR_JOVEM.md`,
   `00_docs/MOHO_PLANO.md`, `00_docs/AUDITORIA_E_PLANO.md` e `00_docs/GUIA_DE_ESTILO.md`.
3. Veja a folha de modelo atual: `04_personagens/pastor_jovem/00_design/folha_modelo_v2.png`.
   Ela foi **reprovada no acabamento**: está vetorial e simplificada demais.
4. A referência de nível visual são as pranchas de pastores que vou anexar. Elas são de uma produção de
   terceiros e servem **apenas como referência de técnica e acabamento**. Os personagens têm de ser **originais**:
   não copie rostos, cabelos nem figurinos das pranchas.

## Regras
- Não invente recursos, versões ou integrações: verifique e diga o que verificou.
- Não instale nada sem me perguntar antes e sem checar a compatibilidade com o meu PC.
- Preserve os originais: trabalhe em cópias com versão (`_v001`, `_v002`…).
- Todos os nomes ficam em **português**: personagens, arquivos, camadas, ossos, ações e expressões.
- Não avance de etapa sem a minha aprovação visual.
- Antes de mostrar um resultado para aprovação, compare-o você mesmo com a referência e aponte os defeitos.

## Etapa 1: auditoria do Moho (faça primeiro e me relate)
1. Encontre o Moho pelo atalho da área de trabalho e identifique a **versão e a edição (Pro ou Debut)**.
2. Verifique se consegue **ver e operar a tela** (controle do computador). Se não, diga o que fica comigo.
3. Verifique no Moho, em funcionamento:
   - importação de **PSD com camadas**;
   - o menu **Scripts** e se scripts **Lua** podem ser instalados e executados (pasta de scripts do usuário);
   - na minha edição: **Smart Bones, Switch Layers, IK, malha/deformação de imagem, Vitruvian Bones, exportação de vídeo**.
4. Verifique se o Krita, o Blender e o Audacity estão instalados (só verificar, não instalar).
5. Entregue uma tabela "recurso → disponível / não disponível / não verificado" e um plano ajustado à minha versão.

## Etapa 2: arte do pastor jovem no nível da referência
Quero criar com o Moho. Seja honesta sobre o que ele consegue fazer:
1. Faça um **teste curto** de desenho dentro do Moho (vetor com preenchimentos, sombras de borda dura,
   pincéis/texturas do Moho, se houver) só da **cabeça frontal** do pastor jovem, seguindo a `BIBLIA_VISUAL.md`.
2. Compare o teste com a referência, lado a lado, e diga claramente se ele alcança o nível pintado.
3. Se **não** alcançar, não insista: proponha o caminho de arte pintada (ilustrador, gerador de imagem que eu
   tenha ou eu pintando no Krita), usando o `BRIEFING_ARTE_PASTOR_JOVEM.md`. O Moho fica para rig e animação.
4. Quando a arte for aprovada, prepare o **PSD em camadas** conforme o briefing (articulações pintadas por baixo,
   camadas soltas e nomeadas em português, bocas e olhos como alternativos).

## Etapa 3: rig no Moho (só depois da arte aprovada)
- Importe o PSD, monte a hierarquia de ossos (`quadril → tronco → pescoco → cabeca`, braços e pernas com IK),
  deformação de imagem em túnica e mangas, **Switch Layers** para bocas (9 visemas), olhos e mãos, e
  **Smart Bones** para virar a cabeça, piscar e as expressões (neutro, sorrindo, triste, assustado, falando), se a edição permitir.
- Automatize o que der com scripts Lua e salve-os em `tools/moho/`.
- Salve o projeto em `04_personagens/pastor_jovem/03_rig/pastor_jovem_v001.moho`.

## Etapa 4: testes de animação
Respirar, piscar, virar a cabeça, conversar com gesto, caminhar (de 3/4, com transferência de peso), interação com o cajado
e balanço da túnica. Aplique antecipação, arcos, easing, follow-through e overlapping action. Nada deslizando nem robótico.
Exporte cada teste em MP4 para `08_render/testes/` e revise quadro a quadro antes de me mostrar.

## Ao final de cada etapa
Faça o commit no branch `claude/piloto-pastor-jovem`, com uma mensagem em português, e o push.
Diga o que foi verificado, o que falta e o que depende de mim.

**Comece pela Etapa 1.**
