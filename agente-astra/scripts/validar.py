#!/usr/bin/env python3
"""Valida el agente antes de empaquetar o subir cambios.

Revisa:
- Skills: frontmatter compatible con Claude.ai (solo claves permitidas), nombre igual a la
  carpeta, límites de largo y que existan los archivos que el SKILL.md menciona.
- Subagentes y comandos: frontmatter con los campos y modelos esperados.
- plugin.json y marketplace.json: JSON válido y rutas que existen.
- Referencias compartidas sincronizadas (scripts/sincronizar.py --check).
- Repositorio público: que no se cuelen correos, teléfonos, links de Drive o Docs,
  IDs de diseños de Canva ni otros datos internos.

Uso:  python3 scripts/validar.py      (sale con código 1 si hay errores)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]          # agente-astra/
REPO = RAIZ.parent
PLUGIN = RAIZ / "plugin"
CLAVES_CLAUDE_AI = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MODELOS = {"haiku", "sonnet", "opus", "fable", "inherit"}
ESFUERZOS = {"low", "medium", "high", "xhigh", "max"}

errores, avisos = [], []


def frontmatter(ruta: Path) -> dict:
    texto = ruta.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.DOTALL)
    if not m:
        errores.append(f"{ruta.relative_to(REPO)}: sin frontmatter")
        return {}
    datos = {}
    for linea in m.group(1).splitlines():
        if ":" in linea and not linea.startswith(" "):
            k, v = linea.split(":", 1)
            datos[k.strip()] = v.strip().strip('"')
    return datos


def validar_skills() -> None:
    for carpeta in sorted((PLUGIN / "skills").iterdir()):
        skill = carpeta / "SKILL.md"
        rel = skill.relative_to(REPO)
        if not skill.exists():
            errores.append(f"{carpeta.relative_to(REPO)}: falta SKILL.md")
            continue
        fm = frontmatter(skill)
        extra = set(fm) - CLAVES_CLAUDE_AI
        if extra:
            errores.append(f"{rel}: claves no aceptadas por Claude.ai: {', '.join(sorted(extra))}")
        nombre = fm.get("name", "")
        if nombre != carpeta.name:
            errores.append(f"{rel}: name '{nombre}' no coincide con la carpeta '{carpeta.name}'")
        if not re.fullmatch(r"[a-z0-9-]{1,64}", nombre):
            errores.append(f"{rel}: name inválido (minúsculas, números y guiones; máx. 64)")
        desc = fm.get("description", "")
        if not desc:
            errores.append(f"{rel}: falta description")
        elif len(desc) > 1024:
            errores.append(f"{rel}: description de {len(desc)} caracteres (máx. 1024)")
        texto = skill.read_text(encoding="utf-8")
        if texto.count("\n") > 500:
            avisos.append(f"{rel}: más de 500 líneas")
        for ref in sorted(set(re.findall(r"`((?:references|scripts)/[\w./-]+)`", texto))):
            if not (carpeta / ref).exists():
                errores.append(f"{rel}: menciona {ref}, que no existe")


def validar_agentes_y_comandos() -> None:
    for ruta in sorted((PLUGIN / "agents").glob("*.md")):
        fm = frontmatter(ruta)
        rel = ruta.relative_to(REPO)
        for clave in ("name", "description", "model"):
            if not fm.get(clave):
                errores.append(f"{rel}: falta {clave}")
        if fm.get("name") and fm["name"] != ruta.stem:
            errores.append(f"{rel}: name no coincide con el archivo")
        if fm.get("model") and fm["model"] not in MODELOS:
            errores.append(f"{rel}: model '{fm['model']}' no reconocido")
        if fm.get("effort") and fm["effort"] not in ESFUERZOS:
            errores.append(f"{rel}: effort '{fm['effort']}' no reconocido")
    for ruta in sorted((PLUGIN / "commands").glob("*.md")):
        fm = frontmatter(ruta)
        rel = ruta.relative_to(REPO)
        if not fm.get("description"):
            errores.append(f"{rel}: falta description")
        if fm.get("model") and fm["model"] not in MODELOS:
            errores.append(f"{rel}: model '{fm['model']}' no reconocido")
        if (PLUGIN / "skills" / ruta.stem).exists():
            errores.append(f"{rel}: choca con una skill del mismo nombre (gana la skill)")
        if "$ARGUMENTS" not in ruta.read_text(encoding="utf-8"):
            avisos.append(f"{rel}: no usa $ARGUMENTS")


def validar_manifiestos() -> None:
    try:
        plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())
        if not re.fullmatch(r"[a-z0-9-]+", plugin.get("name", "")):
            errores.append("plugin.json: name inválido")
    except (OSError, json.JSONDecodeError) as e:
        errores.append(f"plugin.json: {e}")
    try:
        market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
        for p in market.get("plugins", []):
            if not (REPO / p["source"]).resolve().exists():
                errores.append(f"marketplace.json: la ruta {p['source']} no existe")
    except (OSError, json.JSONDecodeError, KeyError) as e:
        errores.append(f"marketplace.json: {e}")
    if (PLUGIN / "bin").exists():
        errores.append("plugin/bin/ bloquea la instalación en Claude.ai y Cowork")


PATRONES_SENSIBLES = {
    "correo": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "teléfono": re.compile(r"\b(?:\+?1[\s-]?)?\(?8[024]9\)?[\s-]?\d{3}[\s-]?\d{4}\b"),
    "link de Drive o Docs": re.compile(r"(?:drive|docs)\.google\.com/\S+"),
    "link de diseño de Canva": re.compile(r"canva\.com/design/\S+"),
    "ID de diseño de Canva": re.compile(r"\bDA[A-Za-z0-9_-]{9}\b"),
}
PERMITIDOS = {"noreply@anthropic.com"}


def validar_contenido_publico() -> None:
    try:
        archivos = subprocess.run(["git", "ls-files", "--others", "--cached", "--exclude-standard", "agente-astra", ".claude-plugin"],
                                  cwd=REPO, capture_output=True, text=True, check=True).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        archivos = [str(p.relative_to(REPO)) for p in RAIZ.rglob("*") if p.is_file()]
    for rel in archivos:
        ruta = REPO / rel
        if ruta.suffix not in {".md", ".json", ".py", ".txt", ".html"} or "workspace" in ruta.parts:
            continue
        texto = ruta.read_text(encoding="utf-8", errors="ignore")
        for nombre, patron in PATRONES_SENSIBLES.items():
            for m in patron.findall(texto):
                if m in PERMITIDOS or (nombre == "correo" and m.endswith("@example.com")):
                    continue
                errores.append(f"{rel}: posible {nombre} en un repo público: {m[:60]}")


def main() -> int:
    validar_skills()
    validar_agentes_y_comandos()
    validar_manifiestos()
    sync = subprocess.run([sys.executable, str(RAIZ / "scripts" / "sincronizar.py"), "--check"], capture_output=True, text=True)
    if sync.returncode != 0:
        errores.append("referencias compartidas desactualizadas:\n  " + sync.stdout.strip().replace("\n", "\n  "))
    validar_contenido_publico()
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"ERROR: {e}")
    print("Validación OK." if not errores else f"{len(errores)} error(es).")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
