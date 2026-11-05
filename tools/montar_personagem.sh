#!/usr/bin/env bash
# Pipeline reprodutível: PSD em camadas -> rig Rigby2D animado, só com o MCP oficial
# (mais a etapa de agrupamento de alternativos, que o importador ainda não faz).
#
# Uso: tools/montar_personagem.sh <psd> <saida.rigby> <pasta_animacoes_json> [<fala.wav> <texto> <offset>]
# Requer: RIGBY2D_MCP=<rigby2d>/src/mcp/server.js
set -euo pipefail
PSD="$1"; OUT="$2"; ANIMS="$3"; WAV="${4:-}"; TEXTO="${5:-}"; OFF="${6:-0.3}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MCP() { node "$ROOT/tools/rigby_mcp.mjs" --root "$ROOT" call "$1" "$2" 2>/dev/null; }
ok() { python3 -c "import json,sys;d=json.load(sys.stdin);print('  ', d['tool'], 'ERRO: '+str(d['result']) if d.get('isError') or d.get('rpcError') else 'ok');sys.exit(1 if d.get('isError') or d.get('rpcError') else 0)"; }
cd "$ROOT"
BASE="${OUT%.rigby}"
AUTO="${BASE}_autorig.rigby"

echo "1. detect_parts"; MCP detect_parts "{\"psd_file\":\"$PSD\",\"roles\":{\"staff\":\"extra\",\"scarf\":\"torso\",\"skirt\":\"tail\"}}" | ok
echo "2. autorig (cajado na mão, estola no tronco, túnica como cadeia de tecido)"
MCP autorig "{\"psd_file\":\"$PSD\",\"output\":\"$AUTO\",\"overwrite\":true,\"roles\":{\"staff\":\"extra\",\"scarf\":\"torso\",\"skirt\":\"tail\"}}" | ok
for i in 1 2 3; do MCP rename_bone "{\"path\":\"$AUTO\",\"bone\":\"tail$i\",\"name\":\"robe_$i\"}" | ok; done
echo "3. ajustes: alternativos num slot + IK (cotovelo junto ao corpo, softness) (boca com 9 visemas, olhos abertos/fechados)"
rm -f "$OUT"
python3 tools/rigby_agrupar_alternativos.py "$AUTO" "$OUT" \
  --grupo mouth=mouth_rest,mouth_MBP,mouth_A,mouth_E,mouth_I,mouth_O,mouth_U,mouth_FV,mouth_L \
  --grupo eye_l=eye_l,eye_l_closed --grupo eye_r=eye_r,eye_r_closed \
  --ik ik_hand_l:softness=12 --ik ik_hand_r:bend=-:softness=12 \
  --ik ik_foot_l:softness=10 --ik ik_foot_r:softness=10
echo "4. animações (batch_edit: carrega e salva uma vez, atômico)"
for f in respirar caminhada_frente conversa fala_teste _expressoes_temp; do
  MCP batch_edit "{\"path\":\"$OUT\",\"operations\":$(cat "$ANIMS/$f.json")}" | ok
done
echo "5. expressões -> biblioteca de poses + controles faciais"
for e in alegre triste preocupado surpreso; do
  MCP save_pose "{\"path\":\"$OUT\",\"name\":\"$e\",\"animation\":\"_pose_$e\",\"time\":0,\"bones\":[\"head\",\"brow_l\",\"brow_r\",\"eye_l\",\"eye_r\",\"pupil_l\",\"pupil_r\",\"mouth\"],\"replace\":true}" | ok
  MCP add_face_control "{\"path\":\"$OUT\",\"name\":\"$e\",\"to\":\"$e\"}" | ok
  MCP delete_animation "{\"path\":\"$OUT\",\"animation\":\"_pose_$e\"}" | ok
done
echo "5b. cajado estável: chaves de compensação medidas com sample_pose"
python3 tools/compensar_rotacao.py "$OUT" hand_l caminhada_frente conversa fala_teste respirar --ref "$AUTO"
if [ -n "$WAV" ]; then
  echo "5c. áudio + lip-sync na animação fala_teste"
  MCP add_audio_track "{\"path\":\"$OUT\",\"audio_file\":\"$WAV\",\"animation\":\"fala_teste\",\"offset\":$OFF}" | ok
  MCP lip_sync "{\"path\":\"$OUT\",\"animation\":\"fala_teste\",\"text\":\"$TEXTO\"}" | ok
fi
echo "6. validate_project"; MCP validate_project "{\"path\":\"$OUT\"}" | ok
