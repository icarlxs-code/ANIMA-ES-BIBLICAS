"""Teste de desenho no Moho: cabeça frontal do pastor jovem em vetor nativo do Moho.

Gera um projeto .moho (ZIP com Project.mohoproj) a partir de um tutorial do próprio Moho 14.5,
usado só como modelo de estrutura, e uma prévia raster das mesmas formas (para a revisão,
NÃO é o render do Moho).

Uso:  python -I gerar_teste_cabeca.py <saida.moho> <previa.png>
"""
import copy, json, math, sys, uuid, zipfile
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from PIL import Image, ImageDraw

MODELO = r"C:\Users\User\Desktop\Moho Pro\Tutorials\1 - Basics\Tutorial 1.02.moho"
W, H = 1000, 1150          # espaço de desenho em px (y para baixo)
ESCALA = 1.7 / H           # altura do desenho = 1,7 unidade do Moho


def hexa(c, a=1.0):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


# Paleta da BIBLIA_VISUAL.md + tons de oclusão
PELE, PELE_S, PELE_O = hexa("#c68a5c"), hexa("#8e5532"), hexa("#6a3a22")
PELE_L = hexa("#e0a777")
CABELO, CABELO_L = hexa("#2a1b12"), hexa("#4a3122")
COURO, COURO_S = hexa("#6e4527"), hexa("#45291a")
TUNICA, TUNICA_S = hexa("#d8c6a0"), hexa("#a08a63")
COLETE, COLETE_S = hexa("#efe5cf"), hexa("#b8a582")
OLHO_B, IRIS, PUPILA = hexa("#ead8c0"), hexa("#5a3218"), hexa("#1a0e08")
FUNDO_A, FUNDO_B = hexa("#4f4a48"), hexa("#8a8480")


# ---------------- geometria ----------------
def catmull(pts, fechado=True, n=14):
    """Curva suave (Catmull-Rom) pelos pontos de controle."""
    out, P = [], list(pts)
    m = len(P)
    rng = range(m) if fechado else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if fechado else P[max(i - 1, 0)]
        p1, p2 = P[i], P[(i + 1) % m]
        p3 = P[(i + 2) % m] if fechado else P[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not fechado:
        out.append(P[-1])
    return out


def traco(pts, w0, w1=None, wm=None, n=10):
    """Traço afinado nas pontas como polígono preenchido."""
    w1 = w0 if w1 is None else w1
    c = catmull(pts, fechado=False, n=n)
    esq, dir_ = [], []
    for i, p in enumerate(c):
        a, b = c[max(i - 1, 0)], c[min(i + 1, len(c) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        t = i / (len(c) - 1)
        w = (w0 + (w1 - w0) * t) if wm is None else (w0 * (1 - t) ** 2 + 2 * wm * t * (1 - t) + w1 * t * t)
        nx, ny = -dy / L * w / 2, dx / L * w / 2
        esq.append((p[0] + nx, p[1] + ny)); dir_.append((p[0] - nx, p[1] - ny))
    return Polygon(esq + dir_[::-1]).buffer(0)


def cachos(cx, cy, rx, ry, n, amp, fase=0.0, a0=0, a1=2 * math.pi):
    """Contorno ondulado (massa de cachos)."""
    pts = []
    for i in range(n * 12):
        a = a0 + (a1 - a0) * i / (n * 12)
        r = 1 + amp * abs(math.sin(n * (a - a0) / ((a1 - a0) / math.pi) / 2 * 2 + fase)) ** 0.6
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    return Polygon(pts).buffer(0)


def elip(cx, cy, rx, ry, rot=0, n=64):
    c, s = math.cos(rot), math.sin(rot)
    return Polygon([(cx + rx * math.cos(t) * c - ry * math.sin(t) * s,
                     cy + rx * math.cos(t) * s + ry * math.sin(t) * c)
                    for t in (2 * math.pi * i / n for i in range(n))])


def cachinho(cx, cy, r, ang=0.0):
    """Um cacho: espiral grossa curta."""
    pts = [(cx + r * (0.35 + 0.65 * t) * math.cos(ang + t * 4.2), cy + r * (0.35 + 0.65 * t) * math.sin(ang + t * 4.2))
           for t in (i / 9 for i in range(10))]
    return traco(pts, r * 0.18, r * 0.5, wm=r * 0.55, n=6)


# ---------------- desenho ----------------
formas = []   # (nome, geometria, cor, contorno_cor_ou_None)


def F(nome, g, cor, contorno=None):
    formas.append((nome, g, cor, contorno))


cx = 500
# rosto
rosto = Polygon(catmull([(cx, 300), (612, 330), (660, 430), (655, 560), (628, 690), (585, 800), (540, 870),
                         (cx, 888), (460, 870), (415, 800), (372, 690), (345, 560), (340, 430), (388, 330)], n=16))
pescoco = Polygon(catmull([(440, 820), (560, 820), (575, 960), (600, 1040), (400, 1040), (425, 960)], n=10))
orelha_e = elip(343, 590, 34, 62, 0.15)
orelha_d = elip(657, 590, 34, 62, -0.15)

# fundo
for i in range(12):
    t = i / 11
    F("fundo", box(0, H * i / 12, W, H), tuple(int(FUNDO_A[j] + (FUNDO_B[j] - FUNDO_A[j]) * t) for j in range(3)) + (1.0,))

cabelo_tras = unary_union([cachos(cx, 430, 230, 240, 9, 0.10, 0.3), elip(cx, 600, 215, 200)])
F("cabelo_tras", cabelo_tras, CABELO, COURO_S)

# roupa (gola da túnica e colete de pele)
tunica = Polygon(catmull([(330, 1010), (430, 975), (cx, 1000), (570, 975), (670, 1010), (760, 1150), (240, 1150)], n=10))
F("tunica", tunica, TUNICA, TUNICA_S)
F("tunica_sombra", tunica.intersection(Polygon([(cx + 20, 960), (W, 960), (W, H), (cx + 60, H)])), TUNICA_S)
gola = Polygon(catmull([(445, 985), (cx, 1080), (555, 985), (565, 1000), (cx, 1105), (435, 1000)], n=8))
F("gola", gola, TUNICA_S)
for lado in (-1, 1):
    colete = Polygon([(cx + lado * 150, 1000), (cx + lado * 260, 1040), (cx + lado * 320, 1150), (cx + lado * 120, 1150)])
    F("colete", colete, COLETE if lado < 0 else COLETE_S, COLETE_S)
    la = unary_union([elip(cx + lado * (150 + 9 * k), 1020 + 14 * k, 16, 14) for k in range(10)])
    F("colete_la", la, COLETE if lado < 0 else hexa("#d9ccb0"))

F("pescoco", pescoco, PELE, PELE_S)
F("pescoco_sombra", pescoco.intersection(unary_union([
    Polygon([(cx + 10, 800), (W, 800), (W, H), (cx + 40, H)]),
    Polygon(catmull([(420, 820), (cx, 900), (580, 820), (580, 790), (420, 790)], n=8))])), PELE_S)
F("pescoco_oclusao", pescoco.intersection(Polygon(catmull([(430, 820), (cx, 870), (570, 820), (570, 800), (430, 800)], n=8))), PELE_O)

F("orelha_esq", orelha_e, PELE, PELE_S)
F("orelha_dir", orelha_d, PELE_S, PELE_O)
F("orelha_dentro_esq", elip(347, 592, 15, 36, 0.15), PELE_S)
F("orelha_dentro_dir", elip(653, 592, 15, 36, -0.15), PELE_O)

F("cabeca_base", rosto, PELE, PELE_O)
# luz de borda (lado da luz, esquerda da imagem)
borda = rosto.difference(rosto.buffer(-9).union(box(cx - 60, 0, W, H)))
F("luz_borda", borda.intersection(box(0, 380, W, 820)), PELE_L)
# sombra própria em bloco: lado direito, com terminador ondulado pela maçã do rosto
term = Polygon(catmull([(548, 300), (560, 420), (552, 470), (566, 560), (600, 640), (590, 720), (572, 790),
                        (548, 860), (520, 900), (W, 900), (W, 300)], fechado=True, n=12))
F("rosto_sombra", rosto.intersection(term), PELE_S)
# oclusão sob o cabelo e o queixo
F("rosto_oclusao_testa", rosto.intersection(Polygon(catmull([(300, 380), (cx, 405), (700, 380), (700, 250), (300, 250)], n=10))), PELE_S)
F("olheira_esq", traco([(400, 548), (430, 560), (465, 556)], 3, 3, wm=10), hexa("#a96d45"))
F("olheira_dir", traco([(535, 556), (570, 560), (600, 548)], 3, 3, wm=10), PELE_O)

# olhos: amendoados, grandes e atentos; pálpebra superior grossa
for lado, ox in ((-1, 432), (1, 568)):
    esc = lado > 0
    olho = Polygon(catmull([(ox - 40, 512), (ox - 12, 494), (ox + 18, 496), (ox + 40, 510), (ox + 14, 526), (ox - 18, 525)], n=10))
    F(f"olho_{'dir' if esc else 'esq'}", olho, hexa("#c9b39a") if esc else OLHO_B)
    iris = elip(ox + 2 * lado - 2, 510, 17, 18).intersection(olho)
    F(f"iris_{'dir' if esc else 'esq'}", iris, IRIS)
    F("pupila", elip(ox + 2 * lado - 2, 511, 8, 9).intersection(olho), PUPILA)
    F("brilho", elip(ox - 6 + 2 * lado, 503, 5, 5), hexa("#f4ece0"))
    F("sombra_palpebra", olho.intersection(Polygon([(ox - 50, 480), (ox + 50, 480), (ox + 50, 506), (ox - 50, 503)])), hexa("#7a4a30", 0.55))
    palp = traco([(ox - 44, 515), (ox - 22, 494), (ox + 8, 490), (ox + 36, 499), (ox + 46, 511)], 4, 3, wm=11)
    F("palpebra", palp, CABELO)
    F("dobra_palpebra", traco([(ox - 34, 492), (ox, 478), (ox + 34, 486)], 2, 2, wm=5), PELE_O if esc else PELE_S)
    F("palpebra_inf", traco([(ox - 30, 526), (ox, 531), (ox + 34, 520)], 1.5, 1, wm=3.5), PELE_O if esc else PELE_S)
    # sobrancelhas grossas, parte interna levemente erguida
    if lado < 0:
        sob = traco([(386, 470), (410, 456), (440, 452), (468, 446), (482, 436)], 9, 13, wm=20)
    else:
        sob = traco([(518, 436), (532, 446), (560, 452), (590, 456), (614, 470)], 13, 9, wm=20)
    F(f"sobrancelha_{'dir' if esc else 'esq'}", sob, CABELO)

# nariz longo e pesado, do meio das sobrancelhas até perto da boca, ponta redonda
nariz_luz = Polygon(catmull([(492, 455), (486, 540), (476, 640), (470, 690), (480, 718), (500, 724), (505, 690),
                             (503, 600), (503, 500)], n=10))
F("nariz_plano_luz", nariz_luz, hexa("#d39869"))
nariz_sombra = Polygon(catmull([(510, 458), (515, 560), (528, 650), (545, 700), (534, 728), (510, 734), (506, 690),
                                (506, 560)], n=10))
F("nariz_sombra", nariz_sombra, PELE_O)
F("nariz_ponta", elip(503, 706, 30, 26), PELE)
F("nariz_ponta_sombra", elip(503, 706, 30, 26).intersection(box(506, 0, W, H)), PELE_S)
F("nariz_ponta_luz", elip(492, 700, 9, 7), PELE_L)
F("asa_nariz_esq", traco([(470, 700), (466, 718), (478, 734)], 3, 2, wm=6), PELE_S)
F("asa_nariz_dir", traco([(536, 700), (541, 718), (528, 734)], 3, 2, wm=6), PELE_O)
F("narinas", unary_union([elip(489, 734, 7, 4, 0.3), elip(518, 734, 7, 4, -0.3)]), PELE_O)
F("sombra_projetada_nariz", rosto.intersection(Polygon(catmull([(510, 740), (545, 732), (560, 752), (520, 762)], n=6))), PELE_O)

# boca pequena; lábio inferior marcado por sombra
F("boca_linha", traco([(472, 790), (488, 786), (503, 789), (518, 786), (534, 791)], 3, 3, wm=5), hexa("#5c2f1c"))
F("labio_sup", Polygon(catmull([(474, 789), (488, 779), (503, 783), (518, 779), (532, 789), (503, 788)], n=6)), hexa("#a7643f"))
F("labio_inf_sombra", Polygon(catmull([(482, 806), (503, 812), (526, 806), (518, 818), (503, 822), (488, 818)], n=6)), PELE_S)
F("buco", Polygon(catmull([(470, 772), (503, 768), (538, 772), (530, 778), (503, 775), (476, 778)], n=6)), hexa("#5a3420", 0.28))
F("penugem_queixo", Polygon(catmull([(475, 850), (503, 862), (530, 850), (522, 872), (503, 880), (484, 872)], n=6)), hexa("#4a2c1a", 0.25))
F("queixo_luz", elip(492, 845, 14, 9), hexa("#d39869"))

# cordão de couro na testa (fica sob os cachos da frente)
cordao = traco([(330, 410), (420, 388), (cx, 382), (580, 388), (670, 410)], 13, 13)
F("cordao", cordao, COURO, COURO_S)
F("cordao_sombra", cordao.intersection(box(560, 0, W, H)), COURO_S)
F("cordao_no", elip(372, 404, 14, 11), COURO_S)

# cabelo da frente: cachos volumosos no alto, cobrindo metade das orelhas
topo = cachos(cx, 300, 235, 150, 11, 0.12, 1.0)
lateral_e = Polygon(catmull([(330, 380), (360, 430), (352, 520), (338, 580), (318, 600), (300, 540), (296, 420)], n=8))
lateral_d = Polygon(catmull([(670, 380), (704, 420), (700, 540), (682, 600), (662, 580), (648, 520), (640, 430)], n=8))
franja = unary_union([elip(cx + dx, 378 + dy, 30, 24) for dx, dy in
                      [(-120, 10), (-75, 0), (-30, 6), (15, -2), (60, 6), (105, 2), (140, 12)]])
cabelo = unary_union([topo.difference(box(0, 382, W, H)), lateral_e, lateral_d, franja])
F("cabelo_frente", cabelo, CABELO, COURO_S)
F("cabelo_luz", cabelo.intersection(Polygon(catmull([(250, 330), (300, 220), (390, 160), (420, 190), (340, 280), (300, 400)], n=8))), hexa("#36241a"))
for (x, y, r, a) in [(330, 240, 26, 0.4), (380, 190, 28, 1.2), (440, 165, 26, 2.0), (510, 158, 28, 0.8), (575, 175, 26, 2.6),
                     (630, 215, 26, 1.6), (670, 280, 24, 0.2), (300, 310, 22, 2.2), (360, 300, 24, 3.0), (430, 270, 26, 1.0),
                     (500, 250, 26, 2.4), (570, 265, 24, 0.6), (630, 330, 22, 1.8), (310, 470, 20, 1.2), (685, 480, 20, 2.8),
                     (400, 360, 20, 0.3), (470, 345, 20, 1.9), (540, 350, 20, 2.7), (605, 368, 18, 1.1)]:
    F("cacho_luz" if x < cx else "cacho_sombra", cachinho(x, y, r, a), CABELO_L if x < cx else hexa("#1a100a"))


F("cordao", cordao, COURO, COURO_S)
F("cordao_luz", traco([(335, 406), (420, 384), (470, 378)], 3, 1), hexa("#8f6040"))
F("cordao_sombra", cordao.intersection(box(560, 0, W, H)), COURO_S)
F("cordao_no", elip(372, 404, 14, 11), COURO_S)
F("cordao_pontas", unary_union([traco([(372, 410), (366, 450), (372, 480)], 5, 3), traco([(378, 410), (386, 446), (384, 470)], 5, 3)]), COURO, COURO_S)
for dx, dy in [(-30, 2), (20, -2), (70, 4)]:
    F("cacho_franja", elip(cx + dx, 390 + dy, 22, 20), CABELO, COURO_S)
    F("cacho_franja_luz", cachinho(cx + dx - 4, 388 + dy, 14, 2.0), hexa("#3d281c"))


# ---------------- prévia raster ----------------
def previa(caminho, s=2):
    im = Image.new("RGBA", (W * s, H * s))
    for nome, g, cor, cont in formas:
        camada = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(camada)
        rgba = tuple(cor[:3]) + (int(cor[3] * 255),)
        for p in (getattr(g, "geoms", None) or [g]):
            if p.is_empty or p.geom_type != "Polygon":
                continue
            d.polygon([(x * s, y * s) for x, y in p.exterior.coords], fill=rgba,
                      outline=(tuple(cont[:3]) + (255,)) if cont else None, width=3 if cont else 0)
            for i in p.interiors:
                d.polygon([(x * s, y * s) for x, y in i.coords], fill=(0, 0, 0, 0))
        im = Image.alpha_composite(im, camada)
    im.convert("RGB").resize((W, H), Image.LANCZOS).save(caminho)


# ---------------- projeto Moho ----------------
def moho(caminho):
    z = zipfile.ZipFile(MODELO)
    proj = json.loads(z.read("Project.mohoproj"))
    camada_modelo = next(l for l in proj["layers"] if l["type"] == "MeshLayer")
    m0 = camada_modelo["mesh"]
    ponto0, curva0, forma0 = m0["points"][0], m0["curves"][0], m0["shapes"][0]
    cp0 = curva0["points"][0]

    pd = proj["project_data"]
    pd["width"], pd["height"], pd["start_frame"], pd["end_frame"] = 1000, 1150, 1, 1

    camada = copy.deepcopy(camada_modelo)
    camada["name"], camada["uuid"] = "cabeca_teste", str(uuid.uuid4())
    for k in ("layer_effects", "layer_shadow", "layer_shading", "perspective_shadow", "motion_blur", "layer_outline"):
        if k in camada_modelo and isinstance(camada_modelo[k], dict) and "enabled" in camada_modelo[k]:
            camada[k]["enabled"] = False
    pts, curvas, shapes = [], [], []

    def cor_moho(c):
        return {"r": round(c[0] / 255, 6), "g": round(c[1] / 255, 6), "b": round(c[2] / 255, 6), "a": c[3]}

    for nome, g, cor, cont in formas:
        for p in (getattr(g, "geoms", None) or [g]):
            if p.is_empty or p.geom_type != "Polygon":
                continue
            p = p.simplify(0.6)
            anel = list(p.exterior.coords)[:-1]
            if len(anel) < 3:
                continue
            ic = len(curvas)
            base = len(pts)
            curva = copy.deepcopy(curva0)
            curva["num_points"], curva["closed"] = len(anel), True
            curva["points"] = []
            for k, (x, y) in enumerate(anel):
                pt = copy.deepcopy(ponto0)
                pt["position"]["val"] = [{"x": round((x - W / 2) * ESCALA, 6), "y": round(-(y - H / 2) * ESCALA, 6)}]
                pt["curves"] = [{"curve": ic, "curve_points": k}]
                pts.append(pt)
                c = copy.deepcopy(cp0)
                c["point"] = base + k
                c["smoothness"]["val"] = [0.001]
                curva["points"].append(c)
            curvas.append(curva)
            sh = copy.deepcopy(forma0)
            sh["name"], sh["id"], sh["selected"] = nome, len(shapes), False
            sh["has_fill"], sh["has_outline"] = True, bool(cont)
            sh["edges"] = {"curve": [ic] * len(anel), "segment": list(range(len(anel))), "flag": [0] * len(anel)}
            st = sh["style"]
            st["uuid"] = str(uuid.uuid4())
            st.pop("fill_style", None); st.pop("fill_style_id", None)
            st["fill_color"]["val"] = [cor_moho(cor)]
            st["line_color"]["val"] = [cor_moho(cont if cont else cor)]
            st["line_width"] = 0.0021
            shapes.append(sh)

    m = camada["mesh"]
    m["points"], m["curves"], m["shapes"], m["groups"] = pts, curvas, shapes, []
    m["next_shape_id"] = len(shapes)
    m["shape_order"]["val"] = ["|".join(str(i) for i in range(len(shapes)))]
    proj["layers"] = [camada]
    proj["doc_uuid"] = str(uuid.uuid4())
    with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as out:
        out.writestr("Project.mohoproj", json.dumps(proj))
        out.writestr("preview.jpg", z.read("preview.jpg"))
    return len(shapes), len(pts)


if __name__ == "__main__":
    print("formas/pontos:", moho(sys.argv[1]))
    previa(sys.argv[2])
