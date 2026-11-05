# Moho: auditoria pendente e plano

## O que NÃO pude verificar
O Moho está no seu PC (TELEMARKETING-JG), que não oferece pastas a sessões na nuvem. Não sei a versão
instalada nem a edição (Debut ou Pro), e não há integração MCP com o Moho conhecida ou testada.
Nada abaixo foi testado por mim.

## Verifique no seu Moho (2 minutos)
1. *Ajuda ▸ Sobre*: versão e edição (**Pro** ou **Debut**). Vários recursos de rig avançado, como Smart Bones, são do Pro: confirme na lista de recursos da sua edição.
2. *Arquivo ▸ Importar*: há a opção de PSD com camadas?
3. *Scripts* no menu: os scripts Lua estão disponíveis? (É a via de automação: a IA escreve os scripts e você os executa.)

## Como a IA participa (realista)
| Etapa | Quem faz | Como |
| --- | --- | --- |
| Design e folhas de modelo | IA | SVG em camadas (`tools/desenho_pastor_jovem.py`), aprovação sua |
| PSD em camadas, com nomes em português | IA | conversão automática do SVG (cada `<g id>` vira uma camada) |
| Importação no Moho | você | *Importar PSD* |
| Ossos, Smart Bones, Switch Layers | você, com roteiro da IA | ficha de rig com hierarquia, pivôs e coordenadas; scripts Lua quando o Moho permitir |
| Animação | você + IA | a IA planeja chaves, tempos e curvas por plano e revisa os renders que você exportar |

## Próximos passos
1. Você aprova (ou corrige) o rosto e as proporções da folha v2.
2. Vistas 3/4 e lateral + mãos (aberta, apontando, segurando).
3. Separação final em PSD com articulações reconstruídas por baixo (ombro, cotovelo, punho, joelho).
4. Ficha de rig para o Moho e teste de caminhada e fala.
