"""PASTOR JOVEM (personagem original), folha de modelo v1: vista frontal + 5 expressões.

Desenhado em SVG, na linguagem da bíblia visual (00_docs/BIBLIA_VISUAL.md): contorno fino no tom
da sombra, luz da esquerda com sombra de borda dura, nariz longo, textura de pincel procedural.
Cada parte é um <g id="..."> com o nome de camada em português (base para o PSD do Moho).

Uso: python3 tools/desenho_pastor_jovem.py <saida.svg>
"""
import math
import sys

INK = "#2b1a10"
SKIN, SKIN_S, SKIN_L = "#c68a5c", "#8e5532", "#dba06f"
TUN, TUN_S = "#d8c6a0", "#a08a63"
VEST, VEST_S = "#efe5cf", "#b8a582"
LEA, LEA_S = "#6e4527", "#45291a"
HAIR, HAIR_S, HAIR_L = "#2a1b12", "#160d07", "#4a3122"
ROPE, ROPE_S = "#a98a5c", "#6d5634"

_n = [0]


def uid(p="c"):
    _n[0] += 1
    return f"{p}{_n[0]}"


DEFS = f"""
<filter id="grao" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3"/>
  <feColorMatrix values="0 0 0 0 0.15  0 0 0 0 0.09  0 0 0 0 0.04  0 0 0 -1.4 1.05"/>
</filter>
<filter id="pincel" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.012 0.11" numOctaves="3" seed="8"/>
  <feColorMatrix values="0 0 0 0 0.2  0 0 0 0 0.12  0 0 0 0 0.05  0 0 0 -2.2 1.25"/>
</filter>
<filter id="desfoque"><feGaussianBlur stdDeviation="14"/></filter>
<linearGradient id="barra" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#2a170c" stop-opacity="0"/><stop offset="1" stop-color="#2a170c" stop-opacity=".42"/>
</linearGradient>
<linearGradient id="fundo" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#565656"/><stop offset="1" stop-color="#bdbdbd"/>
</linearGradient>
"""


def part(d, fill, shade=None, edge=None, folds=(), tex="grao", grad=False, lw=2.0, extra=""):
    """Forma com sombra dura recortada, textura, degradê até a barra, dobras e contorno fino."""
    c = uid()
    edge = edge or shade or INK
    s = f'<clipPath id="{c}"><path d="{d}"/></clipPath><path d="{d}" fill="{fill}"/>'
    g = f'clip-path="url(#{c})"'
    if shade:
        for sd in (shade if isinstance(shade, list) else [shade]):
            if sd.startswith("M"):
                s += f'<path d="{sd}" fill="{edge if False else SHADE_OF.get(fill, INK)}" {g}/>'
    if grad:
        s += f'<path d="{d}" fill="url(#barra)"/>'
    for f in folds:
        s += f'<path d="{f}" fill="none" stroke="{SHADE_OF.get(fill, INK)}" stroke-width="2.6" stroke-linecap="round" opacity=".85" {g}/>'
    if tex:
        s += f'<rect x="0" y="0" width="1000" height="1800" filter="url(#{tex})" opacity="{0.32 if tex == 'pincel' else 0.42}" {g}/>'
    s += extra
    s += f'<path d="{d}" fill="none" stroke="{DARK_OF.get(fill, INK)}" stroke-width="{lw}" stroke-linejoin="round"/>'
    return s


SHADE_OF = {SKIN: SKIN_S, TUN: TUN_S, VEST: VEST_S, LEA: LEA_S, HAIR: HAIR_S, ROPE: ROPE_S, "#7a5a3a": "#4c3420"}
DARK_OF = {SKIN: "#5e3219", TUN: "#6e5a3c", VEST: "#7d6c50", LEA: "#2a170c", HAIR: "#0e0804", ROPE: "#4a3a20"}


def mirror(d, cx=500):
    out, toks, i = [], d.replace(",", " ").split(), 0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            out.append(t)
            i += 1
        else:
            out.append(f"{2 * cx - float(t):g} {toks[i + 1]}")
            i += 2
    return " ".join(out)


def layer(name, body):
    return f'<g id="{name}">{body}</g>'


# =====================================================================================
# CABEÇA (rosto parametrizado por expressão)
# =====================================================================================
EXPR = {
    "neutro":    dict(brow=0, tilt=3, eye=1.0, low=1.0, ix=0, iy=0, isc=1.0, mouth="repouso"),
    "sorrindo":  dict(brow=-2, tilt=0, eye=0.78, low=0.45, ix=0, iy=0, isc=1.0, mouth="sorriso"),
    "triste":    dict(brow=1, tilt=12, eye=0.78, low=1.0, ix=0, iy=2.5, isc=1.0, mouth="triste"),
    "assustado": dict(brow=-9, tilt=5, eye=1.45, low=1.2, ix=0, iy=0, isc=0.82, mouth="susto"),
    "falando":   dict(brow=-3, tilt=2, eye=1.0, low=1.0, ix=-2.5, iy=0, isc=1.0, mouth="A"),
}


def hair_shapes():
    # massa de cachos: borda externa com ondulações
    pts = []
    var = [0, 5, -3, 7, 1, 9, -2, 6, 3, 10, 0, 8, -1, 7, 4, 9, -3, 6, 2, 5, 0]
    for k in range(0, 21):
        a = math.radians(163 + k * (214 / 20))
        r = 1.0 + var[k] / 100
        pts.append((500 + 90 * r * math.cos(a), 206 + 98 * r * math.sin(a)))
    outer = f"M 412 262 L {pts[0][0]:.1f} {pts[0][1]:.1f} "
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = mx - 500, my - 196
        ln = math.hypot(nx, ny)
        bump = 11 + (int(x0 * 7 + y0 * 3) % 7)
        outer += f"Q {mx + nx / ln * bump:.1f} {my + ny / ln * bump:.1f} {x1:.1f} {y1:.1f} "
    outer += ("L 590 262 Q 584 274 576 266 Q 576 248 568 236 Q 574 220 562 208 "
              "Q 552 222 544 206 Q 536 226 524 210 Q 516 230 502 212 Q 492 224 482 210 Q 470 228 460 208 "
              "Q 448 220 440 210 Q 428 222 432 238 Q 424 248 424 266 Q 414 274 412 262 Z")
    shade = "M 522 96 C 580 108 606 160 598 266 L 566 266 C 570 200 560 140 522 96 Z"
    curls = [f"M {x} {y} q 8 -10 16 0" for x, y in
             ((444, 160), (472, 136), (502, 128), (532, 138), (556, 160), (456, 192), (490, 176), (522, 178), (548, 198), (428, 222), (566, 226))]
    hl = [f"M {x} {y} q 7 -8 13 -1" for x, y in ((450, 150), (478, 126), (438, 186), (466, 166), (500, 150))]
    return outer, shade, curls, hl


def eye(cx, cy, o, low, ix, iy, isc, shaded, side):
    w = 17
    up = 10 * o
    lo = 6 * o * low
    d = (f"M {cx - w} {cy} C {cx - 9} {cy - up} {cx + 9} {cy - up} {cx + w} {cy} "
         f"C {cx + 9} {cy + lo} {cx - 9} {cy + lo} {cx - w} {cy} Z")
    c = uid()
    white = "#d9c9b3" if shaded else "#f4ecdc"
    s = f'<clipPath id="{c}"><path d="{d}"/></clipPath><path d="{d}" fill="{white}"/>'
    r = 7.6 * isc
    s += (f'<g clip-path="url(#{c})"><circle cx="{cx + ix}" cy="{cy + iy}" r="{r}" fill="#6b3c1c"/>'
          f'<circle cx="{cx + ix}" cy="{cy + iy}" r="{r * 0.5}" fill="#140a05"/>'
          f'<circle cx="{cx + ix - 2.5}" cy="{cy + iy - 2.5}" r="1.9" fill="#fff"/>'
          f'<path d="M {cx - w} {cy - up - 2} L {cx + w} {cy - up - 2} L {cx + w} {cy - up * 0.45} L {cx - w} {cy - up * 0.45} Z" fill="#000" opacity=".22"/></g>')
    flick = (cx + w + 4 if side == "esq" else cx - w - 4)
    oc = cx + w if side == "esq" else cx - w
    s += (f'<path d="M {cx - w - 1} {cy + 0.5} C {cx - 9} {cy - up - 1} {cx + 9} {cy - up - 1} {cx + w + 1} {cy + 0.5}" '
          f'fill="none" stroke="{INK}" stroke-width="3.6" stroke-linecap="round"/>'
          f'<path d="M {oc} {cy} L {flick} {cy - 2}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>'
          f'<path d="M {cx - 11} {cy + lo + 0.6} C {cx - 4} {cy + lo + 2} {cx + 4} {cy + lo + 2} {cx + 11} {cy + lo + 0.6}" '
          f'fill="none" stroke="#5e3219" stroke-width="1.3" opacity=".7"/>'
          f'<path d="M {cx - 13} {cy - up - 6} C {cx - 4} {cy - up - 10} {cx + 6} {cy - up - 10} {cx + 14} {cy - up - 5}" '
          f'fill="none" stroke="#5e3219" stroke-width="1.4" opacity=".55"/>'
          f'<path d="M {cx - 10} {cy + lo + 6} C {cx - 3} {cy + lo + 8} {cx + 4} {cy + lo + 8} {cx + 10} {cy + lo + 5}" '
          f'fill="none" stroke="#5e3219" stroke-width="1.1" opacity=".35"/>')
    return s


def brow(side, dy, tilt):
    if side == "dir":  # direita do personagem = esquerda da imagem
        ox, oy, ix, iy = 450, 230 + dy, 489, 225 + dy - tilt
    else:
        ox, oy, ix, iy = 550, 230 + dy, 511, 225 + dy - tilt
    mx, my = (ox + ix) / 2, (oy + iy) / 2 - 4
    return (f'<path d="M {ox} {oy - 1} Q {mx} {my - 5} {ix} {iy - 3} L {ix} {iy + 4} Q {mx} {my + 3} {ox} {oy + 3} Z" '
            f'fill="{HAIR}" stroke="{HAIR_S}" stroke-width="1.2"/>'
            f'<path d="M {ox + 6} {oy} Q {mx} {my - 2} {ix - 4} {iy}" stroke="{HAIR_L}" stroke-width="1.3" fill="none" opacity=".7"/>')


def mouth(kind):
    lip = "#7a3f26"
    M = {
        "repouso": f'<path d="M 486 328 C 494 330 506 330 514 327" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>'
                   f'<path d="M 490 335 C 497 339 505 339 511 335" fill="none" stroke="{lip}" stroke-width="3.2" stroke-linecap="round" opacity=".75"/>',
        "sorriso": '<path d="M 483 323 C 492 334 510 334 519 321 C 510 327 492 327 483 323 Z" fill="#f2ebe0" stroke="#2b1a10" stroke-width="2.2"/>'
                   f'<path d="M 474 312 C 476 320 480 326 484 327 M 528 310 C 526 318 522 324 518 325" fill="none" stroke="#5e3219" stroke-width="1.6" stroke-linecap="round"/>'
                   f'<path d="M 491 337 C 498 340 505 340 511 336" fill="none" stroke="{lip}" stroke-width="2.8" stroke-linecap="round" opacity=".7"/>',
        "triste": f'<path d="M 486 331 C 492 325 508 325 514 331" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>'
                  f'<path d="M 491 337 C 497 341 504 341 509 337" fill="none" stroke="{lip}" stroke-width="3.4" stroke-linecap="round" opacity=".8"/>',
        "susto": '<path d="M 489 322 C 489 313 511 313 511 322 L 510 338 C 509 347 491 347 490 338 Z" fill="#3e160d" stroke="#2b1a10" stroke-width="2.2"/>'
                 '<path d="M 491 321 C 495 317 505 317 509 321 L 509 324 L 491 324 Z" fill="#efe7da"/>',
        "A": '<path d="M 486 324 C 494 320 506 320 514 324 C 512 340 488 340 486 324 Z" fill="#3e160d" stroke="#2b1a10" stroke-width="2.2"/>'
             '<path d="M 489 325 C 496 322 504 322 511 325 L 510 328 L 490 328 Z" fill="#efe7da"/>'
             '<path d="M 493 336 C 496 331 504 331 507 336 Z" fill="#b8574a"/>',
    }
    return M[kind]


def head(expr="neutro"):
    e = EXPR[expr]
    outer, hshade, curls, hl = hair_shapes()
    face = ("M 500 124 C 550 124 578 158 580 208 C 582 252 574 290 560 314 C 546 338 524 356 500 358 "
            "C 476 356 454 338 440 314 C 426 290 418 252 420 208 C 422 158 450 124 500 124 Z")
    fshade = ("M 512 120 L 610 120 L 610 370 L 500 370 C 524 356 540 340 538 320 C 536 302 522 298 515 286 "
              "C 521 252 523 192 512 120 Z M 420 200 L 600 200 L 600 222 C 560 212 450 212 420 228 Z")
    s = layer("cabelo_tras", part("M 414 230 C 404 300 420 330 452 334 L 548 334 C 580 330 596 300 586 230 Z", HAIR,
                                  "M 520 230 L 600 230 L 600 340 L 530 340 Z"))
    s += layer("orelha_dir", part("M 424 234 C 404 228 398 262 410 282 C 416 292 426 290 428 282 Z", SKIN, None,
                                  extra='<path d="M 418 246 C 410 254 412 270 420 278" fill="none" stroke="#8e5532" stroke-width="2"/>'))
    s += layer("orelha_esq", part(mirror("M 424 234 C 404 228 398 262 410 282 C 416 292 426 290 428 282 Z"), SKIN,
                                  mirror("M 380 220 L 440 220 L 440 300 L 380 300 Z")))
    socket = ('<ellipse cx="470" cy="244" rx="21" ry="12" fill="#8e5532" opacity=".28"/>'
              '<ellipse cx="530" cy="244" rx="21" ry="12" fill="#6a3c22" opacity=".3"/>'
              '<path d="M 446 290 C 452 304 462 312 474 316" fill="none" stroke="#8e5532" stroke-width="1.5" opacity=".6"/>'
              + '<path d="M 486 346 C 494 352 506 352 514 346" fill="none" stroke="#8e5532" stroke-width="2" opacity=".5"/>')
    s += layer("cabeca_base", part(face, SKIN, fshade, extra=socket))
    s += layer("olho_dir", eye(470, 248, e["eye"], e["low"], e["ix"], e["iy"], e["isc"], False, "dir"))
    s += layer("olho_esq", eye(530, 248, e["eye"], e["low"], e["ix"], e["iy"], e["isc"], True, "esq"))
    s += layer("sobrancelha_dir", brow("dir", e["brow"], e["tilt"]))
    s += layer("sobrancelha_esq", brow("esq", e["brow"], e["tilt"]))
    s += layer("nariz",
               f'<path d="M 497 232 C 493 258 487 280 483 294 C 479 306 487 316 499 316 L 507 316 C 501 302 505 272 507 232 Z" fill="{SKIN_L}"/>'
               f'<path d="M 494 238 C 490 262 485 282 481 295" fill="none" stroke="#8e5532" stroke-width="1.8" stroke-linecap="round"/>'
               f'<path d="M 482 298 C 478 310 488 318 500 318 C 512 318 523 312 521 300" fill="none" stroke="#5e3219" stroke-width="2.2" stroke-linecap="round"/>'
               '<ellipse cx="491" cy="311" rx="3.4" ry="2" fill="#3a1d0e"/><ellipse cx="510" cy="311" rx="3.4" ry="2" fill="#3a1d0e"/>'
               f'<path d="M 494 319 C 503 323 514 322 522 316 L 523 321 C 512 326 501 326 494 319 Z" fill="{SKIN_S}" opacity=".6"/>')
    s += layer("boca", mouth(e["mouth"]))
    s += layer("cabelo_frente", part(outer, HAIR, hshade, tex="grao",
                                     extra="".join(f'<path d="{c}" fill="none" stroke="{HAIR_S}" stroke-width="2.2" stroke-linecap="round"/>' for c in curls)
                                     + "".join(f'<path d="{c}" fill="none" stroke="{HAIR_L}" stroke-width="2.4" stroke-linecap="round"/>' for c in hl)))
    s += layer("cordao", '<path d="M 432 214 C 470 203 530 203 568 214" fill="none" stroke="#7a4a2a" stroke-width="4.5" stroke-linecap="round"/>'
                         '<path d="M 520 205 C 540 206 556 209 568 214" fill="none" stroke="#45291a" stroke-width="4.5" stroke-linecap="round"/>')
    return s


# =====================================================================================
# CORPO
# =====================================================================================
def corpo():
    s = ""
    # sombra projetada longa (luz da esquerda)
    s += layer("sombra_chao", '<path d="M 400 1688 L 610 1680 L 990 1722 L 940 1752 L 420 1712 Z" fill="#1e1e1e" opacity=".38" filter="url(#desfoque)"/>')
    # cabelo de trás e pernas por baixo da túnica
    for side, f in (("dir", lambda d: d), ("esq", mirror)):
        s += layer(f"coxa_{side}", part(f("M 444 860 L 496 860 L 492 1262 L 448 1262 Z"), SKIN, f("M 476 860 L 500 860 L 500 1262 L 474 1262 Z"), tex=None))
    for side, f in (("dir", lambda d: d), ("esq", mirror)):
        shin = "M 444 1226 C 430 1300 434 1420 450 1594 L 480 1594 C 486 1470 492 1330 486 1226 Z"
        sh = "M 468 1226 L 490 1226 L 484 1594 L 470 1594 C 474 1470 476 1330 468 1226 Z"
        s += layer(f"canela_{side}", part(f(shin), SKIN, f(sh), folds=(f("M 452 1300 C 450 1360 452 1420 456 1470"),)))
    for side, f in (("dir", lambda d: d), ("esq", mirror)):
        foot = ("M 448 1584 C 440 1608 424 1638 418 1660 C 414 1676 428 1686 458 1686 C 486 1686 496 1678 494 1660 "
                "C 490 1636 484 1606 480 1584 Z")
        toes = "".join(f'<path d="{f(t)}" fill="none" stroke="#5e3219" stroke-width="1.6" stroke-linecap="round"/>'
                       for t in ("M 426 1672 L 428 1684", "M 438 1676 L 439 1686", "M 450 1678 L 450 1687", "M 462 1678 L 462 1687"))
        sole = f'<path d="{f("M 414 1680 C 430 1690 480 1692 498 1680 L 500 1694 C 480 1700 430 1700 412 1692 Z")}" fill="#3a2414" stroke="#1d1008" stroke-width="1.5"/>'
        straps = "".join(f'<path d="{f(t)}" fill="none" stroke="{LEA}" stroke-width="6" stroke-linecap="round"/>'
                         f'<path d="{f(t)}" fill="none" stroke="#2a170c" stroke-width="1.2" stroke-linecap="round" transform="translate(0,2.5)"/>'
                         for t in ("M 432 1640 L 490 1606", "M 444 1612 L 492 1640", "M 422 1660 L 494 1656", "M 450 1590 C 462 1600 474 1600 482 1590"))
        s += layer(f"pe_{side}", part(f(foot), SKIN, f("M 476 1584 L 500 1584 L 500 1690 L 470 1690 C 486 1660 482 1620 476 1584 Z"),
                                      extra=toes + straps) + sole)
    # túnica: saia
    skirt = ("M 404 736 L 598 736 C 606 900 616 1080 626 1252 C 606 1262 570 1268 534 1264 C 512 1270 488 1270 466 1264 "
             "C 430 1268 394 1262 374 1252 C 384 1080 394 900 404 736 Z")
    s += layer("tunica_saia", part(skirt, TUN, ["M 548 736 L 630 736 L 640 1280 L 560 1280 C 570 1100 562 900 548 736 Z",
                                                "M 470 900 C 466 1020 462 1140 458 1262 L 446 1262 C 452 1140 456 1020 462 900 Z"],
                                   folds=("M 428 800 C 422 960 414 1110 404 1250", "M 470 790 C 468 960 464 1120 462 1262",
                                          "M 588 800 C 594 960 600 1100 606 1250", "M 440 1120 C 436 1180 432 1220 428 1256"),
                                   tex="pincel", grad=True,
                                   extra='<path d="M 512 736 L 534 736 C 538 900 542 1080 546 1266 L 524 1268 C 520 1080 516 900 512 736 Z" fill="#7a5a3a" opacity=".85"/>'))
    # tronco da túnica
    torso = ("M 470 398 C 486 410 514 410 530 398 L 568 410 C 594 418 608 436 610 462 L 600 760 L 400 760 L 390 462 "
             "C 392 436 406 418 432 410 Z")
    s += layer("tunica_tronco", part(torso, TUN, "M 552 404 L 620 404 L 620 770 L 560 770 C 568 640 566 520 552 404 Z", tex="pincel",
                                     extra='<path d="M 512 404 L 532 404 L 534 760 L 512 760 Z" fill="#7a5a3a" opacity=".85"/>'
                                           '<path d="M 494 408 L 500 452 L 506 408 Z" fill="#6e5a3c"/>'))
    s += layer("pescoco", part("M 476 326 C 478 360 474 392 462 416 L 538 416 C 526 392 522 360 524 326 Z", SKIN,
                               ["M 502 326 L 530 326 L 530 420 L 506 420 C 512 380 506 350 502 326 Z", "M 470 326 L 532 326 L 532 352 C 512 362 490 362 470 350 Z"],
                               extra='<path d="M 496 378 C 499 384 503 384 506 378" fill="none" stroke="#5e3219" stroke-width="1.4"/>'))
    # colete de pele de carneiro
    vest_d = "M 434 408 C 410 416 394 436 392 462 L 400 742 L 466 746 C 470 640 476 520 486 412 Z"
    def fleece(x0, y0, x1, y1, n, lado):
        """Borda de lã: faixa com tufos irregulares ao longo da abertura do colete."""
        pts = [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n + 1)]
        w = 12 * lado
        d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f} "
        for k, ((ax, ay), (bx, by)) in enumerate(zip(pts, pts[1:])):
            amp = 7 + (k * 37 % 5)
            d += f"Q {(ax + bx) / 2 + amp * lado:.1f} {(ay + by) / 2:.1f} {bx:.1f} {by:.1f} "
        for (ax, ay) in reversed(pts):
            d += f"L {ax - w:.1f} {ay:.1f} "
        return d + "Z"
    ed = fleece(486, 412, 466, 746, 16, 1)
    s += layer("colete_dir", part(vest_d, VEST, "M 452 412 L 492 412 L 470 750 L 446 750 C 452 640 456 520 452 412 Z",
                                  folds=("M 420 500 C 424 580 426 660 424 730",))
               + part(ed, "#f6efde", None, tex="grao", lw=1.4))
    s += layer("colete_esq", part(mirror(vest_d), VEST, mirror("M 380 400 L 470 400 L 470 760 L 380 760 Z"),
                                  folds=(mirror("M 420 500 C 424 580 426 660 424 730"),))
               + part(mirror(ed), VEST_S, None, tex="grao", lw=1.4))
    # bolsa de couro (quadril direito do personagem)
    s += layer("bolsa", part("M 386 760 C 380 800 384 836 398 852 C 416 866 446 864 456 846 C 462 822 460 790 454 760 Z", LEA,
                             "M 432 760 L 470 760 L 470 870 L 436 870 C 446 830 444 790 432 760 Z",
                             extra='<path d="M 384 762 C 404 790 436 792 456 762 Z" fill="#5a3820" stroke="#2a170c" stroke-width="1.6"/>'
                                   '<circle cx="420" cy="784" r="4" fill="#c9a05a" stroke="#2a170c" stroke-width="1"/>'))
    # cinto de corda + pontas
    rope = "M 400 730 C 470 742 530 742 600 730 L 601 752 C 530 764 470 764 399 752 Z"
    twist = "".join(f'<path d="M {x} 734 l 8 20" stroke="{ROPE_S}" stroke-width="2"/>' for x in range(404, 598, 9))
    s += layer("cinto", part(rope, ROPE, "M 560 726 L 610 726 L 610 760 L 560 760 Z", tex=None, extra=twist))
    s += layer("pontas_cinto",
               f'<path d="M 478 752 C 472 790 468 830 470 866" fill="none" stroke="{ROPE}" stroke-width="7" stroke-linecap="round"/>'
               f'<path d="M 490 752 C 492 790 496 820 504 852" fill="none" stroke="{ROPE_S}" stroke-width="7" stroke-linecap="round"/>'
               f'<path d="M 466 862 l -3 16 M 470 866 l 0 16 M 474 862 l 3 16 M 500 850 l -2 15 M 504 852 l 2 15 M 508 848 l 4 14" stroke="{ROPE_S}" stroke-width="2"/>'
               f'<ellipse cx="484" cy="748" rx="13" ry="10" fill="{ROPE}" stroke="{ROPE_S}" stroke-width="2"/>')
    return s


def bracos():
    s = ""
    upper = "M 398 422 C 372 428 354 456 352 492 L 344 652 C 358 670 398 672 414 654 L 432 472 C 434 446 422 426 398 422 Z"
    fore = "M 346 630 L 416 632 C 426 720 438 800 446 870 C 420 892 352 896 318 874 C 322 800 332 712 346 630 Z"
    hand = ("M 362 852 L 412 852 C 418 874 420 898 416 916 C 414 938 408 958 398 968 C 390 976 380 974 376 964 "
            "C 368 970 358 964 358 952 C 350 950 346 940 350 928 C 344 914 348 890 352 870 Z")
    thumb = "M 410 880 C 426 896 428 920 418 932 C 412 936 406 930 408 920 Z"
    fingers = ("M 378 916 L 381 962", "M 366 912 L 362 950", "M 392 918 L 396 964")
    # braço direito do personagem (esquerda da imagem): relaxado
    s_dir = layer("braco_sup_dir", part(upper, TUN, "M 402 422 L 440 422 L 440 670 L 404 670 C 414 600 416 500 402 422 Z", tex="pincel",
                                        folds=("M 380 520 C 378 580 376 620 372 650",)))
    s_dir += layer("mao_dir", part(hand, SKIN, "M 398 852 L 424 852 L 424 980 L 396 980 C 406 940 408 890 398 852 Z",
                                   folds=fingers, extra=part(thumb, SKIN, "M 414 880 L 430 880 L 430 940 L 414 940 Z", tex=None)))
    s_dir += layer("antebraco_dir", part(fore, TUN, "M 398 630 L 440 630 L 440 884 L 404 884 C 414 800 410 700 398 630 Z", tex="pincel", grad=True,
                                         folds=("M 364 700 C 362 770 360 830 356 866", "M 390 760 C 392 800 394 840 394 872")))
    # braço esquerdo (direita da imagem): segura o cajado
    fist = "M 604 846 C 598 872 600 900 610 914 C 622 928 652 926 662 910 C 670 890 668 866 658 846 Z"
    s_esq = layer("braco_sup_esq", part(mirror(upper), TUN, mirror("M 300 400 L 420 400 L 420 680 L 300 680 Z"), tex="pincel",
                                        folds=(mirror("M 380 520 C 378 580 376 620 372 650"),)))
    s_esq += layer("antebraco_esq", part(mirror(fore), TUN, mirror("M 300 630 L 372 630 C 366 720 362 800 360 890 L 300 890 Z"), tex="pincel", grad=True,
                                         folds=(mirror("M 364 700 C 362 770 360 830 356 866"),)))
    staff = ("M 632 1694 C 628 1300 638 900 630 384 C 628 334 640 294 668 288 C 698 284 712 310 704 334 "
             "C 698 350 682 352 674 340")
    s_esq += layer("cajado",
                   f'<path d="{staff}" fill="none" stroke="#2a170c" stroke-width="17" stroke-linecap="round"/>'
                   f'<path d="{staff}" fill="none" stroke="#7a5234" stroke-width="13" stroke-linecap="round"/>'
                   '<path d="M 638 1690 C 634 1300 644 900 636 384 C 636 350 644 318 662 304" fill="none" stroke="#4a2f1c" stroke-width="5"/>'
                   '<path d="M 626 1200 C 624 900 632 700 625 420" fill="none" stroke="#a27a52" stroke-width="2.5" opacity=".7"/>'
                   + "".join(f'<path d="M 626 {y} q 6 4 12 0" fill="none" stroke="#2a170c" stroke-width="2"/>' for y in (560, 760, 1060, 1380)))
    s_esq += layer("mao_esq", part(fist, SKIN, "M 638 846 L 672 846 L 672 930 L 636 930 C 646 900 646 870 638 846 Z",
                                   folds=("M 606 872 C 624 868 646 868 664 872", "M 606 892 C 624 888 646 888 664 892", "M 610 908 C 626 904 646 904 660 908"),
                                   extra=part("M 606 850 C 618 838 642 838 650 852 C 638 858 620 860 606 850 Z", SKIN, None, tex=None)))
    return s_dir, s_esq


def figura(expr="neutro"):
    d, e = bracos()
    return corpo() + layer("cabeca", head(expr)) + d + e


def folha():
    W, H = 2500, 1800
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f"<defs>{DEFS}</defs>", f'<rect width="{W}" height="{H}" fill="url(#fundo)"/>']
    out.append(f'<g id="vista_frontal" transform="translate(40,20)">{figura("neutro")}</g>')
    lab = 'font-family="Trebuchet MS, Arial" font-weight="700" fill="#e9b649" letter-spacing="2"'
    out.append(f'<text x="540" y="1782" text-anchor="middle" font-size="40" {lab}>PASTOR JOVEM — FRONTAL</text>')
    slots = [(1080, 40), (1560, 40), (2040, 40), (1320, 900), (1800, 900)]
    for (x, y), ex in zip(slots, EXPR):
        sc = 1.95
        out.append(f'<g transform="translate({x},{y}) scale({sc}) translate(-390,-60)">'
                   f'<clipPath id="cl_{ex}"><rect x="380" y="60" width="240" height="370"/></clipPath>'
                   f'<g clip-path="url(#cl_{ex})">{corpo_minimo()}{head(ex)}</g></g>')
        out.append(f'<text x="{x + 210}" y="{y + 800}" text-anchor="middle" font-size="34" {lab}>{ex.upper()}</text>')
    out.append("</svg>")
    return "\n".join(out)


def corpo_minimo():
    """Ombros e gola para os retratos de expressão."""
    d = bracos()
    return (layer("tunica_tronco", part("M 470 398 C 486 410 514 410 530 398 L 568 410 C 594 418 608 436 610 462 L 600 760 L 400 760 L 390 462 C 392 436 406 418 432 410 Z",
                                        TUN, "M 552 404 L 620 404 L 620 770 L 560 770 C 568 640 566 520 552 404 Z", tex="pincel"))
            + part("M 476 326 C 478 360 474 392 462 416 L 538 416 C 526 392 522 360 524 326 Z", SKIN,
                   ["M 502 326 L 530 326 L 530 420 L 506 420 C 512 380 506 350 502 326 Z", "M 470 326 L 532 326 L 532 352 C 512 362 490 362 470 350 Z"]))


if __name__ == "__main__":
    open(sys.argv[1], "w").write(folha())
