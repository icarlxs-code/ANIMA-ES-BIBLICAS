"""Gera o personagem PROVISÓRIO (placeholder técnico) do pastor jovem em camadas SVG.

Não é a arte final: serve para validar o pipeline Krita -> PSD -> Rigby2D (AutoRig, animação,
lip-sync). A arte final deve ser pintada no Krita com OS MESMOS nomes e a mesma ordem de camadas.

Saída: <pasta>/svg/NN_nome.svg (uma camada por arquivo, tela inteira 1000x1700) e camadas.json.
Convenção de lados: _l/_r = lado DO PERSONAGEM (o esquerdo dele fica à direita da imagem).
"""
import json
import sys
from pathlib import Path

W, H = 1000, 1700
INK = "#4a2e1e"  # tinta de detalhe (olhos, boca); sem contorno preto no estilo de referência
C = {
    "skin": ("#c98a5a", "#9c623c"),
    "tunic": ("#ece2cc", "#c7b796"),
    "scarf": ("#9a6a3c", "#6b4424"),
    "belt": ("#4a3a30", "#2f241d"),
    "hair": ("#3b2a1e", "#22170f"),
    "sandal": ("#6b4a2e", "#47301c"),
    "wood": ("#7a5234", "#4f331f"),
    "eye": ("#fbf6ee", "#d9cfc2"),
}


def mirror(d):
    """Espelha um path simples (só comandos absolutos M L C Z com pares x,y) em torno de x=500."""
    out, toks, i = [], d.replace(",", " ").split(), 0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            out.append(t)
            i += 1
        else:
            out.append(f"{W - float(t):g} {toks[i + 1]}")
            i += 2
    return " ".join(out)


GRAD = {"tunic", "scarf", "belt", "wood"}  # tecidos escurecem em degradê até a barra


def part(base, mat, shadow=None, lines=(), extra="", sw=1.4):
    """Estilo das referências: base chapada + sombra de borda dura (luz da esquerda) +
    degradê vertical nos tecidos + borda fina no tom da sombra (sem contorno preto)."""
    fill, shade = C[mat]
    cid = f"c{abs(hash(base)) % 10**8}"
    s = f'<clipPath id="{cid}"><path d="{base}"/></clipPath>'
    s += f'<path d="{base}" fill="{fill}"/>'
    if shadow:
        s += f'<path d="{shadow}" fill="{shade}" clip-path="url(#{cid})"/>'
    if mat in GRAD:
        s += (f'<linearGradient id="g{cid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2414" stop-opacity="0"/>'
              f'<stop offset="1" stop-color="#3a2414" stop-opacity=".38"/></linearGradient>'
              f'<path d="{base}" fill="url(#g{cid})"/>')
    for ln in lines:
        s += f'<path d="{ln}" fill="none" stroke="{shade}" stroke-width="3" stroke-linecap="round" opacity=".9" clip-path="url(#{cid})"/>'
    s += extra
    s += f'<path d="{base}" fill="none" stroke="{shade}" stroke-width="{sw}" stroke-linejoin="round" opacity=".8"/>'
    return s


L = []  # (nome, svg_interno, visível)


def add(name, body, visible=True):
    L.append((name, body, visible))


# ---------- cabelo de trás ----------
add("hair_back", part("M 428 230 C 420 300 425 330 445 345 L 555 345 C 575 330 580 300 572 230 Z", "hair",
                      "M 520 230 L 572 230 C 580 300 575 330 555 345 L 530 345 Z"))

# ---------- pernas (lado direito do personagem = esquerda da imagem) ----------
thigh = "M 440 755 L 497 755 L 494 1085 L 446 1085 Z"
shin = "M 446 1045 L 493 1045 C 492 1180 488 1320 484 1418 L 455 1418 C 452 1320 448 1180 446 1045 Z"
shin_sh = "M 478 1045 L 500 1045 L 490 1418 L 474 1418 C 478 1300 480 1170 478 1045 Z"
foot = "M 452 1400 L 488 1400 C 496 1428 500 1450 494 1466 L 426 1470 C 418 1460 426 1440 452 1400 Z"
foot_sh = "M 420 1456 L 500 1452 L 500 1480 L 420 1480 Z"
straps = ("M 448 1425 L 491 1425", "M 440 1445 L 496 1442", "M 470 1400 L 470 1425")
sole = '<path d="M 424 1466 L 496 1462 L 497 1476 L 422 1480 Z" fill="#3a2718" stroke="#2e1d14" stroke-width="1"/>'
for side, f in (("r", lambda d: d), ("l", mirror)):
    add(f"thigh_{side}", part(f(thigh), "skin"))
for side, f in (("r", lambda d: d), ("l", mirror)):
    add(f"shin_{side}", part(f(shin), "skin", f(shin_sh)))
for side, f in (("r", lambda d: d), ("l", mirror)):
    strap_svg = "".join(f'<path d="{f(s)}" stroke="{C["sandal"][0]}" stroke-width="7" stroke-linecap="round" fill="none"/>' for s in straps)
    sole_svg = sole if side == "r" else sole.replace(
        'M 424 1466 L 496 1462 L 497 1476 L 422 1480 Z', mirror('M 424 1466 L 496 1462 L 497 1476 L 422 1480 Z'))
    add(f"foot_{side}", part(f(foot), "skin", f(foot_sh), extra=strap_svg + sole_svg))

# ---------- túnica: saia (pelve), tronco, faixa ----------
add("skirt", part("M 410 735 L 590 735 C 606 950 612 1150 614 1372 C 560 1380 440 1380 386 1372 C 388 1150 394 950 410 735 Z",
                  "tunic",
                  "M 545 735 L 600 735 L 620 1380 L 555 1380 C 560 1150 556 950 545 735 Z",
                  ("M 455 800 C 450 1000 440 1200 432 1365", "M 500 820 C 502 1000 505 1200 505 1370",
                   "M 470 1180 C 468 1260 466 1320 462 1370")))
add("neck", part("M 478 325 L 522 325 L 527 445 L 473 445 Z", "skin", "M 470 325 L 530 325 L 530 372 C 510 380 490 380 470 360 Z"))
add("torso", part("M 445 418 L 482 418 L 500 478 L 518 418 L 555 418 C 585 425 602 445 606 475 L 596 765 L 404 765 L 394 475 C 398 445 415 425 445 418 Z",
                  "tunic",
                  "M 548 418 C 590 425 606 450 606 475 L 596 765 L 552 765 C 560 640 560 520 548 418 Z",
                  ("M 430 520 C 445 600 448 680 444 760", "M 560 520 C 556 600 555 690 560 760")))
add("belt", part("M 403 732 C 470 742 530 742 597 732 L 599 786 C 530 796 470 796 401 786 Z", "belt",
                 "M 403 770 L 600 770 L 600 800 L 400 800 Z",
                 extra=('<path d="M 452 760 C 440 800 438 860 442 905 L 466 902 C 466 860 468 810 470 765 Z" '
                        f'fill="{C["belt"][0]}" stroke="{INK}" stroke-width="1.4" stroke-opacity=".5"/>'
                        '<path d="M 470 762 C 476 800 480 850 488 880 L 506 872 C 498 840 492 800 486 760 Z" '
                        f'fill="{C["belt"][1]}" stroke="{INK}" stroke-width="1.4" stroke-opacity=".5"/>'
                        f'<ellipse cx="468" cy="760" rx="20" ry="16" fill="{C["belt"][0]}" stroke="{INK}" stroke-width="1.4" stroke-opacity=".5"/>')))

# ---------- estola / echarpe ----------
add("scarf", part("M 446 408 C 466 448 534 448 554 408 L 572 428 L 582 600 C 586 760 588 880 586 1010 L 540 1016 "
                  "C 544 880 544 740 540 470 C 520 478 482 478 470 470 C 466 560 462 640 468 705 L 438 696 "
                  "C 434 600 436 500 428 428 Z",
                  "scarf",
                  "M 556 440 L 586 440 L 590 1016 L 560 1016 C 565 880 566 700 556 440 Z",
                  ("M 480 452 C 495 462 515 462 532 452", "M 556 520 C 560 700 562 850 560 1000", "M 450 470 C 448 560 447 630 452 690")))

# ---------- cabeça (com orelhas) ----------
head = "M 432 248 C 432 176 568 176 568 248 C 568 300 552 346 500 372 C 448 346 432 300 432 248 Z"
ears = (f'<ellipse cx="432" cy="285" rx="13" ry="23" fill="{C["skin"][0]}" stroke="{INK}" stroke-width="1.4" stroke-opacity=".5"/>'
        f'<ellipse cx="568" cy="285" rx="13" ry="23" fill="{C["skin"][1]}" stroke="{INK}" stroke-width="1.4" stroke-opacity=".5"/>')
add("head", ears + part(head, "skin",
                        "M 525 180 C 570 200 575 270 560 312 C 548 345 522 364 500 372 C 532 330 545 268 525 180 Z "
                        "M 420 170 L 580 170 L 580 232 C 540 220 470 222 420 236 Z"))

# ---------- olhos (abertos e fechados = imagens alternativas do mesmo slot) ----------
eye = "M 451 274 C 460 262 482 260 492 272 C 484 282 462 284 451 274 Z"
for side, f in (("r", lambda d: d), ("l", mirror)):
    lid = f("M 449 274 C 460 258 484 257 494 271")
    add(f"eye_{side}", part(f(eye), "eye", f("M 440 255 L 500 255 L 500 268 L 440 268 Z"), sw=2,
                            extra=f'<path d="{lid}" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>'))
for side, f in (("r", lambda d: d), ("l", mirror)):
    add(f"eye_{side}_closed", f'<path d="{f("M 450 274 C 462 281 482 281 493 272")}" fill="none" stroke="{INK}" '
                              'stroke-width="4.5" stroke-linecap="round"/>', visible=False)
for side, cx in (("r", 472), ("l", 528)):
    add(f"pupil_{side}", f'<circle cx="{cx}" cy="272" r="8" fill="#3a2414"/><circle cx="{cx}" cy="272" r="4" fill="#120a05"/>'
                         f'<circle cx="{cx - 3}" cy="269" r="2.3" fill="#fff"/>')
for side, f in (("r", lambda d: d), ("l", mirror)):
    add(f"brow_{side}", f'<path d="{f("M 448 250 C 460 240 478 238 492 243 L 490 249 C 478 246 462 248 450 256 Z")}" '
                        f'fill="{C["hair"][0]}" stroke="{INK}" stroke-width="2"/>')

# ---------- nariz ----------
add("nose", f'<path d="M 498 250 C 494 280 486 304 486 316 C 488 330 512 332 520 320 C 518 300 510 276 504 250 Z" fill="#d89a6a"/>'
            f'<path d="M 503 250 C 510 276 518 300 520 320 C 514 330 502 331 496 327 C 506 318 508 290 503 250 Z" fill="{C["skin"][1]}"/>'
            f'<path d="M 487 318 C 491 327 500 329 506 326" fill="none" stroke="#6e3f24" stroke-width="2.2" stroke-linecap="round"/>')

# ---------- bocas (visemas). rest visível; as demais ocultas ----------
lip = C["skin"][1]
dark = "#5a2418"
M = {
    "mouth_rest": f'<path d="M 484 342 C 494 346 508 346 518 341" fill="none" stroke="{INK}" stroke-width="1.4" stroke-opacity=".5" stroke-linecap="round"/>',
    "mouth_MBP": f'<path d="M 483 342 C 494 344 508 344 519 341" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
                 f'<path d="M 489 348 C 497 351 506 351 513 348" fill="none" stroke="{lip}" stroke-width="3" stroke-linecap="round"/>',
    "mouth_A": f'<path d="M 482 338 C 492 334 510 334 520 338 C 516 360 486 360 482 338 Z" fill="{dark}" stroke="{INK}" stroke-width="2.5"/>'
               '<path d="M 486 340 C 495 337 507 337 516 340 L 514 344 C 505 342 496 342 488 344 Z" fill="#f4efe6"/>',
    "mouth_E": f'<path d="M 480 339 C 492 336 510 336 522 339 C 516 351 486 351 480 339 Z" fill="{dark}" stroke="{INK}" stroke-width="2.5"/>'
               '<path d="M 484 340 C 495 338 507 338 518 340 L 516 343 C 505 341 496 341 486 343 Z" fill="#f4efe6"/>',
    "mouth_I": f'<path d="M 480 340 C 492 338 510 338 522 340 C 516 348 486 348 480 340 Z" fill="#f4efe6" stroke="{INK}" stroke-width="2.5"/>',
    "mouth_O": f'<ellipse cx="501" cy="344" rx="11" ry="13" fill="{dark}" stroke="{INK}" stroke-width="2.5"/>',
    "mouth_U": f'<ellipse cx="501" cy="343" rx="7" ry="8" fill="{dark}" stroke="{INK}" stroke-width="2.5"/>',
    "mouth_FV": f'<path d="M 484 341 C 494 338 508 338 518 341 L 516 345 C 506 343 496 343 486 345 Z" fill="#f4efe6" stroke="{INK}" stroke-width="2"/>'
                f'<path d="M 485 346 C 495 350 507 350 517 346" fill="none" stroke="{INK}" stroke-width="1.4" stroke-opacity=".5" stroke-linecap="round"/>',
    "mouth_L": f'<path d="M 483 338 C 493 335 509 335 519 338 C 515 355 487 355 483 338 Z" fill="{dark}" stroke="{INK}" stroke-width="2.5"/>'
               '<path d="M 491 349 C 495 342 507 342 511 349 Z" fill="#c45a4a"/>',
}
for n, svg in M.items():
    add(n, svg, visible=(n == "mouth_rest"))

# ---------- cabelo da frente ----------
add("hair", part("M 424 250 C 412 190 440 140 500 138 C 560 136 592 185 578 252 C 570 236 566 226 560 214 "
                 "C 548 232 530 236 520 222 C 512 240 490 242 482 226 C 470 242 452 240 446 226 C 440 236 432 244 424 250 Z",
                 "hair",
                 "M 520 140 C 570 150 592 190 578 252 C 570 236 566 226 560 214 C 556 190 545 160 520 140 Z",
                 ("M 470 160 C 480 180 485 200 482 222", "M 520 160 C 528 180 526 205 520 220", "M 450 180 C 448 200 446 215 446 226")))

# ---------- braços ----------
upper = "M 408 424 C 382 430 364 456 364 492 L 362 702 C 378 722 412 722 426 702 L 440 482 C 440 450 430 428 408 424 Z"
upper_sh = "M 400 424 L 445 424 L 445 720 L 410 720 C 418 640 420 520 400 424 Z"
fore = "M 360 676 L 427 676 C 432 760 434 830 432 902 C 410 916 368 916 348 902 C 350 830 354 760 360 676 Z"
fore_sh = "M 405 676 L 440 676 L 440 916 L 400 916 C 410 830 410 760 405 676 Z"
hand = "M 372 892 C 362 925 362 962 380 984 C 393 996 412 992 416 970 C 419 945 418 918 412 892 Z"
hand_sh = "M 400 892 L 425 892 L 425 1000 L 398 1000 C 406 960 406 920 400 892 Z"
fist = "M 586 902 C 584 930 586 962 596 978 C 608 990 634 988 644 974 C 650 950 648 924 640 902 Z"
fist_sh = "M 622 902 L 652 902 L 652 992 L 618 992 C 628 960 628 930 622 902 Z"
fingers = ("M 590 930 C 610 926 630 926 646 930", "M 590 948 C 610 944 630 944 646 948", "M 594 964 C 612 960 630 960 644 964")
add("upperarm_r", part(upper, "tunic", upper_sh, ("M 390 560 C 395 600 398 650 395 700",)))
add("hand_r", part(hand, "skin", hand_sh, ("M 384 960 C 388 972 395 980 402 984",)))
add("forearm_r", part(fore, "tunic", fore_sh, ("M 372 760 C 372 820 370 870 366 900",)))
add("upperarm_l", part(mirror(upper), "tunic", mirror("M 445 424 L 470 424 L 470 720 L 445 720 Z"), (mirror("M 390 560 C 395 600 398 650 395 700"),)))
add("forearm_l", part(mirror(fore), "tunic", mirror("M 340 676 L 380 676 C 375 760 372 830 370 916 L 340 916 Z"), (mirror("M 372 760 C 372 820 370 870 366 900"),)))
add("staff", part("M 611 380 C 607 600 616 900 612 1474 L 628 1474 C 632 900 623 600 627 380 C 622 372 616 372 611 380 Z",
                  "wood", "M 620 376 L 632 376 L 632 1474 L 621 1474 C 626 900 618 600 620 376 Z",
                  ("M 615 520 L 622 526", "M 614 760 L 622 766", "M 616 1180 L 623 1186")))
add("hand_l", part(fist, "skin", fist_sh, fingers))


def main(out):
    out = Path(out)
    (out / "svg").mkdir(parents=True, exist_ok=True)
    meta = []
    for i, (name, body, vis) in enumerate(L):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
               f"<defs></defs>{body}</svg>")
        fn = f"{i:02d}_{name}.svg"
        (out / "svg" / fn).write_text(svg)
        meta.append({"name": name, "svg": fn, "visible": vis})
    (out / "camadas.json").write_text(json.dumps({"width": W, "height": H, "layers": meta}, indent=1))
    print(len(meta), "camadas")


if __name__ == "__main__":
    main(sys.argv[1])
