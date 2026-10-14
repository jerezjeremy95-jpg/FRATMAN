#!/usr/bin/env python3
"""Copia las referencias compartidas (compartido/) a cada skill que las usa.

Cada skill tiene que poder instalarse sola en Claude.ai, así que lleva su propia copia
de las referencias. La fuente única es compartido/: se edita ahí y se sincroniza.

Uso:
    python3 scripts/sincronizar.py          copia
    python3 scripts/sincronizar.py --check  solo verifica (sale con código 1 si hay diferencias)
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
COMP = RAIZ / "compartido"

# archivo compartido -> skills que lo llevan (y en qué subcarpeta)
MAPA = {
    "principios-astra.md": (["agente-astra", "guardian-marca", "reciclador-contenido", "guionista-reels"], "references"),
    "claims-riesgo.md": (["guardian-marca", "reciclador-contenido", "guionista-reels"], "references"),
    "marco-rd.md": (["guardian-marca"], "references"),
    "formatos-canal.md": (["reciclador-contenido", "guionista-reels"], "references"),
    "temporadas.md": (["guionista-reels"], "references"),
    "enrutamiento-modelos.md": (["agente-astra"], "references"),
    "verificar_copy.py": (["reciclador-contenido", "guionista-reels", "guardian-marca"], "scripts"),
}


def main() -> int:
    check = "--check" in sys.argv
    diferencias = []
    for archivo, (skills, sub) in MAPA.items():
        origen = COMP / archivo
        if not origen.exists():
            diferencias.append(f"falta la fuente compartido/{archivo}")
            continue
        for skill in skills:
            destino = RAIZ / "plugin" / "skills" / skill / sub / archivo
            if destino.exists() and destino.read_bytes() == origen.read_bytes():
                continue
            if check:
                diferencias.append(f"desactualizado: plugin/skills/{skill}/{sub}/{archivo}")
            else:
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(origen, destino)
                print(f"copiado → plugin/skills/{skill}/{sub}/{archivo}")
    if diferencias:
        print("\n".join(diferencias))
        return 1 if check else 0
    print("Referencias compartidas al día.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
