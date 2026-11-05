# Estúdio de Animação Bíblica 2D + 2.5D

Pipeline de animação bíblica assistida por IA: **Krita** (arte em camadas) → **Rigby2D** via MCP
oficial (rig, animação, expressões, lip-sync) → **Blender** (cenários 2.5D) → **Audacity** (áudio).

- Auditoria, limitações e plano: [`00_docs/AUDITORIA_E_PLANO.md`](00_docs/AUDITORIA_E_PLANO.md)
- Estilo e convenção de camadas: [`00_docs/GUIA_DE_ESTILO.md`](00_docs/GUIA_DE_ESTILO.md)

## Personagem-piloto: pastor jovem (arte PROVISÓRIA)

```bash
export RIGBY2D_MCP=<rigby2d>/src/mcp/server.js
tools/montar_personagem.sh 04_personagens/pastor_jovem/02_psd/pastor_jovem_v003.psd \
  04_personagens/pastor_jovem/03_rig/pastor_jovem_rig_v003.rigby \
  04_personagens/pastor_jovem/03_rig/animacoes_json \
  06_audio/dialogos/teste_pastor_lc2-15_espeak.wav "Vamos, pois, até Belém, e vejamos isso que aconteceu." 0.3
```

Rig: 33 ossos, IK em braços e pernas (com softness), túnica como cadeia de tecido `robe_1..3`,
boca com 9 visemas. Animações: `respirar`, `caminhada_frente`, `conversa`, `fala_teste`.
Controles faciais: `alegre`, `triste`, `preocupado`, `surpreso`. Teste em vídeo:
`08_render/testes/pastor_jovem_piloto_v003.mp4`.

| Ferramenta | Função |
| --- | --- |
| `tools/rigby_mcp.mjs` | cliente MCP mínimo (o mesmo protocolo do Claude Desktop) |
| `tools/montar_personagem.sh` | PSD → rig animado, ponta a ponta |
| `tools/animacoes_pastor.py` | chaves das animações (para o `batch_edit`) |
| `tools/rigby_agrupar_alternativos.py` | ajustes que o MCP não expõe (slots alternativos, IK) |
| `tools/compensar_rotacao.py` | mantém o cajado estável (medido com `sample_pose`) |
| `tools/montar_sequencia.py` | quadros + áudio → MP4 de teste |
| `tools/gerar_pastor_placeholder.py`, `svg_camadas_para_psd.mjs` | arte provisória em camadas → PSD |
