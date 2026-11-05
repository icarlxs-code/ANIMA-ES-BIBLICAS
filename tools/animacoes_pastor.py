"""Gera as operações batch_edit (MCP do Rigby2D) das animações-base do pastor jovem.

Convenções do Rigby2D: valores relativos à pose de setup; rotate em graus (anti-horário +);
translate no espaço do osso-pai (hip e alvos IK são filhos de root = espaço do mundo, Y para cima);
scale multiplica. Personagem de FRENTE para a câmera.

Princípios usados: antecipação, overshoot + assentamento, defasagem entre partes (overlap),
follow-through no cabelo e na túnica (cadeia robe_1..3), easing em vez de linear, piscadas e
sacadas de olhar curtas.

Uso: python3 tools/animacoes_pastor.py <pasta_saida>  -> escreve um JSON por animação
"""
import json
import sys
from pathlib import Path

EASE = "easeInOut"


class Anim:
    def __init__(self, name):
        self.name = name
        self.ops = [{"op": "add_animation", "name": name}]

    def keys(self, bone, channel, pts, curve=EASE):
        """pts: [(t, valor)] ou [(t, (x, y))]; curva por chave (ou tupla (t, v, curva))."""
        for p in pts:
            t, v = p[0], p[1]
            c = p[2] if len(p) > 2 else curve
            op = {"op": "set_bone_key", "animation": self.name, "bone": bone, "channel": channel,
                  "time": round(t, 4), "curve": c}
            if isinstance(v, tuple):
                op["x"], op["y"] = v
            else:
                op["value"] = v
            self.ops.append(op)
        return self

    def swap(self, slot, t, attachment=None, hide=False):
        op = {"op": "set_attachment_key", "animation": self.name, "slot": slot, "time": round(t, 4)}
        if hide:
            op["hide"] = True
        else:
            op["attachment"] = attachment
        self.ops.append(op)
        return self

    def blink(self, t, dur=0.1):
        # Rigby2D 0.4.3 aplica a 1ª chave de anexo também ANTES dela: fixa "aberto" em t=0.
        if not getattr(self, "_olhos_t0", False):
            self._olhos_t0 = True
            for s in ("l", "r"):
                self.swap(f"eye_{s}", 0, f"eye_{s}").swap(f"pupil_{s}", 0, f"pupil_{s}")
        for s in ("l", "r"):
            self.swap(f"eye_{s}", t, f"eye_{s}_closed").swap(f"pupil_{s}", t, hide=True)
            self.swap(f"eye_{s}", t + dur, f"eye_{s}").swap(f"pupil_{s}", t + dur, f"pupil_{s}")
        return self


def respirar():
    """Idle 3 s em loop: respiração, peso, piscada."""
    a = Anim("respirar")
    a.keys("chest", "scale", [(0, (1, 1)), (1.4, (1.012, 1.004)), (3.0, (1, 1))])
    a.keys("neck", "rotate", [(0, 0), (1.6, 0.5), (3.0, 0)])
    a.keys("head", "rotate", [(0, 0), (1.8, -0.8), (3.0, 0)])
    a.keys("hip", "translate", [(0, (0, 0)), (1.5, (-1.5, -1)), (3.0, (0, 0))])
    a.keys("ik_hand_r", "translate", [(0, (0, 0)), (1.5, (-1.5, 2)), (3.0, (0, 0))])
    a.keys("ik_hand_l", "translate", [(0, (0, 0)), (1.6, (-1, 1.5)), (3.0, (0, 0))])
    a.keys("robe_1", "rotate", [(0, 0), (1.7, 0.3), (3.0, 0)])
    a.keys("hair", "rotate", [(0, 0), (2.0, 0.6), (3.0, 0)])
    a.keys("pupil_l", "translate", [(0, (0, 0)), (0.9, (0, 0)), (1.0, (-2, 0.5)), (2.3, (-2, 0.5)), (2.4, (0, 0)), (3.0, (0, 0))])
    a.keys("pupil_r", "translate", [(0, (0, 0)), (0.9, (0, 0)), (1.0, (-2, 0.5)), (2.3, (-2, 0.5)), (2.4, (0, 0)), (3.0, (0, 0))])
    a.blink(2.38)
    return a


def caminhada_frente():
    """Ciclo de 1 s (2 passos) no lugar, vista frontal. Pés em IK; quadril sobe na passagem e
    desce no contato; peso troca de lado; tronco e cabeça contra-rotacionam com atraso; túnica,
    cabelo e mãos seguem com defasagem."""
    a = Anim("caminhada_frente")
    a.keys("ik_foot_l", "translate", [(0, (0, 0)), (0.06, (0, 3), "easeOut"), (0.22, (-6, 10)),
                                      (0.40, (0, 5), "easeIn"), (0.5, (0, 0)), (1.0, (0, 0))])
    a.keys("ik_foot_r", "translate", [(0, (0, 0)), (0.5, (0, 0)), (0.56, (0, 3), "easeOut"), (0.72, (6, 10)),
                                      (0.90, (0, 5), "easeIn"), (1.0, (0, 0))])
    a.keys("hip", "translate", [(0, (0, -5)), (0.06, (-2, -7)), (0.27, (-8, 4)), (0.5, (0, -5)),
                                (0.56, (2, -7)), (0.77, (8, 4)), (1.0, (0, -5))])
    a.keys("hip", "rotate", [(0, 0), (0.25, -2.2), (0.5, 0), (0.75, 2.2), (1.0, 0)])
    a.keys("chest", "rotate", [(0, -0.5), (0.29, 1.6), (0.79, -1.6), (1.0, -0.5)])
    a.keys("head", "rotate", [(0, 0.4), (0.32, -1.1), (0.82, 1.1), (1.0, 0.4)])
    a.keys("head", "translate", [(0, (0, 0)), (0.1, (-1.5, 0)), (0.33, (1, 0)), (0.6, (-1.5, 0)), (0.83, (1, 0)), (1.0, (0, 0))])
    a.keys("hair", "rotate", [(0, 0.6), (0.17, -1.2), (0.42, 1.0), (0.67, -1.2), (0.92, 1.0), (1.0, 0.6)])
    # túnica: arrasto oposto à velocidade lateral do quadril, cada elo mais atrasado e mais amplo
    for bone, amp, lag in (("robe_1", 1.0, 0.08), ("robe_2", 1.4, 0.14), ("robe_3", 1.8, 0.20)):
        a.keys(bone, "rotate", [(0, round(amp * _cos(lag), 3)), (lag, amp), (lag + 0.5, -amp), (1.0, round(amp * _cos(lag), 3))])
    # mão livre: acompanha o quadril com atraso + balanço (braço oposto à perna)
    a.keys("ik_hand_r", "translate", [(0, (0, -5)), (0.06, (-2, -7)), (0.3, (-6, 9)), (0.5, (0, -5)), (0.56, (2, -7)), (0.8, (9, 5)), (1.0, (0, -5))])
    # punho livre arrastado pelo antebraço (follow-through), meio ciclo atrasado em relação ao balanço
    a.keys("hand_r", "rotate", [(0, 1.5), (0.38, -3.5), (0.88, 3.5), (1.0, 1.5)])
    # mão do cajado: acompanha o corpo; o cajado avança um pouco no passo da esquerda
    a.keys("ik_hand_l", "translate", [(0, (0, -5)), (0.06, (-2, -7)), (0.27, (-8, 4)), (0.5, (0, -5)), (0.56, (2, -7)), (0.77, (8, 4)), (1.0, (0, -5))])
    return a


def _cos(lag):
    import math
    return math.cos(2 * math.pi * (0 - lag))


def fala(name, dur):
    """A atuação da conversa reescalada para a duração de uma fala; boca em repouso em t=0
    (o lip_sync preenche o resto a partir do áudio)."""
    a = conversa()
    k = dur / 4.0
    a.name = name
    for op in a.ops:
        if op["op"] == "add_animation":
            op["name"] = name
        else:
            op["animation"] = name
            op["time"] = round(op["time"] * k, 4)
    a.swap("mouth", 0, "mouth_rest")
    return a


def conversa():
    """4 s: escuta empática e fala com gesto da mão direita.
    Antecipação (cabeça desce e mão cai antes de subir), overshoot e assentamento, aceno de
    cabeça na ênfase, sacada de olhar com piscada, sobrancelhas na ênfase."""
    a = Anim("conversa")
    a.keys("chest", "scale", [(0, (1, 1)), (1.8, (1.012, 1.004)), (4.0, (1, 1))])
    a.keys("chest", "rotate", [(0, 0), (0.7, 1.2), (3.0, 0.6), (4.0, 0)])
    a.keys("neck", "rotate", [(0, 0), (0.3, 0.5), (0.8, 2.0), (2.5, 1.2), (3.2, 0), (4.0, 0)])
    a.keys("head", "rotate", [(0, 0), (0.35, -1.2), (0.9, 4.5, "easeOut"), (1.2, 3.8), (1.9, 3.5), (2.6, 0.8), (3.3, 1.5), (4.0, 0)])
    a.keys("head", "translate", [(0, (0, 0)), (1.9, (0, 0)), (2.1, (-5, 0)), (2.35, (1, 0)), (2.55, (0, 0)), (4.0, (0, 0))])
    for s in ("l", "r"):
        a.keys(f"brow_{s}", "translate", [(0, (0, 0)), (0.8, (3.5, 0)), (1.6, (1.5, 0)), (1.95, (5, 0), "easeOut"),
                                          (2.5, (1, 0)), (4.0, (0, 0))])
        a.keys(f"pupil_{s}", "translate", [(0, (0, 0)), (0.45, (-3.5, 0), "easeOut"), (2.6, (-3.5, 0)), (2.72, (2.5, 2), "easeOut"),
                                           (3.2, (2.5, 2)), (3.32, (-3, 0), "easeOut"), (3.9, (-3, 0)), (4.0, (0, 0))])
    a.blink(1.35).blink(3.3)
    # gesto (cotovelo junto à cintura, antebraço abre para o lado): antecipação -> sobe -> overshoot -> assenta -> batida na ênfase -> desce
    a.keys("ik_hand_r", "translate", [(0, (0, 0)), (0.6, (2, -6)), (1.1, (-171, 106), "easeOut"), (1.25, (-180, 114)), (1.45, (-171, 104)),
                                      (2.0, (-166, 100)), (2.15, (-168, 90)), (2.4, (-166, 98)), (2.9, (-160, 95)),
                                      (3.35, (4, 6), "easeOut"), (3.55, (0, -3)), (3.8, (0, 0)), (4.0, (0, 0))])
    a.keys("hand_r", "rotate", [(0, 0), (0.7, 6), (1.3, -14), (1.5, -9), (2.9, -10), (3.45, 4), (3.75, 0), (4.0, 0)])
    a.keys("ik_hand_l", "translate", [(0, (0, 0)), (2.0, (-1, 3)), (4.0, (0, 0))])
    a.keys("robe_1", "rotate", [(0, 0), (1.0, -0.6), (2.5, 0.3), (4.0, 0)])
    a.keys("hair", "rotate", [(0, 0), (1.05, -1.5), (1.4, 0.8), (1.7, -0.3), (2.25, 1.0), (2.6, -0.5), (4.0, 0)])
    return a


# ---------- expressões: animações temporárias de 1 quadro, depois salvas como poses ----------
FACE_BONES = ["head", "brow_l", "brow_r", "eye_l", "eye_r", "pupil_l", "pupil_r", "mouth"]


def expressoes():
    ex = {}

    def e(name):
        a = Anim(f"_pose_{name}")
        ex[name] = a
        return a

    e("alegre").keys("brow_l", "translate", [(0, (3, 0))]).keys("brow_r", "translate", [(0, (3, 0))]) \
        .keys("eye_l", "scale", [(0, (1, 0.8))]).keys("eye_r", "scale", [(0, (1, 0.8))]) \
        .keys("head", "rotate", [(0, 2)]).swap("mouth", 0, "mouth_E")
    e("triste").keys("brow_l", "rotate", [(0, -10)]).keys("brow_r", "rotate", [(0, 10)]) \
        .keys("brow_l", "translate", [(0, (-1, 0))]).keys("brow_r", "translate", [(0, (-1, 0))]) \
        .keys("eye_l", "scale", [(0, (1, 0.88))]).keys("eye_r", "scale", [(0, (1, 0.88))]) \
        .keys("pupil_l", "translate", [(0, (0, -2))]).keys("pupil_r", "translate", [(0, (0, -2))]) \
        .keys("head", "rotate", [(0, -3)]).keys("head", "translate", [(0, (-4, 0))]).swap("mouth", 0, "mouth_rest")
    e("preocupado").keys("brow_l", "rotate", [(0, -12)]).keys("brow_r", "rotate", [(0, 12)]) \
        .keys("brow_l", "translate", [(0, (3, 0))]).keys("brow_r", "translate", [(0, (3, 0))]) \
        .keys("pupil_l", "translate", [(0, (-2.5, 0))]).keys("pupil_r", "translate", [(0, (-2.5, 0))]) \
        .swap("mouth", 0, "mouth_MBP")
    e("surpreso").keys("brow_l", "translate", [(0, (8, 0))]).keys("brow_r", "translate", [(0, (8, 0))]) \
        .keys("eye_l", "scale", [(0, (1.08, 1.22))]).keys("eye_r", "scale", [(0, (1.08, 1.22))]) \
        .keys("head", "translate", [(0, (3, 0))]).swap("mouth", 0, "mouth_O")
    return ex


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for a in (respirar(), caminhada_frente(), conversa(), fala("fala_teste", 5.6)):
        (out / f"{a.name}.json").write_text(json.dumps(a.ops, indent=1))
        print(a.name, len(a.ops) - 1, "chaves")
    ex = expressoes()
    ops = [op for a in ex.values() for op in a.ops]
    (out / "_expressoes_temp.json").write_text(json.dumps(ops, indent=1))
    print("expressões temporárias:", list(ex))


if __name__ == "__main__":
    main(sys.argv[1])
