#!/usr/bin/env python3
"""Escribe timing.json en cada run a partir de un TSV con: run_dir, tokens, duración en ms.

Los tokens y el tiempo de cada subagente solo llegan en el aviso de fin de tarea, así que
se anotan en el TSV a medida que llegan y este script los reparte.

Uso:  python3 registrar_tiempos.py tiempos.tsv
"""
import json
import sys
from pathlib import Path

for linea in Path(sys.argv[1]).read_text().splitlines():
    if not linea.strip() or linea.startswith("#"):
        continue
    run_dir, tokens, ms = linea.split("\t")
    datos = {"total_tokens": int(tokens), "duration_ms": int(ms), "total_duration_seconds": round(int(ms) / 1000, 1)}
    (Path(run_dir) / "timing.json").write_text(json.dumps(datos, indent=2))
    print(run_dir, datos)
