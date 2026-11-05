"""Pintura raster procedural: cabeça frontal do pastor jovem (ficha da BIBLIA_VISUAL.md),
na técnica da folha de referência (sombra de borda dura com transições pintadas, luz da esquerda-alto,
luz de borda, contorno fino no tom do material, textura de pincel).

Uso:  python -I pintar_cabeca_frontal.py <saida.png>
"""
import math, sys
import numpy as np
import cv2
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

S = 1.6                       # px por unidade do desenho (desenho em 1000 x 1150)
W, H = int(1000 * S), int(1150 * S)
RNG = np.random.default_rng(7)
LUZ = np.array([-0.55, -0.70, 0.50]); LUZ = LUZ / np.linalg.norm(LUZ)


def cor(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


# ---------------- geometria (espaço do desenho) ----------------
def catmull(pts, fechado=True, n=14):
    out, P, m = [], list(pts), len(pts)
    for i in (range(m) if fechado else range(m - 1)):
        p0 = P[(i - 1) % m] if fechado else P[max(i - 1, 0)]
        p1, p2 = P[i], P[(i + 1) % m]
        p3 = P[(i + 2) % m] if fechado else P[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not fechado:
        out.append(P[-1])
    return out


def poli(pts, n=14):
    return Polygon(catmull(pts, n=n)).buffer(0)


def elip(cx, cy, rx, ry, rot=0.0, n=72):
    c, s = math.cos(rot), math.sin(rot)
    return Polygon([(cx + rx * math.cos(t) * c - ry * math.sin(t) * s, cy + rx * math.cos(t) * s + ry * math.sin(t) * c)
                    for t in (2 * math.pi * i / n for i in range(n))])


def traco(pts, w0, w1=None, wm=None, n=10):
    w1 = w0 if w1 is None else w1
    c = catmull(pts, fechado=False, n=n)
    e, d = [], []
    for i, p in enumerate(c):
        a, b = c[max(i - 1, 0)], c[min(i + 1, len(c) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        t = i / (len(c) - 1)
        w = (w0 + (w1 - w0) * t) if wm is None else (w0 * (1 - t) ** 2 + 2 * wm * t * (1 - t) + w1 * t * t)
        nx, ny = -dy / L * w / 2, dx / L * w / 2
        e.append((p[0] + nx, p[1] + ny)); d.append((p[0] - nx, p[1] - ny))
    return Polygon(e + d[::-1]).buffer(0)


# ---------------- raster ----------------
def mascara(g, suave=0.0):
    m = np.zeros((H, W), np.uint8)
    for p in (getattr(g, "geoms", None) or [g]):
        if p.is_empty or p.geom_type != "Polygon":
            continue
        ext = (np.array(p.exterior.coords) * S * 16).astype(np.int32)
        cv2.fillPoly(m, [ext], 255, cv2.LINE_AA, shift=4)
        for i in p.interiors:
            cv2.fillPoly(m, [(np.array(i.coords) * S * 16).astype(np.int32)], 0, cv2.LINE_AA, shift=4)
    m = m.astype(np.float32) / 255
    if suave > 0:
        m = cv2.GaussianBlur(m, (0, 0), suave * S)
    return m


def sombreamento(m, raio, achatar=1.0):
    """Luz difusa de uma forma 'inflada' a partir da máscara (0 = sombra, 1 = luz)."""
    d = cv2.distanceTransform((m > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    h = np.sqrt(np.clip(d / (raio * S), 0, 1)) * raio * S * achatar
    h = cv2.GaussianBlur(h, (0, 0), max(raio * S * 0.12, 1))
    gy, gx = np.gradient(h)
    n = np.dstack([-gx, -gy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return np.clip(n @ LUZ, 0, 1)


def degrau(x, t, w):
    """Terminador: borda firme com transição pintada de largura w."""
    return np.clip((x - (t - w)) / (2 * w), 0, 1) ** 1.0


def ruido(sx, sy, amp):
    """Textura de pincel (manchas alongadas)."""
    r = RNG.standard_normal((H, W)).astype(np.float32)
    r = cv2.GaussianBlur(r, (0, 0), sigmaX=sx * S, sigmaY=sy * S)
    r /= (r.std() + 1e-6)
    return r * amp


tela = np.zeros((H, W, 3), np.float32)


def pinta(m, rgb, alfa=1.0):
    """Aplica cor (cor única ou imagem) com a máscara m."""
    global tela
    a = (m * alfa)[..., None]
    tela = tela * (1 - a) + (rgb if np.ndim(rgb) == 3 else np.asarray(rgb, np.float32)) * a


def material(m, luz_c, sombra_c, raio, limiar=0.38, transicao=0.05, oclusao_c=None, brilho_c=None,
             textura=None, borda=True, borda_c=None, achatar=1.0):
    """Pinta um material com 2 a 3 tons e terminador firme."""
    sh = sombreamento(m, raio, achatar)
    k = degrau(sh, limiar, transicao)[..., None]
    rgb = sombra_c * (1 - k) + luz_c * k
    if oclusao_c is not None:
        ko = (1 - degrau(sh, limiar * 0.45, 0.06))[..., None]
        rgb = rgb * (1 - ko * 0.6) + oclusao_c * ko * 0.6
    if brilho_c is not None:
        kb = degrau(sh, 0.80, 0.05)[..., None]
        rgb = rgb * (1 - kb * 0.55) + brilho_c * kb * 0.55
    if textura is not None:
        rgb = rgb * (1 + textura[..., None])
    pinta(m, rgb)
    if borda:
        contorno(m, borda_c if borda_c is not None else sombra_c * 0.55)
    return sh


def contorno(m, c, esp=1.6, alfa=0.85):
    er = cv2.erode((m * 255).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=max(1, int(esp * S / 1.5)))
    e = np.clip(m - er.astype(np.float32) / 255, 0, 1)
    pinta(e, c, alfa)


def luz_borda(m, c, larg=5, alfa=0.9):
    """Luz de recorte no lado iluminado (esquerda)."""
    er = cv2.erode((m * 255).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=int(larg * S / 1.5))
    faixa = np.clip(m - er.astype(np.float32) / 255, 0, 1)
    gy, gx = np.gradient(cv2.GaussianBlur(m, (0, 0), 3 * S))
    lado = np.clip(gx * 40, 0, 1) * np.clip(1 - np.abs(gy) * 30, 0.3, 1)   # bordas voltadas para a esquerda
    pinta(cv2.GaussianBlur(faixa * lado, (0, 0), 0.8 * S), c, alfa)


def sombra_dura(g, c, alfa=1.0, suave=1.4, dentro=None):
    m = mascara(g, suave)
    if dentro is not None:
        m = m * dentro
    pinta(m, c, alfa)


# ---------------- paleta (BIBLIA_VISUAL.md + tons derivados) ----------------
PELE, PELE_S, PELE_O, PELE_L = cor("#c68a5c"), cor("#86492a"), cor("#5a2c1a"), cor("#e3ad7f")
PELE_RUBOR = cor("#c0704f")
CAB, CAB_L, CAB_S, CAB_B = cor("#2a1b12"), cor("#5b3d2a"), cor("#140b06"), cor("#7a5640")
COURO, COURO_S, COURO_L = cor("#6e4527"), cor("#45291a"), cor("#9a6a44")
TUN, TUN_S, TUN_O = cor("#d8c6a0"), cor("#a08a63"), cor("#7a6748")
COL, COL_S, COL_O = cor("#efe5cf"), cor("#b8a582"), cor("#8f7e60")
IRIS, IRIS_L, PUP = cor("#4e2a14"), cor("#8a5630"), cor("#140a05")
ESCLERA, ESCLERA_S = cor("#efe2cf"), cor("#b99a80")

# ---------------- fundo ----------------
yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :, None]
fundo = cor("#3f3b39") * (1 - yy) + cor("#8b8581") * yy
fundo = fundo * (1 - 0.10 * xx ** 2) + np.zeros((1, W, 3), np.float32)
tela[:] = fundo * (1 + ruido(6, 6, 0.025)[..., None]) * (1 + ruido(0.6, 0.6, 0.012)[..., None])

cx = 500
rosto = poli([(cx, 300), (606, 326), (652, 420), (652, 548), (632, 680), (600, 790), (556, 858),
              (cx, 880), (444, 858), (400, 790), (368, 680), (348, 548), (348, 420), (394, 326)], n=16)
pescoco = poli([(448, 800), (554, 800), (560, 940), (568, 1030), (432, 1030), (440, 940)], n=10)
cabelo_massa = unary_union([elip(cx, 330, 232, 190), elip(cx, 470, 220, 190), elip(cx, 600, 200, 150)])

# ---------------- cabelo de trás ----------------
m = mascara(cabelo_massa.difference(box(0, 640, W, 2000)).union(elip(cx, 610, 190, 120)))
material(m, CAB, CAB_S, 120, limiar=0.42, textura=ruido(1.2, 1.2, 0.05))

# ---------------- túnica, colete de pele ----------------
tun = Polygon(catmull([(420, 1000), (330, 1028), (240, 1075), (190, 1150)], fechado=False, n=8) + catmull([(810, 1150), (760, 1075), (670, 1028), (580, 1000)], fechado=False, n=8) + catmull([(578, 1000), (cx, 1040), (422, 1000)], fechado=False, n=8)).buffer(0)
streak = ruido(0.7, 14, 0.06)
mt = mascara(tun)
material(mt, TUN, TUN_S, 160, limiar=0.36, textura=streak)
sombra_dura(Polygon([(cx + 25, 960), (W, 960), (W, 1200), (cx + 80, 1200)]), TUN_S, 0.8, 3, dentro=mt)
sombra_dura(poli([(420, 990), (cx, 1050), (580, 990), (580, 1030), (cx, 1080), (420, 1030)], n=8), TUN_O, 0.55, 6, dentro=mt)
# decote com a faixa tecida marrom
dec = poli([(440, 1004), (cx, 1062), (560, 1004), (566, 1016), (cx, 1080), (434, 1016)], n=8)
sombra_dura(dec, TUN_O, 0.9, 1.2)
for lado in (-1, 1):
    col = Polygon([(cx + lado * 150, 1010), (cx + lado * 250, 1045), (cx + lado * 312, 1100), (cx + lado * 330, 1150), (cx + lado * 120, 1150)])
    mc = mascara(col)
    material(mc, COL if lado < 0 else COL_S, COL_S if lado < 0 else COL_O, 70, limiar=0.4, textura=ruido(2, 2, 0.06))
    # lã clara na borda: massa irregular com tufos
    tufos = [elip(cx + lado * (156 + 10.5 * k) + RNG.normal(0, 4), 1004 + 13.5 * k + RNG.normal(0, 4),
                  19 + RNG.normal(0, 3), 15 + RNG.normal(0, 3), RNG.uniform(0, 3)) for k in range(16)]
    ml = mascara(unary_union(tufos))
    material(ml, COL if lado < 0 else cor("#d8cbb0"), COL_S if lado < 0 else COL_O, 22, limiar=0.38,
             textura=ruido(0.8, 0.8, 0.08), borda_c=COL_O * 0.8)
    for t in tufos:
        c0 = t.centroid
        pinta(mascara(traco([(c0.x - 8, c0.y + 2), (c0.x - 2, c0.y - 6), (c0.x + 6, c0.y - 2)], 2, 1.5, wm=3), 0.6) * ml,
              COL_O if lado > 0 else COL_S, 0.6)

# ---------------- pescoço ----------------
mp = mascara(pescoco)
material(mp, PELE, PELE_S, 60, limiar=0.30, textura=ruido(1.5, 1.5, 0.012))
sombra_dura(Polygon([(cx + 8, 790), (W, 790), (W, 1100), (cx + 30, 1100)]), PELE_S, 0.95, 1.6, dentro=mp)
sombra_dura(poli([(430, 800), (cx, 880), (570, 800), (570, 770), (430, 770)], n=8), PELE_O, 0.85, 4, dentro=mp)
sombra_dura(traco([(470, 900), (474, 960), (468, 1010)], 4, 2, wm=6), PELE_S, 0.5, 3, dentro=mp)   # tendão
sombra_dura(poli([(400, 1035), (600, 1035), (600, 1010), (cx, 1020), (400, 1010)], n=6), PELE_O, 0.6, 5, dentro=mp)
luz_borda(mp, PELE_L, 4, 0.7)

# ---------------- orelhas (meio cobertas pelo cabelo) ----------------
for lado, x, rot in ((-1, 349, 0.12), (1, 651, -0.12)):
    mo = mascara(elip(x, 600, 32, 60, rot))
    material(mo, PELE if lado < 0 else PELE_S, PELE_S if lado < 0 else PELE_O, 22, limiar=0.36)
    sombra_dura(traco([(x - lado * 4, 572), (x + lado * 6, 600), (x - lado * 2, 632)], 9, 5, wm=12), PELE_O, 0.8, 2)

# ---------------- rosto ----------------
mr = mascara(rosto)
pele_tex = ruido(1.0, 1.0, 0.012) + ruido(6, 6, 0.012)
sh_r = material(mr, PELE, PELE_S, 150, limiar=0.30, transicao=0.06, textura=pele_tex, borda=False)
# rubor quente nas maçãs e no nariz (pintura)
pinta(mascara(elip(420, 655, 55, 40), 18) * mr, PELE_RUBOR, 0.30)
pinta(mascara(elip(592, 655, 50, 40), 18) * mr, PELE_RUBOR, 0.25)
# sombra própria em bloco: metade direita, terminador pela maçã do rosto
term = Polygon(catmull([(548, 296), (560, 410), (552, 468), (566, 560), (604, 640), (596, 716), (578, 790),
             (548, 858), (520, 900)], fechado=False, n=12) + [(1000, 900), (1000, 296)]).buffer(0)
sombra_dura(term, PELE_S, 1.0, 1.3, dentro=mr)
# reflexo quente dentro da sombra (luz rebatida), sutil
pinta(mascara(elip(615, 700, 22, 70, -0.25), 14) * mr, cor("#a0623c"), 0.45)
# planos: sob a sobrancelha, osso da face, têmpora
sombra_dura(poli([(360, 470), (420, 455), (470, 470), (470, 495), (420, 488), (365, 500)], n=8), PELE_S, 0.35, 6, dentro=mr)
sombra_dura(poli([(360, 610), (395, 590), (420, 640), (410, 720), (380, 700)], n=8), PELE_S, 0.25, 9, dentro=mr)
sombra_dura(poli([(342, 380), (cx, 400), (660, 380), (660, 280), (342, 280)], n=10), PELE_O, 0.75, 6, dentro=mr)
sombra_dura(poli([(372, 640), (405, 660), (440, 700), (455, 760), (430, 800), (400, 770), (378, 700)], n=8), PELE_S, 0.30, 10, dentro=mr)
sombra_dura(poli([(420, 830), (455, 852), (500, 864), (545, 852), (540, 880), (500, 890), (450, 878)], n=8), PELE_S, 0.45, 5, dentro=mr)
pinta(mascara(elip(408, 610, 26, 18, -0.3), 10) * mr, PELE_L, 0.35)
# olheiras
for ox, s in ((432, 1), (568, -1)):
    sombra_dura(traco([(ox - 34, 538), (ox, 552), (ox + 34, 540)], 3, 3, wm=12), PELE_S if s > 0 else PELE_O, 0.55, 3, dentro=mr)
luz_borda(mr, PELE_L, 6, 0.85)
contorno(mr, PELE_O * 0.8, 1.4, 0.75)

# ---------------- olhos ----------------
for lado, ox in ((-1, 432), (1, 568)):
    d = lado > 0
    olho = poli([(ox - 40, 512), (ox - 14, 493), (ox + 16, 494), (ox + 40, 509), (ox + 14, 527), (ox - 18, 526)], n=10)
    mo = mascara(olho)
    material(mo, ESCLERA * (0.86 if d else 1), ESCLERA_S, 26, limiar=0.30, borda=False)
    sombra_dura(Polygon([(ox - 50, 470), (ox + 50, 470), (ox + 50, 508), (ox - 50, 504)]), ESCLERA_S, 0.6, 3, dentro=mo)
    ix = ox - 3 + 3 * lado
    mi = mascara(elip(ix, 510, 17.5, 18.5)) * mo
    yy2, xx2 = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt((xx2 - ix * S) ** 2 + (yy2 - 514 * S) ** 2) / (18 * S)
    iris = IRIS_L * (1 - np.clip(rr, 0, 1)[..., None]) * 0.8 + IRIS * np.clip(rr * 1.1, 0.25, 1)[..., None]
    iris = np.where((yy2 < 508 * S)[..., None], iris * 0.62, iris)
    pinta(mi, iris)
    pinta(mascara(elip(ix, 511, 8, 9)) * mo, PUP)
    pinta(mascara(elip(ix - 7, 503, 4.5, 4.5), 0.4), cor("#fbf3e6"))
    pinta(mascara(elip(ix + 6, 518, 2, 2), 0.4), cor("#d9b48c"), 0.7)
    # pálpebra superior grossa e escura
    palp = traco([(ox - 45, 516), (ox - 24, 495), (ox + 6, 489), (ox + 36, 497), (ox + 47, 511)], 4, 3, wm=12)
    sombra_dura(palp, CAB, 1.0, 0.7)
    sombra_dura(traco([(ox - 38, 492), (ox, 477), (ox + 38, 486)], 2.4, 2, wm=6), PELE_O if d else PELE_S, 0.9, 1.0)
    sombra_dura(poli([(ox - 40, 492), (ox, 478), (ox + 40, 487), (ox + 40, 498), (ox, 490), (ox - 40, 503)], n=8),
                PELE_S if not d else PELE_O, 0.45, 2.5)
    sombra_dura(traco([(ox - 30, 527), (ox, 532), (ox + 34, 521)], 1.8, 1, wm=4), PELE_O, 0.75, 0.8)
    pinta(mascara(traco([(ox - 26, 533), (ox, 538), (ox + 26, 530)], 2, 2, wm=4), 1.2), PELE_L if not d else PELE, 0.5)
    # sobrancelhas grossas, parte interna levemente erguida, com fios
    if not d:
        sob = traco([(384, 471), (408, 457), (440, 452), (466, 446), (481, 434)], 9, 12, wm=21)
    else:
        sob = traco([(519, 434), (534, 446), (560, 452), (592, 457), (616, 471)], 12, 9, wm=21)
    ms = mascara(sob, 0.8)
    pinta(ms, CAB * (1 + ruido(0.4, 2.5, 0.25)[..., None]))
    pinta(ms * mascara(Polygon([(0, 0), (W, 0), (W, 449), (0, 449)]), 3), CAB_L, 0.35)

# ---------------- nariz: longo e pesado, ponta redonda ----------------
pinta(mascara(poli([(493, 455), (488, 540), (478, 640), (472, 690), (486, 712), (498, 690), (501, 600), (502, 500)], n=10), 3.5) * mr,
      cor("#d9a073"), 0.85)
ns = poli([(511, 458), (516, 560), (530, 650), (548, 700), (538, 730), (512, 736), (507, 690), (507, 560)], n=10)
sombra_dura(ns, PELE_O, 0.9, 1.8, dentro=mr)
sombra_dura(poli([(530, 520), (570, 560), (585, 650), (556, 700), (535, 640)], n=8), PELE_S, 0.6, 8, dentro=mr)
mpn = mascara(elip(503, 704, 31, 27))
material(mpn, PELE, PELE_S, 24, limiar=0.36, brilho_c=PELE_L, borda=False)
sombra_dura(elip(503, 704, 31, 27).intersection(box(507, 0, 1000, 2000)), PELE_S, 0.75, 1.6)
pinta(mascara(elip(491, 697, 8, 6), 1.5), cor("#f0c49a"), 0.85)
sombra_dura(traco([(472, 698), (467, 717), (480, 734)], 3.5, 2, wm=7), PELE_S, 0.85, 1.0)
sombra_dura(traco([(535, 698), (541, 717), (528, 734)], 3.5, 2, wm=7), PELE_O, 0.9, 1.0)
sombra_dura(unary_union([elip(489, 733, 7, 4, 0.3), elip(518, 733, 7, 4, -0.3)]), PELE_O * 0.8, 1, 0.8)
sombra_dura(poli([(480, 738), (530, 736), (566, 752), (520, 766), (486, 752)], n=8), PELE_O, 0.65, 3, dentro=mr)

# ---------------- boca pequena ----------------
sombra_dura(poli([(474, 789), (488, 778), (503, 782), (518, 778), (533, 789), (503, 790)], n=6), cor("#9a5a38"), 0.95, 1.0)
sombra_dura(traco([(470, 790), (488, 787), (503, 790), (518, 787), (536, 791)], 3, 3, wm=5), cor("#4f2716"), 1, 0.7)
pinta(mascara(poli([(480, 793), (503, 798), (528, 793), (522, 808), (503, 813), (486, 808)], n=6), 1.5), cor("#b87552"), 0.7)
sombra_dura(poli([(483, 810), (503, 815), (525, 810), (518, 822), (503, 826), (489, 822)], n=6), PELE_S, 0.75, 2.5)
pinta(mascara(elip(498, 800, 10, 3), 1.5), cor("#d99a78"), 0.45)
# buço e primeira penugem no queixo
pinta(mascara(poli([(468, 772), (503, 766), (540, 772), (532, 779), (503, 775), (474, 779)], n=6), 3)
      * (0.6 + 0.4 * (ruido(0.5, 0.5, 1) > 0)), cor("#4a2a18"), 0.30)
pinta(mascara(poli([(470, 846), (503, 860), (536, 846), (528, 874), (503, 884), (478, 874)], n=6), 4)
      * (0.6 + 0.4 * (ruido(0.5, 0.5, 1) > 0)), cor("#4a2a18"), 0.26)
pinta(mascara(elip(490, 842, 14, 8), 4), PELE_L, 0.45)

# ---------------- cabelo da frente: massa com cachos miúdos pintados ----------------
def cacho(x, y, r, ang, forca):
    sombra = elip(x + r * 0.30, y + r * 0.38, r * 0.95, r * 0.75, ang).difference(elip(x, y, r * 0.92, r * 0.8, ang))
    pinta(mascara(sombra, 1.4) * mh, CAB_S, 0.8)
    luz = elip(x - r * 0.05, y - r * 0.05, r * 0.78, r * 0.62, ang).difference(elip(x + r * 0.22, y + r * 0.24, r * 0.80, r * 0.66, ang))
    pinta(mascara(luz, 1.0) * mh, CAB_L, 0.7 * forca)
    a0 = ang + 3.6 + RNG.normal(0, 0.3)
    pts = [(x + r * 0.55 * math.cos(a0 + t * 1.3), y + r * 0.5 * math.sin(a0 + t * 1.3)) for t in (0, 0.5, 1)]
    pinta(mascara(traco(pts, 1.0, 1.0, wm=2.4, n=6), 0.5) * mh, CAB_B, 0.45 * forca)


cachos_pos = []
for fila, (y, rx, n, r) in enumerate([(205, 140, 7, 27), (236, 192, 9, 28), (270, 218, 10, 28), (306, 230, 11, 27),
                                      (342, 234, 11, 26), (374, 226, 11, 24)]):
    for k in range(n):
        t = (k + 0.5 * (fila % 2)) / max(n - 1, 1)
        x = cx - rx + 2 * rx * min(t, 1)
        cachos_pos.append((x + RNG.normal(0, 5), y + RNG.normal(0, 5), r * RNG.uniform(0.85, 1.12), RNG.uniform(0, 6.28)))
for lado in (-1, 1):
    for k, y in enumerate((410, 448, 486, 524, 560, 594)):
        x = cx + lado * (226 - 6 * k + (k % 2) * 8)
        cachos_pos.append((x + RNG.normal(0, 3), y, 24 - 1.3 * k, RNG.uniform(0, 6.28)))
massa_frente = unary_union([elip(x, y, r * 1.05, r * 0.95) for x, y, r, a in cachos_pos])
mh = mascara(massa_frente)
material(mh, CAB, CAB_S, 75, limiar=0.40, transicao=0.07, textura=ruido(0.6, 0.6, 0.06), borda_c=CAB_S * 0.8)
for (x, y, r, a) in sorted(cachos_pos, key=lambda c: c[1]):
    forca = float(np.clip(1.25 - (x - 270) / 420, 0.25, 1.0))
    cacho(x, y, r, a, forca)
luz_borda(mh, CAB_B, 4, 0.55)

# cordão de couro na testa, sobre o cabelo, com nó do lado direito do personagem
cord = traco([(326, 414), (420, 391), (cx, 385), (580, 391), (674, 414)], 12, 12, n=12)
mcd = mascara(cord)
material(mcd, COURO, COURO_S, 6, limiar=0.36, brilho_c=COURO_L, borda_c=COURO_S * 0.7)
sombra_dura(cord.intersection(box(556, 0, 1000, 2000)), COURO_S, 0.7, 1.2)
pinta(mascara(traco([(330, 410), (420, 389), (470, 384)], 2.5, 1), 0.6), COURO_L, 0.8)
mn = mascara(elip(342, 418, 13, 11))
material(mn, COURO, COURO_S, 8, limiar=0.38, brilho_c=COURO_L, borda_c=COURO_S * 0.7)
for pts in ([(338, 424), (326, 462), (332, 500)], [(346, 424), (346, 458), (340, 488)]):
    mpt = mascara(traco(pts, 6, 3.5))
    material(mpt, COURO, COURO_S, 3, limiar=0.4, borda_c=COURO_S * 0.7)
# alguns cachos da franja caem por cima do cordão
for pts in ([(470, 372), (462, 398), (472, 418)], [(522, 370), (530, 396), (520, 414)], [(430, 376), (424, 400), (434, 414)]):
    pinta(mascara(traco(pts, 7, 3, wm=9), 0.6), CAB)
    pinta(mascara(traco([(p[0] - 2, p[1]) for p in pts[:2]], 2, 1), 0.5), CAB_L, 0.6)
    sombra_dura(traco([(pts[2][0] + 4, pts[2][1] + 6), (pts[2][0] + 8, pts[2][1] + 14)], 5, 2), PELE_O, 0.35, 3, dentro=mr)

# ---------------- acabamento: grão de pintura geral ----------------
tela = tela * (1 + ruido(0.5, 0.5, 0.010)[..., None])
out = np.clip(tela, 0, 1)
img = cv2.cvtColor((out * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
cv2.imwrite(sys.argv[1], img)
print("ok", img.shape)
