# Auditoria técnica e plano: Estúdio de Animação Bíblica

Data: 2026-11-05 · Rigby2D **0.4.3** (release mais recente, tag `v0.4.3`)

## 1. Onde cada coisa roda (importante)

| Ambiente | O que é | Situação |
| --- | --- | --- |
| **Sessão na nuvem (Linux, 4 vCPU, 15 GB)** | Onde a IA trabalhou nesta etapa | Rigby2D 0.4.3 (servidor MCP) instalado e **testado** |
| **Seu PC Windows (TELEMARKETING-JG)** | 16 GB, Intel, gráficos integrados | **Não acessível** desta sessão: o Remote Control lista 3 pastas, mas nenhuma é oferecida a sessões na nuvem. Nada foi instalado nele. |

O servidor MCP do Rigby2D é Node.js puro, sem dependência de GPU, e funciona igual no Windows. Tudo o que foi validado aqui vale para o Claude Desktop no seu PC.

## 2. O que foi VERIFICADO (com teste)

- Documentação oficial lida no repositório (`docs/mcp.md`, `mcp-tools.md`, `autorig.md`, `lip-sync.md`, `importing-art.md`, `file-formats.md`). O site rigby2d.com está bloqueado na rede desta sessão; o conteúdo é o mesmo.
- Conexão MCP real (JSON-RPC por stdio, protocolo `2025-06-18`): servidor `rigby2d 0.4.3`, **41 ferramentas** (lista em `mcp_tools_list.json`).
- O bloqueio de pastas funciona: um caminho fora de `--root` é recusado.
- Ferramentas testadas com sucesso: `detect_parts`, `autorig`, `rename_bone`, `inspect_project`, `describe_rig`, `describe_animation`, `sample_pose`, `validate_project`, `batch_edit` (com `add_animation`, `set_bone_key` e `set_attachment_key`), `save_pose`, `add_face_control`, `delete_animation`, `add_audio_track`, `lip_sync` e `export_sprite_sheet`.
- Salvamento: cada edição é salva atomicamente; `validate_project` passa (estrutura, imagens, JSON e `.skel` OK).

## 3. Limitações encontradas (e como foram contornadas)

| # | Limitação no Rigby2D 0.4.3 | Contorno adotado |
| --- | --- | --- |
| 1 | O importador de PSD cria **um slot por camada**; bocas e olhos alternativos não vão para o mesmo slot (a documentação diz que vão). Sem isso, o `lip_sync` não funciona. | `tools/rigby_agrupar_alternativos.py` junta os slots numa **cópia**, antes de animar, e o resultado é validado pelo MCP. |
| 2 | Antes da 1ª chave de anexo, o runtime já mostra o valor dessa chave (olho fechado desde t=0). | Chave explícita de "aberto"/"repouso" em t=0 em toda animação. **Reportar ao projeto.** |
| 3 | O MCP não expõe a direção de dobra nem o `softness` do IK, e `run_script` não edita constraints. | A mesma etapa da linha 1 ajusta `bendPositive` e `softness` (cotovelo junto ao corpo no gesto, sem "estalo" na extensão). |
| 4 | `slot.bone` não pode ser alterado por script. | Usar `roles` do AutoRig (`scarf → torso`, `staff → extra`, que caiu em `hand_l`). |
| 5 | Uma túnica longa como "pelve" põe o quadril no meio da saia (coxas invertidas). | `skirt → tail`: quadril correto e túnica como cadeia `robe_1..3` com malha, que dá o *follow-through* do tecido. |
| 6 | O cajado herda a rotação do antebraço sob IK. | `tools/compensar_rotacao.py` mede com `sample_pose` e grava a compensação (desvio < 0,2°). |
| 7 | **Renderizar MP4/WebM não existe no MCP** (só no editor: *File ▸ Render animation*). | Testes: `export_sprite_sheet` (quadros) + ffmpeg (`tools/montar_sequencia.py`). Final: render do editor. |
| 8 | O AutoRig só reconhece nomes de camada em **inglês**. | Camadas e ossos com nomes técnicos em inglês; todo o resto em português (veja o guia de estilo). |

## 4. Hardware (16 GB, Intel, iGPU)

- Rigby2D: editor 2D (Tauri/WebView2, Windows 10/11); o MCP não usa GPU. **Adequado.**
- Krita: adequado para pintar em camadas (use telas de ~2000×3400 px por personagem).
- Blender: usar **Eevee/Workbench** com planos 2.5D. Cycles na CPU é lento demais; evitar. *(Versões não verificadas nesta sessão.)*
- Audacity: adequado.
- Evitar: geração local de vídeo ou imagem por IA (exige GPU dedicada).

## 5. Estrutura de pastas

```
00_docs/            auditoria, guias, registro de testes
01_referencias/     pranchas de estilo (somente referência; NÃO versionadas)
02_roteiros/        roteiros por história
03_storyboards/     storyboards por história
04_personagens/<nome>/01_arte_krita 02_psd 03_rig 04_exports 05_revisao
05_cenarios/        cenários 2.5D (Blender / camadas com profundidade)
06_audio/           narracao, dialogos, sfx, trilhas
07_cenas/           cenas montadas (.rigby com atores e clipes)
08_render/          vídeos finais e testes
tools/              automação (cliente MCP, pipeline, compensações, montagem)
```

## 6. Plano em etapas

| Etapa | Status |
| --- | --- |
| E1. Auditoria + MCP oficial conectado e testado | ✅ concluída (nesta sessão) |
| E2. Pipeline PSD → rig → animações → poses → lip-sync → vídeo, reprodutível | ✅ `tools/montar_personagem.sh` |
| E3. **No seu PC**: instalar o Rigby2D + Rigby2D-AI.mcpb no Claude Desktop (passos na seção 7) | ⏳ depende de você |
| E4. **Arte final do pastor jovem no Krita**, no estilo das pranchas, com as camadas de `GUIA_DE_ESTILO.md` | ⏳ precisa de um ilustrador (a IA não pinta nesse nível) |
| E5. Rodar o pipeline na arte final; revisar no editor (pesos de malha, physics no cabelo e na estola) | próxima |
| E6. Vista 3/4 ou perfil para a caminhada lateral (de frente, a caminhada é limitada) | próxima |
| E7. Cenário 2.5D com parallax: teste com `add_actor` + `set_layer_depth` e com o Blender | próxima |
| E8. Personagem-piloto aprovado → biblioteca de personagens → primeira história | depois da aprovação |

## 7. Instalação no seu Windows (você executa)

1. Crie a pasta do estúdio, por exemplo `C:\EstudioBiblico` (sem acentos, fora de pastas ocultas).
2. Baixe da [release mais recente](https://github.com/jaisurya-dev-art/rigby2d/releases/latest): `Rigby2D_x64_portable.exe`, `Rigby2D-AI.mcpb` e `SHA256SUMS.txt`.
3. Confira os checksums no PowerShell: `Get-FileHash .\Rigby2D-AI.mcpb -Algorithm SHA256` (os arquivos não são assinados; o SmartScreen pode avisar).
4. Arraste o `Rigby2D-AI.mcpb` para a janela do Claude Desktop (ou *Settings ▸ Extensions ▸ Advanced settings ▸ Install Extension…*). Em "Project folders", escolha **somente** `C:\EstudioBiblico`.
5. Teste no Claude Desktop: "use inspect_project em 04_personagens\pastor_jovem\03_rig\pastor_jovem_rig_v003.rigby".
