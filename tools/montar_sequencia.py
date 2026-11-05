"""Monta uma sequência de vídeo a partir dos quadros exportados pelo MCP (export_sprite_sheet, format=frames).

Uso:
  python3 -I tools/montar_sequencia.py <pasta_quadros> <saida.mp4> --plano respirar:1 --plano fala_teste:1 ...
        [--audio arquivo.wav:inicio_s] [--fps 30] [--tam 1920x1080]
Cada --plano é animação:repetições, em ordem. Fundo cinza em degradê com sombra projetada,
no estilo das pranchas de referência. Requer ffmpeg.
"""
import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def fundo(w, h, chao_y):
    bg = Image.new("RGB", (w, h))
    px = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / (h - 1)
        v = int(86 + (178 - 86) * t)
        px.line([(0, y), (w, y)], fill=(v, v, v))
    sombra = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sombra).ellipse([w // 2 - 230, chao_y - 22, w // 2 + 330, chao_y + 18], fill=120)
    sombra = sombra.filter(ImageFilter.GaussianBlur(10))
    bg.paste((60, 60, 60), (0, 0), sombra)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("quadros")
    ap.add_argument("saida")
    ap.add_argument("--plano", action="append", required=True)
    ap.add_argument("--audio", action="append", default=[])
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--tam", default="1920x1080")
    a = ap.parse_args()
    W, H = map(int, a.tam.split("x"))
    q = Path(a.quadros)
    seq = []
    for pl in a.plano:
        nome, rep = pl.split(":")
        frames = sorted(q.glob(f"{nome}_[0-9][0-9][0-9].png"))
        if not frames:
            raise SystemExit(f"Sem quadros para {nome}")
        seq += frames * int(rep)
    fw, fh = Image.open(seq[0]).size
    x0, y0 = (W - fw) // 2, H - fh - 40
    bg = fundo(W, H, y0 + fh - 8)
    with tempfile.TemporaryDirectory() as tmp:
        for i, f in enumerate(seq):
            im = bg.copy()
            im.paste(Image.open(f).convert("RGBA"), (x0, y0), Image.open(f).convert("RGBA"))
            im.save(f"{tmp}/{i:05d}.png")
        cmd = ["ffmpeg", "-y", "-v", "error", "-framerate", str(a.fps), "-i", f"{tmp}/%05d.png"]
        filt, maps = [], []
        for k, au in enumerate(a.audio):
            arq, ini = au.rsplit(":", 1)
            cmd += ["-i", arq]
            ms = int(float(ini) * 1000)
            filt.append(f"[{k + 1}:a]adelay={ms}|{ms}[a{k}]")
            maps.append(f"[a{k}]")
        if a.audio:
            filt.append("".join(maps) + f"amix=inputs={len(maps)}:normalize=0[aout]")
            cmd += ["-filter_complex", ";".join(filt), "-map", "0:v", "-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart", a.saida]
        subprocess.run(cmd, check=True)
    print(f"{a.saida}: {len(seq)} quadros, {len(seq) / a.fps:.2f} s")


if __name__ == "__main__":
    main()
