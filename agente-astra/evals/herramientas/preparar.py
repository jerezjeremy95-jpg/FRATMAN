#!/usr/bin/env python3
"""Prepara una iteración de pruebas: carpetas por caso y configuración, metadatos
y el texto exacto de la instrucción para cada subagente ejecutor.

Uso:
    python3 preparar.py <iteracion> <skill> <config> [<config> ...] [--casos 201,203]

Ejemplo:
    python3 preparar.py 1 guardian-marca opus_con_skill sonnet_con_skill sonnet_sin_skill

Cada config tiene la forma <modelo>_con_skill o <modelo>_sin_skill. Con --casos solo se
preparan esos casos (útil para repetir en una iteración nueva solo lo que falló).
Escribe en evals/workspace/iteration-<n>/<skill>/eval-<id>-<nombre>/<config>/run-1/
y deja la instrucción del ejecutor en instruccion.txt dentro de cada run.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]  # agente-astra/
EVALS = RAIZ / "evals"
FECHA = "2026-10-14"

RESTRICCIONES = (
    "Restricciones de esta prueba: no uses conectores ni herramientas externas "
    "(Google Drive, Gmail, Calendar, Canva, Notion, HubSpot, etc.), no busques en la web "
    "y no invoques skills con la herramienta Skill. Trabaja solo con los archivos indicados. "
    f"La fecha de hoy es {FECHA}."
)


def instruccion(caso: dict, skill: str, config: str, run_dir: Path) -> str:
    core = RAIZ / caso["core_brand"]
    salida = run_dir / "outputs" / "respuesta.md"
    if config.endswith("_con_skill"):
        cabeza = (
            "Trabajas en el equipo de contenido de Astra, una agencia de Santiago (República Dominicana), "
            "y vas a usar una skill.\n"
            f"- Skill: lee primero {RAIZ / 'plugin' / 'skills' / skill / 'SKILL.md'} y síguela. "
            "Sus referencias están en la carpeta references/ de esa skill: léelas cuando la skill lo indique.\n"
        )
    else:
        cabeza = (
            "Trabajas en el equipo de contenido de Astra, una agencia de Santiago (República Dominicana).\n"
        )
    return (
        cabeza
        + f"- Core Brand de la marca: {core} (en el día a día vive en Google Drive; aquí usa este archivo como si fuera esa carpeta).\n"
        + "- Pedido del usuario:\n<<<\n" + caso["prompt"] + "\n>>>\n"
        + "- " + RESTRICCIONES + "\n"
        + f"- Guarda tu respuesta final completa, exactamente como se la entregarías al usuario, en: {salida}\n"
        + "- Cuando termines, responde solo: listo"
    )


def main() -> None:
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    args = sys.argv[1:]
    casos = None
    if "--casos" in args:
        i = args.index("--casos")
        casos = {int(x) for x in args[i + 1].split(",")}
        del args[i:i + 2]
    iteracion, skill, configs = args[0], args[1], args[2:]
    datos = json.loads((EVALS / f"{skill}.evals.json").read_text())
    base = EVALS / "workspace" / f"iteration-{iteracion}" / skill
    for caso in datos["evals"]:
        if casos and caso["id"] not in casos:
            continue
        eval_dir = base / f"eval-{caso['id']}-{caso['nombre']}"
        meta = {
            "eval_id": caso["id"],
            "eval_name": caso["nombre"],
            "prompt": caso["prompt"],
            "assertions": caso.get("expectations", []),
        }
        eval_dir.mkdir(parents=True, exist_ok=True)
        (eval_dir / "eval_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        for config in configs:
            run_dir = eval_dir / config / "run-1"
            (run_dir / "outputs").mkdir(parents=True, exist_ok=True)
            # El visor busca eval_metadata.json en la carpeta del run o en su padre.
            (run_dir / "eval_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
            (run_dir / "instruccion.txt").write_text(instruccion(caso, skill, config, run_dir))
            print(run_dir)


if __name__ == "__main__":
    main()
