#!/usr/bin/env python3
"""Escribe juicio/instruccion_juez.txt para los casos indicados.
Uso: python3 instruir_juez.py <dir_skill_iteracion> <plantilla> <id> [<id> ...]"""
import sys
from pathlib import Path
base, plantilla, ids = Path(sys.argv[1]), Path(sys.argv[2]), set(sys.argv[3:])
for j in sorted(base.glob("eval-*/juicio")):
    if j.parent.name.split("-")[1] in ids:
        t = plantilla.read_text().replace("{PAQUETE}", str((j / "paquete.md").resolve())).replace("{SALIDA}", str((j / "juicio.json").resolve()))
        (j / "instruccion_juez.txt").write_text(t)
        print((j / "instruccion_juez.txt").resolve())
