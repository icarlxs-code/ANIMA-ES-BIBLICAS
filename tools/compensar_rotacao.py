"""Mantém a rotação de MUNDO de um osso (ex.: hand_l com o cajado) igual à pose de setup.

Mede com sample_pose (MCP) quanto o osso girou no mundo a cada 2 quadros e grava chaves de rotate
que anulam esse desvio (o osso não pode já ter chaves de rotate na animação). Como o osso não faz
parte de nenhuma cadeia de IK, uma passada basta. Verifica o resultado ao final.

Uso: python3 tools/compensar_rotacao.py <projeto.rigby> <osso> <animação> [...] [--ref <rigby_referência>]
--ref: arquivo cuja pose de setup define o ângulo-alvo (ex.: o rig como saiu do AutoRig, igual ao desenho).
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FPS, STEP = 30, 2


def mcp_calls(calls):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(calls, f)
    try:
        out = subprocess.run(["node", str(ROOT / "tools/rigby_mcp.mjs"), "--root", str(ROOT), "calls", f.name],
                             capture_output=True, text=True, env=os.environ)
    finally:
        os.unlink(f.name)
    res = json.loads(out.stdout)
    bad = [r for r in res if r.get("isError") or r.get("rpcError")]
    if bad:
        sys.exit(f"Erro MCP: {bad[0]}")
    return [r["result"] for r in res]


def wrap(a):
    return (a + 180) % 360 - 180


def world_rot(pose, bone):
    return next(b["rotation"] for b in pose["bones"] if b["name"] == bone)


def main():
    args = sys.argv[1:]
    ref = None
    if "--ref" in args:
        i = args.index("--ref")
        ref = args[i + 1]
        del args[i:i + 2]
    path, bone, *anims = args
    info, setup = mcp_calls([{"tool": "inspect_project", "args": {"path": path}},
                             {"tool": "sample_pose", "args": {"path": ref or path}}])
    base = world_rot(setup, bone)
    dur = {a["name"]: a["duration"] for a in info["animations"]}
    for anim in anims:
        n = round(dur[anim] * FPS)
        times = [f / FPS for f in range(0, n + 1, STEP)]
        if times[-1] < dur[anim]:
            times.append(dur[anim])
        poses = mcp_calls([{"tool": "sample_pose", "args": {"path": path, "animation": anim, "time": t}} for t in times])
        dev = [wrap(world_rot(p, bone) - base) for p in poses]
        ops = [{"op": "set_bone_key", "animation": anim, "bone": bone, "channel": "rotate",
                "time": round(t, 4), "value": round(-d, 3), "curve": "linear"} for t, d in zip(times, dev)]
        mcp_calls([{"tool": "batch_edit", "args": {"path": path, "operations": ops}}])
        check = mcp_calls([{"tool": "sample_pose", "args": {"path": path, "animation": anim, "time": t + 1 / FPS}}
                           for t in times[:-1]])
        resid = max(abs(wrap(world_rot(p, bone) - base)) for p in check)
        print(f"   {anim}: desvio máx. {max(map(abs, dev)):.2f}° -> {resid:.2f}° (entre chaves)")


if __name__ == "__main__":
    main()
