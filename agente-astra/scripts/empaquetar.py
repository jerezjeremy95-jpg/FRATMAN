#!/usr/bin/env python3
"""Empaqueta el agente para instalarlo.

Genera en dist/:
- <skill>.zip            una por skill, para subir en Claude.ai (Personalizar → Skills).
                         Dentro del zip, la carpeta de la skill es la entrada de primer nivel.
- agente-astra-plugin.zip el plugin completo, para Cowork (Agregar → Subir plugin).

Con --skill-files <carpeta>, además deja copias .skill en esa carpeta. Son el mismo zip,
pero en las apps de Claude se pueden guardar con un clic.

Los zip son reproducibles (fecha fija y orden fijo): si nada cambió, el archivo sale igual.

Uso:
    python3 scripts/empaquetar.py [--skill-files RUTA]
"""
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PLUGIN = RAIZ / "plugin"
DIST = RAIZ / "dist"
FECHA_FIJA = (2026, 1, 1, 0, 0, 0)
EXCLUIR = {"__pycache__", ".DS_Store"}


def archivos(carpeta: Path):
    for ruta in sorted(carpeta.rglob("*")):
        if ruta.is_file() and not any(p in EXCLUIR for p in ruta.parts) and ruta.suffix != ".pyc":
            yield ruta


def zip_reproducible(destino: Path, carpeta: Path, nombre_raiz: str) -> None:
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for ruta in archivos(carpeta):
            arc = f"{nombre_raiz}/{ruta.relative_to(carpeta).as_posix()}"
            info = zipfile.ZipInfo(arc, date_time=FECHA_FIJA)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if ruta.suffix == ".py" else 0o644) << 16
            z.writestr(info, ruta.read_bytes())


def main() -> int:
    for paso in ("sincronizar.py", "validar.py"):
        r = subprocess.run([sys.executable, str(RAIZ / "scripts" / paso)], capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode != 0:
            print(f"Se detiene: {paso} falló.")
            return 1
    DIST.mkdir(exist_ok=True)
    skill_files = None
    if "--skill-files" in sys.argv:
        skill_files = Path(sys.argv[sys.argv.index("--skill-files") + 1])
        skill_files.mkdir(parents=True, exist_ok=True)
    for carpeta in sorted((PLUGIN / "skills").iterdir()):
        destino = DIST / f"{carpeta.name}.zip"
        zip_reproducible(destino, carpeta, carpeta.name)
        print(f"dist/{destino.name}")
        if skill_files:
            shutil.copy2(destino, skill_files / f"{carpeta.name}.skill")
    destino = DIST / "agente-astra-plugin.zip"
    zip_reproducible(destino, PLUGIN, "agente-astra")
    print(f"dist/{destino.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
