#!/usr/bin/env python3
"""Ajuste aplicado tras la investigación legal (2026-10-14): la Ley 42-01, art. 123, exige la
leyenda "El consumo de alcohol perjudica la salud" en toda publicidad de alcohol. La marca
ficticia Monteluz la incorpora a su leyenda, y los casos y expectativas se alinean."""
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
VIEJA = "Disfruta con responsabilidad. Prohibida su venta a menores de 18 años."
NUEVA = "Disfruta con responsabilidad. El consumo de alcohol perjudica la salud. Prohibida su venta a menores de 18 años."

cb = E / "marcas-ficticias" / "monteluz.md"
t = cb.read_text()
if NUEVA not in t:
    cb.write_text(t.replace(VIEJA, NUEVA))

for archivo in ("guardian-marca.evals.json", "reciclador-contenido.evals.json", "guionista-reels.evals.json"):
    p = E / archivo
    t = p.read_text()
    if NUEVA not in t:
        t = t.replace(VIEJA, NUEVA)
    p.write_text(t)
    d = json.loads(t)  # valida
print("leyenda actualizada")
