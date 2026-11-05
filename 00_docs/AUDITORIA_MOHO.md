# Auditoria do Moho no PC local (Etapa 1)

Data: 2026-11-05. Sessão local no PC Windows (16 GB, Intel, gráficos integrados).

## Como foi verificado
Esta sessão **não tem controle da tela** (as ferramentas de computer use não estão disponíveis), então nada
foi clicado dentro do Moho. Tudo abaixo vem de arquivos, do executável e de um teste por linha de comando.

## Moho
- Atalho `Moho 14.lnk` (área de trabalho pública) → `C:\Program Files\Moho 14\Moho.exe`.
- Versão do arquivo: **14.5** (Lost Marble LLC). Programas instalados: "Moho 14.5".
- Edição: o Moho roda como **Pro**: as preferências ficam em `AppData\Roaming\Lost Marble\Moho Pro\14` e a pasta de
  conteúdo do usuário é `C:\Users\User\Desktop\Moho Pro` (criada hoje às 09:53).
- **Licença: provável modo de avaliação (Trial).** O teste de render por linha de comando
  (`Moho.exe -r arquivo.moho -f PNG/MP4 -o saída`) terminou com código 0 e **sem gerar nenhum arquivo**. O próprio
  programa tem as mensagens "o render por linha de comando não pode ser iniciado porque o Moho está em modo Trial"
  e "é um recurso só do Pro". Confirmar em *Ajuda ▸ Sobre o Moho* (aparece "Computer ID (Trial Mode)" se for trial).
- Formato `.moho`: um ZIP com `Project.mohoproj` (JSON) e `preview.jpg`, verificado num tutorial.

## Tabela de recursos
| Recurso | Situação | Evidência |
| --- | --- | --- |
| Versão / edição | 14.5 Pro (licença provavelmente trial) | executável, pasta de preferências, teste da linha de comando |
| Controle da tela pela IA | **não disponível** nesta sessão | nenhuma ferramenta de computer use carregada |
| Importação de PSD com camadas | existe no programa, **não testada** | mensagens de PSD (só RGB; CMYK, Lab, tons de cinza e bitmap recusados) |
| Menu Scripts / Lua | disponível | 65 scripts de menu, 46+15 de ferramenta, 5 módulos; *Scripts ▸ Install Script...* |
| Pasta de scripts do usuário | existe, vazia | `C:\Users\User\Desktop\Moho Pro\Scripts\{Menu,Tool,Utility,Modules}` |
| Smart Bones | existe no programa, não testado | "Make Smart Bone Dial", "Smart bone timeline" |
| Switch Layers | existe, não testado | `lm_switch_layer.lua`, canal "Switch Layer", lip-sync em switch |
| IK | existe, não testado | "Inverse Kinematics" na ferramenta Selecionar Osso |
| Malha / deformação de imagem | existe, não testado | Smart Warp, "Create Mesh Layer", "Triangulate 2D Mesh" |
| Vitruvian Bones | existe, não testado | menu Ossos ▸ ativar/desativar Vitruvian Bones |
| Lip-sync automático | existe, não testado | Rhubarb incluído em `Resources\Rhubarb` |
| Exportação de vídeo pela interface | existe, não testada | formatos MPEG-4/H.264 nas strings; ffmpeg (avcodec-61) incluído |
| Render por linha de comando | **não funcionou** | sem saída; bloqueado em Trial/Debut |
| Krita | instalado, 5.3.4.1 | `C:\Program Files\Krita (x64)` |
| Blender | instalado, 5.2.2 | `C:\Program Files\Blender Foundation\Blender 5.2` |
| Audacity | **não instalado** | não está em Program Files nem em Programas instalados |
| FFmpeg | instalado, 9.0.2 (winget) | no PATH |

"Existe no programa" = o recurso aparece nos menus e nas mensagens do Moho 14.5. Sem a tela, não pude
confirmar que a sua licença o libera.

## Plano ajustado
1. **Você**: abre *Ajuda ▸ Sobre* e diz se é Trial (e quantos dias restam) ou Pro ativado. Se for trial, só a compra
   do Pro destrava o render por linha de comando. O trial também pode expirar no meio do rig.
2. **Controle da tela** (opcional): ative *Configurações ▸ Este computador ▸ Computer use* no app do Claude. Assim eu
   testo os menus e as ferramentas. Sem isso, cada teste na interface fica com você, com um roteiro meu.
3. **Automação sem a tela**: scripts Lua em `tools/moho/`, que você instala em *Scripts ▸ Install Script...* e
   executa no menu. Alternativa a testar: gerar ou editar o `Project.mohoproj` (JSON) direto numa cópia versionada.
4. **Render dos testes**: pela interface (*Arquivo ▸ Exportar animação*), feito por você. Ou eu exporto quadros PNG e
   monto o MP4 com o ffmpeg, se o render por linha de comando for liberado.
5. **Áudio**: o Audacity não está instalado. Para cortar diálogos dá para usar o ffmpeg, ou você decide se instala.
6. **Conflito de nomes**: o `GUIA_DE_ESTILO.md` manda camadas em inglês (exigência do AutoRig do Rigby2D). No Moho isso não é
   necessário, então o PSD do Moho usará os nomes em português da `BIBLIA_VISUAL.md`, seção 3.
