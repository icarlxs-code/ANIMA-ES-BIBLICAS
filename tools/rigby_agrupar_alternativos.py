"""Ajustes de rig que o MCP 0.4.3 não expõe: junta imagens alternativas (bocas, olhos fechados)
num único slot e ajusta IK (direção da dobra, softness). Sempre gera uma CÓPIA.

Por quê: o importador de PSD do Rigby2D 0.4.3 (MCP e editor) cria um slot por camada; as
alternativas compartilham o osso, mas não o slot. O lip_sync precisa de UM slot de boca com todas as
formas como anexos. Esta etapa roda logo após o autorig, antes de qualquer animação, e escreve
uma CÓPIA (o arquivo de entrada não é alterado). Valide depois com validate_project.

Uso:
  python3 tools/rigby_agrupar_alternativos.py entrada.rigby saida.rigby \
      --grupo mouth=mouth_rest,mouth_MBP,mouth_A ... --grupo eye_l=eye_l,eye_l_closed
O primeiro slot da lista é o destino (mantém o anexo visível dele); o slot é renomeado para o nome do grupo.
"""
import argparse
import json
import sys
import zipfile
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("saida")
    ap.add_argument("--grupo", action="append", default=[], help="nome=slot1,slot2,...")
    ap.add_argument("--ik", action="append", default=[],
                    help="nome:bend=+|-:softness=N  (direção da dobra e suavidade perto da extensão total)")
    a = ap.parse_args()
    src, dst = Path(a.entrada), Path(a.saida)
    if dst.exists():
        sys.exit(f"{dst} já existe: escolha outro nome (não sobrescrevo).")
    with zipfile.ZipFile(src) as z:
        files = {n: z.read(n) for n in z.namelist()}
    doc = json.loads(files["project.json"])
    if doc.get("animations"):
        sys.exit("O projeto já tem animações: agrupe slots antes de animar (as chaves referenciam slots).")
    slots = doc["slots"]
    by_name = {s["name"]: s for s in slots}
    remove = set()
    for g in a.grupo:
        name, members = g.split("=", 1)
        members = members.split(",")
        missing = [m for m in members if m not in by_name]
        if missing:
            sys.exit(f"Slots inexistentes: {missing}")
        target = by_name[members[0]]
        for m in members[1:]:
            s = by_name[m]
            if s["bone"] != target["bone"]:
                sys.exit(f"{m} está em outro osso que {members[0]}: não agrupo.")
            target["attachments"].extend(s["attachments"])
            remove.add(id(s))
        if name != target["name"] and name in by_name and name not in members:
            sys.exit(f"Já existe um slot chamado {name}.")
        target["name"] = name
        print(f"{name}: {[at['name'] for at in target['attachments']]} (visível: {target['attachment']})")
    doc["slots"] = [s for s in slots if id(s) not in remove]
    for spec in a.ik:
        name, *props = spec.split(":")
        ik = next((c for c in doc.get("ik", []) if c["name"] == name), None)
        if ik is None:
            sys.exit(f"IK inexistente: {name}")
        for pr in props:
            k, v = pr.split("=")
            if k == "bend":
                ik["bendPositive"] = (v == "+")
            elif k == "softness":
                ik["softness"] = float(v)
            else:
                sys.exit(f"Propriedade desconhecida: {k}")
        print(f"IK {name}: bendPositive={ik['bendPositive']} softness={ik['softness']}")
    files["project.json"] = json.dumps(doc, separators=(",", ":")).encode()
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_STORED) as z:
        for n, b in files.items():
            z.writestr(n, b)
    print(f"{len(slots)} -> {len(doc['slots'])} slots: {dst}")


if __name__ == "__main__":
    main()
