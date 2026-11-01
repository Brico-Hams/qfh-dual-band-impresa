"""Autocomprobación de la plantilla de taladros.

Ejecutar desde la raíz del repositorio:  python test_plantilla.py
"""
import tempfile

import plantilla_taladros as pt


def test_plantilla():
    with tempfile.TemporaryDirectory() as tmp:
        G, hojas, archivos = pt.generar(tmp)
        assert pt.verificar(G, hojas, archivos)


if __name__ == "__main__":
    test_plantilla()
    print("OK: plantilla de taladros verificada")
