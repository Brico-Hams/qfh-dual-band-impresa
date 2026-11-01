#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BricoHams - Plantilla de taladros para la QFH doble banda (2 m / 70 cm).

Genera una tira de papel a escala 1:1 que se enrolla alrededor del tubo central
de 30 mm y marca todos los taladros (tornillos M4 de los soportes y entradas de
los hilos de alimentación).

Uso (solo biblioteca estándar de Python 3, resultado determinista):

    python plantilla_taladros.py

Escribe en la raíz del repositorio (junto a este script):
    plantilla_taladros.svg        tira completa (sin partir)
    plantilla_taladros_p1.svg ... una hoja A4 vertical por SVG
    plantilla_taladros.pdf        todas las hojas A4 en un PDF listo para imprimir

Los parámetros del tubo y de los tornillos se leen de qfh_piezas.scad.
Las alturas y giros de los soportes están en MONTAJE.md (tabla "Posiciones en el
tubo"); aquí se repiten en SOPORTES y verificar() comprueba que coinciden.
"""

import math
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ  # raíz del repositorio

# ---------- tabla de soportes (idéntica a MONTAJE.md, "Posiciones en el tubo") ----------
# (nombre, tipo, z en mm desde la cruceta VHF, giro del soporte en grados)
SOPORTES = [
    ("cruceta_vhf",              "cruceta_vhf", 0,    0),
    ("cruceta_uhf",              "uhf",         -30,  0),
    ("barra_uhf_peq",            "uhf",         -236, 90),
    ("barra_uhf_grande",         "uhf",         -248, 0),
    ("barra_vhf media pequeña",  "barra_vhf",   -307, 0),
    ("barra_vhf media grande",   "barra_vhf",   -325, 90),
    ("barra_vhf abajo pequeña",  "barra_vhf",   -615, 90),
    ("barra_vhf abajo grande",   "barra_vhf",   -650, 0),
]

# ---------- entrada de los hilos de alimentación ----------
FEED_D = 4.0                      # hilo 2,5 mm + aislante
FEED_ANGULOS = [0, 90, 180, 270]  # extremos cortados de los hilos horizontales
# z = punto medio del hueco entre el manguito VHF (z = 0) y el UHF (z = -30)
# (se calcula en construir() con manguito_h)

# ---------- papel y composición ----------
A4_W, A4_H = 210.0, 297.0
MARGEN_IMP = 10.0            # margen de impresora
X0 = 10.0                    # borde izquierdo de la tira en la hoja
Y0 = 20.0                    # borde superior de la ventana de la tira
VENTANA = 260.0              # alto de tira por hoja (Y0 .. Y0+260 = 280)
SOLAPE = 10.0                # solape entre hojas consecutivas
PASO = VENTANA - SOLAPE      # avance de tira entre hojas
MARGEN_Z = 20.0              # margen de tira sobre z = 0 y bajo el último soporte
PESTANA = 15.0               # solapa de pegado
ANG0 = -75.0                 # ángulo del borde izquierdo de la tira (el corte queda lejos de los taladros)
COL_X = 125.0                # columna derecha: cuadrado, leyenda
ESCALA_X = 195.0             # barra de escala vertical de 100 mm
LEYENDA_Y_MAX = 262.0

AZUL, ROJO, GRIS, NEGRO = "#0050c8", "#c81e1e", "#9a9a9a", "#000000"
TITULO = "BricoHams - Plantilla de taladros QFH 2 m / 70 cm"
AVISO = ("Imprimir al 100 % (sin ajustar a página). "
         "Comprueba que el cuadrado mide 50 mm")


def fmt(v, dec=1):
    """Número con coma decimal; sin decimales si es entero."""
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.{dec}f}".replace(".", ",")


# =====================================================================
#  Lectura de parámetros reales
# =====================================================================
def leer_parametros():
    t = (RAIZ / "qfh_piezas.scad").read_text(encoding="utf-8")

    def num(nombre):
        m = re.search(r"^\s*%s\s*=\s*([0-9.]+)\s*;" % nombre, t, re.M)
        if not m:
            raise ValueError(f"No encuentro {nombre} en qfh_piezas.scad")
        return float(m.group(1))

    def ang(patron):
        m = re.search(patron, t)
        if not m:
            raise ValueError(f"No encuentro {patron} en qfh_piezas.scad")
        return float(m.group(1))

    p = {
        "tubo_d": num("tubo_d"),
        "tornillo_d": num("tornillo_d"),
        "hilo_d": num("hilo_d"),
        "manguito_h": num("manguito_h"),
        # ángulo del tornillo dentro de cada pieza (respecto a sus brazos a 0°)
        "tornillo_ang": {
            "cruceta_vhf": ang(r'PIEZA == "cruceta_vhf"\)\s*cruceta_varillas\(\[[^\]]*\],\s*([0-9.]+)\)'),
            "barra_vhf": ang(r'PIEZA == "barra_vhf"\)\s*cruceta_varillas\(\[[^\]]*\],\s*([0-9.]+)\)'),
            "uhf": ang(r"bloque_tornillo\((\d+)\)"),
        },
    }
    uhf_agujero = ang(r"agujero_tornillo\((\d+)\)")
    assert uhf_agujero == p["tornillo_ang"]["uhf"], "bloque y agujero UHF no coinciden"
    return p


def construir():
    """Calcula toda la geometría de la plantilla (sin dibujar)."""
    p = leer_parametros()
    tubo_d = p["tubo_d"]
    circ = math.pi * tubo_d
    zmin = min(s[2] for s in SOPORTES)
    largo = MARGEN_Z + (-zmin) + MARGEN_Z
    n_hojas = max(1, math.ceil((largo - VENTANA) / PASO) + 1)

    agujeros = []
    for i, (nombre, tipo, z, giro) in enumerate(
            sorted(SOPORTES, key=lambda s: -s[2]), start=1):
        ang = (giro + p["tornillo_ang"][tipo]) % 360
        agujeros.append({"id": f"T{i}", "nombre": nombre + " (tornillo M4)",
                         "soporte": nombre, "tipo": "tornillo",
                         "z": float(z), "ang": float(ang), "d": p["tornillo_d"],
                         "giro": float(giro), "ang_rel": p["tornillo_ang"][tipo]})
    # hueco libre entre los manguitos de cruceta_vhf (z=0) y cruceta_uhf (z=-30)
    z_vhf, z_uhf = 0.0, -30.0
    z_feed = (z_vhf - p["manguito_h"] / 2 + z_uhf + p["manguito_h"] / 2) / 2
    for i, a in enumerate(FEED_ANGULOS, start=1):
        agujeros.append({"id": f"F{i}", "nombre": "entrada hilo alimentación",
                         "soporte": None, "tipo": "alimentacion",
                         "z": z_feed, "ang": float(a), "d": FEED_D})
    return {"p": p, "tubo_d": tubo_d, "circ": circ, "ancho": circ + PESTANA,
            "largo": largo, "n_hojas": n_hojas, "agujeros": agujeros,
            "soportes": SOPORTES, "z_feed": z_feed}


def x_de_ang(G, ang):
    return X0 + ((ang - ANG0) % 360.0) * G["circ"] / 360.0


def s_de_z(z):
    return MARGEN_Z - z  # distancia desde el borde superior de la tira


# =====================================================================
#  Primitivas de dibujo (independientes del formato)
# =====================================================================
def ancho_txt(s, size, neg=False):
    return len(s) * size * (0.56 if neg else 0.52)


class Hoja:
    def __init__(self):
        self.ops = []

    def linea(self, x1, y1, x2, y2, w=0.25, c=NEGRO, dash=None, tag=None):
        self.ops.append({"t": "linea", "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                         "w": w, "c": c, "dash": dash, "tag": tag})

    def linea_recortada(self, x1, y1, x2, y2, caja, **kw):
        # Liang-Barsky: recorta el segmento al rectángulo caja = (xmin, ymin, xmax, ymax)
        xmin, ymin, xmax, ymax = caja
        dx, dy = x2 - x1, y2 - y1
        t0, t1 = 0.0, 1.0
        for p, q in ((-dx, x1 - xmin), (dx, xmax - x1), (-dy, y1 - ymin), (dy, ymax - y1)):
            if p == 0:
                if q < 0:
                    return
            else:
                r = q / p
                if p < 0:
                    t0 = max(t0, r)
                else:
                    t1 = min(t1, r)
        if t0 >= t1:
            return
        self.linea(x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy, **kw)

    def circulo(self, cx, cy, r, w=0.25, c=NEGRO, dash=None, tag=None):
        self.ops.append({"t": "circulo", "cx": cx, "cy": cy, "r": r,
                         "w": w, "c": c, "dash": dash, "tag": tag})

    def rect(self, x, y, w, h, lw=0.25, c=NEGRO, tag=None):
        self.ops.append({"t": "rect", "x": x, "y": y, "w": w, "h": h,
                         "lw": lw, "c": c, "tag": tag})

    def texto(self, x, y, s, size=2.5, c=NEGRO, ancla="start", neg=False, rot=0):
        w = ancho_txt(s, size, neg)
        off = {"start": 0.0, "middle": w / 2, "end": w}[ancla]
        if rot == 0:
            x -= off
        else:  # -90: el texto sube
            y += off
        self.ops.append({"t": "texto", "x": x, "y": y, "s": s, "size": size,
                         "c": c, "neg": neg, "rot": rot})

    def clip_ini(self, x, y, w, h):
        self.ops.append({"t": "clip_ini", "x": x, "y": y, "w": w, "h": h})

    def clip_fin(self):
        self.ops.append({"t": "clip_fin"})


# =====================================================================
#  Contenido de cada hoja
# =====================================================================
def etiquetas_angulo(a):
    return ("brazos grande" if a in (0, 180) else "brazos pequeña")


def texto_leyenda(G):
    p = G["p"]
    L = []
    L.append(("LEYENDA", True))
    L.append((f"Tubo Ø{fmt(G['tubo_d'])} mm. Circunferencia = pi x {fmt(G['tubo_d'])} = "
              f"{fmt(G['circ'], 2)} mm, más {fmt(PESTANA)} mm de solapa para pegar.", False))
    L.append(("Ángulos: 0° = brazos de la espira grande, 90° = espira pequeña (MONTAJE.md). "
              "Con el dibujo hacia fuera y la parte superior arriba, crecen hacia la derecha "
              "(antihorario visto desde arriba). Borde izquierdo de la tira = "
              f"{fmt(ANG0)}°.", False))
    L.append(("z = 0 es el eje de la cruceta VHF; z negativa = hacia abajo.", False))
    L.append(("Taladros (z mm / ángulo / broca):", True))
    for h in G["agujeros"]:
        L.append((f"{h['id']}  {h['soporte'] or 'alimentación'}  z {fmt(h['z'])}  "
                  f"{fmt(h['ang'])}°  Ø{fmt(h['d'])}", False))
    L.append((f"T1-T8: tornillo M4 de cada soporte, broca {fmt(p['tornillo_d'])} mm. "
              "Ángulo = giro del soporte + posición del tornillo en la pieza "
              f"({fmt(p['tornillo_ang']['cruceta_vhf'])}° en crucetas y barras UHF, "
              f"{fmt(p['tornillo_ang']['barra_vhf'])}° en barras VHF; "
              "bloque_tornillo en qfh_piezas.scad). Altura = eje del soporte "
              f"(manguito_h/2 = {fmt(p['manguito_h'] / 2)} mm sobre su base), "
              "como en la tabla de MONTAJE.md.", False))
    L.append((f"F1-F4: entrada de los hilos de alimentación, broca {fmt(FEED_D)} mm "
              f"(hilo {fmt(p['hilo_d'])} mm + aislante). Suposición: a 0°, 90°, 180° y 270° "
              f"(extremos de los hilos horizontales cortados) y z {fmt(G['z_feed'])}, "
              "el hueco entre los manguitos VHF y UHF.", False))
    L.append(("Taladrar: 1) marca con granete; 2) pilotea con 2 mm; 3) broca final. "
              "Taladra perpendicular al eje del tubo, con el tubo en un bloque en V.", True))
    L.append(("Monta: pega la solapa, alinea la línea 0° con los brazos del primer soporte.", False))
    return L


def maquetar_leyenda(hoja, G, x, y0):
    lineas = texto_leyenda(G)
    for size in (2.4, 2.3, 2.2, 2.1, 2.0, 1.9, 1.8):
        ancho_car = int(60.0 / (size * 0.54))
        y = y0
        out = []
        for txt, neg in lineas:
            for r in _envolver(txt, ancho_car):
                out.append((y, r, neg))
                y += size * 1.35
            y += size * 0.3
        if out[-1][0] <= LEYENDA_Y_MAX:
            for yy, r, neg in out:
                hoja.texto(x, yy, r, size=size, neg=neg)
            return out[-1][0]
    raise ValueError("La leyenda no cabe en la hoja 1")


def _envolver(txt, ancho):
    import textwrap
    return textwrap.wrap(txt, ancho)


def dibujar_hoja(G, k):
    N = G["n_hojas"]
    h = Hoja()
    circ, W, L = G["circ"], G["ancho"], G["largo"]
    inicio = k * PASO
    alto = min(VENTANA, L - inicio)

    def y_de_s(s):
        return Y0 + (s - inicio)

    # --- cabecera y pie ---
    h.texto(MARGEN_IMP, 15.0, TITULO, size=4.5, neg=True)
    h.texto(A4_W - MARGEN_IMP, 15.0, f"Hoja {k + 1} de {N}", size=3.5, ancla="end", neg=True)
    pie = f"BricoHams QFH - plantilla de taladros - hoja {k + 1}/{N}"
    h.texto(MARGEN_IMP, 286.0, pie, size=2.4)
    if k < N - 1:
        h.texto(A4_W - MARGEN_IMP, 286.0,
                f"Abajo: une con hoja {k + 2} (solape {fmt(SOLAPE)} mm)",
                size=2.4, ancla="end", neg=True)

    # --- tira (recortada a la ventana) ---
    h.clip_ini(X0 - 1, Y0 - 0.5, W + 2, alto + 1)
    h.linea(X0, Y0, X0, Y0 + alto, w=0.4)                 # borde de corte izquierdo
    h.linea(X0 + W, Y0, X0 + W, Y0 + alto, w=0.4)         # borde de corte derecho (solapa)
    if k == 0:
        h.linea(X0, Y0, X0 + W, Y0, w=0.4)
    if inicio + alto >= L - 1e-9:
        h.linea(X0, Y0 + alto, X0 + W, Y0 + alto, w=0.4)
    # solapa de pegado rayada
    h.linea(X0 + circ, Y0, X0 + circ, Y0 + alto, w=0.25, c=GRIS, dash=(1.5, 1.0))
    t = -PESTANA - alto
    while t < PESTANA + alto + 3:
        h.linea_recortada(X0 + circ + t, Y0 + alto, X0 + circ + t + alto, Y0,
                          (X0 + circ, Y0, X0 + circ + PESTANA, Y0 + alto), w=0.15, c=GRIS)
        t += 3.0
    h.texto(X0 + circ + PESTANA / 2 + 1.2, Y0 + alto / 2, "PEGAR AQUÍ", size=3.6,
            ancla="middle", neg=True, rot=-90)

    # líneas de ángulo
    for a in (0, 90, 180, 270):
        x = x_de_ang(G, a)
        h.linea(x, Y0, x, Y0 + alto, w=0.25, c=AZUL, dash=(2.0, 1.0))
        h.texto(x, Y0 + 3.8, f"{a}°", size=3.4, c=AZUL, ancla="middle", neg=True)
        h.texto(x, Y0 + 6.8, etiquetas_angulo(a), size=2.2, c=AZUL, ancla="middle")

    # líneas de altura de cada soporte
    for nombre, tipo, z, giro in G["soportes"]:
        y = y_de_s(s_de_z(z))
        if not (Y0 - 4 <= y <= Y0 + alto + 4):
            continue
        h.linea(X0, y, X0 + circ, y, w=0.25, c=ROJO)
        etiqueta = f"{nombre} z={z}"
        w = ancho_txt(etiqueta, 2.2)
        cerca = [x_de_ang(G, a["ang"]) for a in G["agujeros"] if abs(a["z"] - z) < 6]
        izq = (X0 + 1, X0 + 1 + w)
        der = (X0 + circ - 1 - w, X0 + circ - 1)
        libre = lambda iv: all(not (iv[0] < xh + 3.5 and iv[1] > xh - 3.5) for xh in cerca)
        if libre(izq):
            h.texto(izq[0], y - 1.0, etiqueta, size=2.2, c=ROJO)
        else:
            h.texto(der[0], y - 1.0, etiqueta, size=2.2, c=ROJO)

    # taladros: cruz + círculo al diámetro real
    for a in G["agujeros"]:
        x = x_de_ang(G, a["ang"])
        y = y_de_s(s_de_z(a["z"]))
        r = a["d"] / 2
        if not (Y0 - r - 4 <= y <= Y0 + alto + r + 4):
            continue
        h.circulo(x, y, r, w=0.3)
        h.linea(x - r - 3, y, x + r + 3, y, w=0.2)
        h.linea(x, y - r - 3, x, y + r + 3, w=0.2)
        h.texto(x + r + 1.0, y - r - 0.3, a["id"], size=2.6, neg=True)
    h.clip_fin()

    # --- marcas de unión entre hojas ---
    if k < N - 1:
        y = Y0 + PASO
        h.linea(X0 - 6, y, X0 + W + 6, y, w=0.3, dash=(3.0, 1.5))
        h.texto(X0 + W + 8, y + 1.0, f"<-- une con hoja {k + 2}", size=3.0, neg=True)
    if k > 0:
        h.linea(X0 - 6, Y0, X0 + W + 6, Y0, w=0.3, dash=(3.0, 1.5))
        h.texto(X0 + W + 8, Y0 - 1.0, f"<-- recorta y une con hoja {k}", size=3.0, neg=True)
        h.texto(X0, Y0 - 1.5, f"Recorta por la línea y pon el borde sobre la de la hoja {k}",
                size=2.2)

    # --- cuadrado de 50 mm (en todas las hojas) ---
    cy = Y0 + 6
    h.rect(COL_X, cy, 50.0, 50.0, lw=0.3, tag="cuadrado")
    h.linea(COL_X, cy, COL_X + 50, cy + 50, w=0.1, c=GRIS)
    h.linea(COL_X, cy + 50, COL_X + 50, cy, w=0.1, c=GRIS)
    h.texto(COL_X + 25, cy + 26.0, "50 x 50 mm", size=3.0, ancla="middle", c=GRIS)
    y = cy + 54
    for r in _envolver(AVISO, 44):
        h.texto(COL_X, y, r, size=2.6, neg=True)
        y += 3.6

    # --- barra de escala vertical de 100 mm (en todas las hojas) ---
    h.linea(ESCALA_X, cy, ESCALA_X, cy + 100.0, w=0.5, tag="escala")
    for i in range(0, 101, 10):
        h.linea(ESCALA_X - (5 if i % 50 == 0 else 3), cy + i, ESCALA_X, cy + i, w=0.25)
    h.texto(ESCALA_X + 3.2, cy + 50, "Escala: 100 mm", size=3.0, ancla="middle", rot=-90)

    # --- leyenda (solo hoja 1) ---
    if k == 0:
        maquetar_leyenda(h, G, COL_X, 98.0)
    return h


# =====================================================================
#  Salida SVG
# =====================================================================
def _d(dash):
    return f' stroke-dasharray="{dash[0]} {dash[1]}"' if dash else ""


def a_svg(hoja, titulo, ancho=A4_W, alto=A4_H):
    o = ['<?xml version="1.0" encoding="UTF-8"?>',
         f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho:g}mm" height="{alto:g}mm" '
         f'viewBox="0 0 {ancho:g} {alto:g}">',
         f"<title>{escape(titulo)}</title>",
         f'<rect x="0" y="0" width="{ancho:g}" height="{alto:g}" fill="#ffffff"/>']
    n = 0
    for op in hoja.ops:
        t = op["t"]
        if t == "clip_ini":
            n += 1
            o.append(f'<clipPath id="c{n}"><rect x="{op["x"]:.3f}" y="{op["y"]:.3f}" '
                     f'width="{op["w"]:.3f}" height="{op["h"]:.3f}"/></clipPath>'
                     f'<g clip-path="url(#c{n})">')
        elif t == "clip_fin":
            o.append("</g>")
        elif t == "linea":
            idt = f' id="{op["tag"]}"' if op["tag"] else ""
            o.append(f'<line{idt} x1="{op["x1"]:.3f}" y1="{op["y1"]:.3f}" x2="{op["x2"]:.3f}" '
                     f'y2="{op["y2"]:.3f}" stroke="{op["c"]}" stroke-width="{op["w"]}"{_d(op["dash"])}/>')
        elif t == "circulo":
            o.append(f'<circle cx="{op["cx"]:.3f}" cy="{op["cy"]:.3f}" r="{op["r"]:.3f}" fill="none" '
                     f'stroke="{op["c"]}" stroke-width="{op["w"]}"{_d(op["dash"])}/>')
        elif t == "rect":
            idt = f' id="{op["tag"]}"' if op["tag"] else ""
            o.append(f'<rect{idt} x="{op["x"]:.3f}" y="{op["y"]:.3f}" width="{op["w"]:.3f}" '
                     f'height="{op["h"]:.3f}" fill="none" stroke="{op["c"]}" stroke-width="{op["lw"]}"/>')
        elif t == "texto":
            rot = f' transform="rotate(-90 {op["x"]:.3f} {op["y"]:.3f})"' if op["rot"] else ""
            neg = ' font-weight="bold"' if op["neg"] else ""
            o.append(f'<text x="{op["x"]:.3f}" y="{op["y"]:.3f}" font-family="Helvetica, Arial, sans-serif" '
                     f'font-size="{op["size"]}" fill="{op["c"]}"{neg}{rot}>{escape(op["s"])}</text>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


# =====================================================================
#  Salida PDF mínima (Helvetica, vectores, texto en WinAnsi)
# =====================================================================
K_BEZ = 0.5522847498


def _rgb(c):
    return " ".join(f"{int(c[i:i + 2], 16) / 255:.3f}" for i in (1, 3, 5))


def _pdf_str(s):
    b = s.encode("cp1252")  # falla si hay un carácter fuera de WinAnsi
    b = b.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
    return b"(" + b + b")"


def _contenido_pdf(hoja):
    S = 72.0 / 25.4
    out = [f"{S:.6f} 0 0 {-S:.6f} 0 {A4_H * S:.4f} cm".encode()]
    dash = lambda d: (f"[{d[0]} {d[1]}] 0 d" if d else "[] 0 d")
    for op in hoja.ops:
        t = op["t"]
        if t == "clip_ini":
            out.append(b"q")
            out.append(f"{op['x']:.3f} {op['y']:.3f} {op['w']:.3f} {op['h']:.3f} re W n".encode())
        elif t == "clip_fin":
            out.append(b"Q")
        elif t == "linea":
            out.append(f"{_rgb(op['c'])} RG {op['w']} w {dash(op['dash'])} "
                       f"{op['x1']:.3f} {op['y1']:.3f} m {op['x2']:.3f} {op['y2']:.3f} l S".encode())
        elif t == "rect":
            out.append(f"{_rgb(op['c'])} RG {op['lw']} w [] 0 d "
                       f"{op['x']:.3f} {op['y']:.3f} {op['w']:.3f} {op['h']:.3f} re S".encode())
        elif t == "circulo":
            cx, cy, r = op["cx"], op["cy"], op["r"]
            k = K_BEZ * r
            c = (f"{cx + r:.3f} {cy:.3f} m "
                 f"{cx + r:.3f} {cy + k:.3f} {cx + k:.3f} {cy + r:.3f} {cx:.3f} {cy + r:.3f} c "
                 f"{cx - k:.3f} {cy + r:.3f} {cx - r:.3f} {cy + k:.3f} {cx - r:.3f} {cy:.3f} c "
                 f"{cx - r:.3f} {cy - k:.3f} {cx - k:.3f} {cy - r:.3f} {cx:.3f} {cy - r:.3f} c "
                 f"{cx + k:.3f} {cy - r:.3f} {cx + r:.3f} {cy - k:.3f} {cx + r:.3f} {cy:.3f} c S")
            out.append(f"{_rgb(op['c'])} RG {op['w']} w {dash(op['dash'])} {c}".encode())
        elif t == "texto":
            m = "0 -1 -1 0" if op["rot"] else "1 0 0 -1"  # el CTM está invertido en y
            fuente = "/F2" if op["neg"] else "/F1"
            out.append(f"BT {fuente} {op['size']} Tf {_rgb(op['c'])} rg {m} "
                       f"{op['x']:.3f} {op['y']:.3f} Tm ".encode() + _pdf_str(op["s"]) + b" Tj ET")
    return b"\n".join(out)


def a_pdf(hojas):
    n = len(hojas)
    objs = {}
    objs[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{5 + 2 * i} 0 R" for i in range(n))
    objs[2] = f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode()
    objs[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    objs[4] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
    wpt, hpt = A4_W * 72 / 25.4, A4_H * 72 / 25.4
    for i, hoja in enumerate(hojas):
        po, co = 5 + 2 * i, 6 + 2 * i
        objs[po] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {wpt:.3f} {hpt:.3f}] "
                    f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {co} 0 R >>").encode()
        cont = _contenido_pdf(hoja)
        objs[co] = f"<< /Length {len(cont)} >>\nstream\n".encode() + cont + b"\nendstream"
    buf = bytearray(b"%PDF-1.4\n")
    offs = {}
    for num in sorted(objs):
        offs[num] = len(buf)
        buf += f"{num} 0 obj\n".encode() + objs[num] + b"\nendobj\n"
    xref = len(buf)
    buf += f"xref\n0 {len(objs) + 1}\n".encode() + b"0000000000 65535 f \n"
    for num in sorted(objs):
        buf += f"{offs[num]:010d} 00000 n \n".encode()
    buf += (f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n").encode()
    return bytes(buf)


# =====================================================================
#  Tira completa en un solo SVG (sin partir en hojas)
# =====================================================================
def tira_completa(G):
    """Una sola hoja SVG de tamaño tira (para ver o imprimir en plotter)."""
    N = G["n_hojas"]
    ancho = X0 + G["ancho"] + 10
    alto = Y0 + G["largo"] + 10
    h = Hoja()
    h.texto(X0, 12.0, TITULO + " - tira completa 1:1", size=4.0, neg=True)
    circ, W, L = G["circ"], G["ancho"], G["largo"]
    h.rect(X0, Y0, W, L, lw=0.4)
    h.linea(X0 + circ, Y0, X0 + circ, Y0 + L, c=GRIS, dash=(1.5, 1.0))
    h.texto(X0 + circ + PESTANA / 2 + 1.2, Y0 + L / 2, "PEGAR AQUÍ", size=3.6,
            ancla="middle", neg=True, rot=-90)
    for a in (0, 90, 180, 270):
        x = x_de_ang(G, a)
        h.linea(x, Y0, x, Y0 + L, c=AZUL, dash=(2.0, 1.0))
        h.texto(x, Y0 + 3.8, f"{a}°", size=3.4, c=AZUL, ancla="middle", neg=True)
        h.texto(x, Y0 + 6.8, etiquetas_angulo(a), size=2.2, c=AZUL, ancla="middle")
    for nombre, tipo, z, giro in G["soportes"]:
        y = Y0 + s_de_z(z)
        h.linea(X0, y, X0 + circ, y, c=ROJO)
        h.texto(X0 + circ + PESTANA + 2, y + 0.8, f"{nombre} z={z}", size=2.4, c=ROJO)
    for a in G["agujeros"]:
        x, y, r = x_de_ang(G, a["ang"]), Y0 + s_de_z(a["z"]), a["d"] / 2
        h.circulo(x, y, r, w=0.3)
        h.linea(x - r - 3, y, x + r + 3, y, w=0.2)
        h.linea(x, y - r - 3, x, y + r + 3, w=0.2)
        h.texto(x + r + 1.0, y - r - 0.3, a["id"], size=2.6, neg=True)
    return h, ancho, alto


# =====================================================================
#  Generación y autocomprobación
# =====================================================================
def generar(salida=SALIDA):
    salida = Path(salida)
    G = construir()
    hojas = [dibujar_hoja(G, k) for k in range(G["n_hojas"])]
    archivos = []
    tira, tw, th = tira_completa(G)
    f = salida / "plantilla_taladros.svg"
    f.write_text(a_svg(tira, TITULO + " - tira completa", tw, th), encoding="utf-8", newline="\n")
    archivos.append(f)
    for k, hoja in enumerate(hojas, start=1):
        f = salida / f"plantilla_taladros_p{k}.svg"
        f.write_text(a_svg(hoja, f"{TITULO} - hoja {k} de {len(hojas)}"),
                     encoding="utf-8", newline="\n")
        archivos.append(f)
    f = salida / "plantilla_taladros.pdf"
    f.write_bytes(a_pdf(hojas))
    archivos.append(f)
    return G, hojas, archivos


def verificar(G, hojas, archivos):
    """Comprobaciones con assert; lanza AssertionError si algo no cuadra."""
    import xml.etree.ElementTree as ET
    ns = "{http://www.w3.org/2000/svg}"

    # circunferencia = pi * tubo_d
    assert abs(G["circ"] - math.pi * G["tubo_d"]) < 0.1, "circunferencia incorrecta"
    assert G["tubo_d"] == 30.0, "el tubo ya no es de 30 mm: revisa MONTAJE.md"

    # alturas idénticas a MONTAJE.md
    montaje = (RAIZ / "MONTAJE.md").read_text(encoding="utf-8")
    for nombre, tipo, z, giro in G["soportes"]:
        if z != 0:
            assert f"−{abs(z)} mm" in montaje, f"{nombre}: z={z} no está en MONTAJE.md"

    # taladros dentro de la tira, fuera de la solapa pegada y dentro de los manguitos/huecos
    for a in G["agujeros"]:
        x = x_de_ang(G, a["ang"])
        r = a["d"] / 2
        assert X0 + PESTANA < x - r and x + r < X0 + G["circ"], f"{a['id']} fuera de la tira"
        s = s_de_z(a["z"])
        assert r < s < G["largo"] - r, f"{a['id']} fuera por arriba/abajo"
    mh = G["p"]["manguito_h"]
    zf = G["z_feed"]
    assert -30 + mh / 2 < zf - FEED_D / 2 and zf + FEED_D / 2 < 0 - mh / 2, \
        "los agujeros de alimentación chocan con un manguito"

    # ángulos de los tornillos de cada soporte
    esperado_rel = {"cruceta_vhf": 45, "uhf": 45, "barra_vhf": 90}
    por_soporte = {a["soporte"]: a for a in G["agujeros"] if a["soporte"]}
    assert len(por_soporte) == len(G["soportes"]), "falta algún soporte"
    for nombre, tipo, z, giro in G["soportes"]:
        a = por_soporte[nombre]
        assert a["z"] == z
        assert (a["ang"] - giro) % 360 == esperado_rel[tipo], f"{nombre}: ángulo de tornillo"
    feeds = sorted(a["ang"] for a in G["agujeros"] if a["tipo"] == "alimentacion")
    assert feeds == [0, 90, 180, 270]

    # número de hojas
    esperado = max(1, math.ceil((G["largo"] - VENTANA) / PASO) + 1)
    assert G["n_hojas"] == esperado == len(hojas)
    assert (G["n_hojas"] - 1) * PASO + VENTANA >= G["largo"] > (G["n_hojas"] - 2) * PASO + VENTANA
    assert abs(G["largo"] - (MARGEN_Z + 650 + MARGEN_Z)) < 1e-9

    # ficheros: SVG por hoja (escala y cuadrado exactos) y PDF
    nombres = {f.name for f in archivos}
    assert "plantilla_taladros.svg" in nombres and "plantilla_taladros.pdf" in nombres
    for k in range(1, G["n_hojas"] + 1):
        f = next(f for f in archivos if f.name == f"plantilla_taladros_p{k}.svg")
        raiz = ET.parse(f).getroot()
        assert raiz.get("width") == "210mm" and raiz.get("height") == "297mm"
        assert raiz.get("viewBox") == "0 0 210 297"
        esc = next(e for e in raiz.iter(ns + "line") if e.get("id") == "escala")
        largo = math.hypot(float(esc.get("x2")) - float(esc.get("x1")),
                           float(esc.get("y2")) - float(esc.get("y1")))
        assert abs(largo - 100.0) < 1e-6, f"hoja {k}: la escala no mide 100"
        cua = next(e for e in raiz.iter(ns + "rect") if e.get("id") == "cuadrado")
        assert float(cua.get("width")) == 50.0 and float(cua.get("height")) == 50.0
        textos = "".join("".join(e.itertext()) for e in raiz.iter(ns + "text"))
        assert "Imprimir al 100 %" in textos and "BricoHams" in textos
        for e in raiz.iter():  # todo dentro de márgenes de 10 mm (salvo el fondo blanco)
            if e.tag in (ns + "line",):
                for c in ("x1", "x2"):
                    assert 0 <= float(e.get(c)) <= A4_W
    pdf = next(f for f in archivos if f.suffix == ".pdf").read_bytes()
    assert pdf.startswith(b"%PDF-1.4") and pdf.rstrip().endswith(b"%%EOF")
    assert len(re.findall(rb"/Type /Page /", pdf)) == G["n_hojas"]
    assert f"/Count {G['n_hojas']}".encode() in pdf
    return True


def main():
    G, hojas, archivos = generar()
    verificar(G, hojas, archivos)
    print(f"Circunferencia {G['circ']:.2f} mm, tira {G['largo']:.0f} mm, {G['n_hojas']} hojas A4.")
    for a in G["agujeros"]:
        print(f"  {a['id']:>3}  z {a['z']:7.1f}  {a['ang']:5.1f}°  Ø{a['d']}  {a['nombre']}")
    for f in archivos:
        print("  escrito", f.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
