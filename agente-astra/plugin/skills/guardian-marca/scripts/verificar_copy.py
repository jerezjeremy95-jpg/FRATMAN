#!/usr/bin/env python3
"""Verificación mecánica de un copy o de un paquete del agente de Astra.

No juzga el contenido: cuenta y compara. Sirve para que el subagente Haiku (o cualquier
persona) revise en segundos lo que una IA cuenta mal: caracteres, hashtags, emojis,
tiempos del Reel, palabras prohibidas, leyendas obligatorias, datos por confirmar y el
registro del Guardián.

Uso:
    python3 verificar_copy.py ARCHIVO.md [--prohibidas "detox,dieta,barato"]
                                         [--leyenda "Disfruta con responsabilidad."]
                                         [--json]

Si no hay archivo, lee de la entrada estándar.
"""
import argparse
import json
import re
import sys
import unicodedata

LIMITE_LINKEDIN = 3000          # caracteres por publicación (ver formatos-canal.md)
LIMITE_CAPTION_IG = 2200        # caracteres por caption de Instagram
CORTE_VER_MAS_LINKEDIN = 210    # aprox. caracteres visibles antes de "ver más"

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002B50\U00002B06\U00002934\U00002935]"
)
HASHTAG_RE = re.compile(r"(?<![\w&])#[\wáéíóúñü]+", re.IGNORECASE)
CONFIRMAR_RE = re.compile(r"\[confirmar[^\]]*\]", re.IGNORECASE)
CIFRA_RE = re.compile(r"(RD\$\s?[\d.,]+|US\$\s?[\d.,]+|\$\s?[\d.,]+|\d+(?:[.,]\d+)?\s?%|\b\d{1,3}(?:[.,]\d{3})+\b|\b\d+\b)")
TIEMPO_RE = re.compile(r"^\|\s*(\d+(?:[.,]\d+)?)\s*(?:s|seg)?\s*[–—-]\s*(\d+(?:[.,]\d+)?)\s*(?:s|seg)?\b", re.IGNORECASE)
REGISTRO_RE = re.compile(r"REGISTRO-GUARDIAN\s*:?\s*(\{.*\})")
DURACION_RE = re.compile(r"(\d+)\s*(?:s|seg|segundos)\b", re.IGNORECASE)


def sin_acentos(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def secciones(texto: str) -> dict:
    """Parte el texto por encabezados markdown (##, ###)."""
    partes, actual, buffer = {}, "(inicio)", []
    for linea in texto.splitlines():
        m = re.match(r"^#{2,4}\s+(.*)", linea)
        if m:
            partes[actual] = "\n".join(buffer).strip()
            actual, buffer = m.group(1).strip(), []
        else:
            buffer.append(linea)
    partes[actual] = "\n".join(buffer).strip()
    return {k: v for k, v in partes.items() if v}


def buscar(partes: dict, *claves: str):
    for nombre, cuerpo in partes.items():
        n = sin_acentos(nombre)
        if any(c in n for c in claves):
            return nombre, cuerpo
    return None, None


def tiempos_reel(cuerpo: str, titulo: str):
    filas = []
    for linea in cuerpo.splitlines():
        m = TIEMPO_RE.match(linea.strip())
        if m:
            filas.append((float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))))
    if not filas:
        return {"filas": 0}
    huecos = [f"{a[1]:g}→{b[0]:g}" for a, b in zip(filas, filas[1:]) if abs(b[0] - a[1]) > 0.01]
    declarada = None
    m = DURACION_RE.search(titulo or "")
    if m:
        declarada = int(m.group(1))
    total = filas[-1][1] - filas[0][0]
    return {
        "filas": len(filas),
        "inicio": filas[0][0],
        "fin": filas[-1][1],
        "duracion_tabla": total,
        "duracion_declarada": declarada,
        "huecos_o_solapes": huecos,
        "cuadra": (not huecos) and filas[0][0] == 0 and (declarada is None or abs(total - declarada) <= 2),
    }


def cifras(texto: str) -> list:
    """Cifras y precios a contrastar con la fuente. Ignora fechas, rangos de tiempo del
    guion, duraciones, el registro JSON y los dígitos sueltos."""
    limpio = REGISTRO_RE.sub(" ", texto)
    limpio = re.sub(r"\d{4}-\d{2}-\d{2}", " ", limpio)
    limpio = re.sub(r"\d+(?:[.,]\d+)?\s*(?:s|seg)?\s*[–—-]\s*\d+(?:[.,]\d+)?\s*(?:s|seg|segundos)\b", " ", limpio, flags=re.IGNORECASE)
    limpio = re.sub(r"\b\d+\s*(?:s|seg|segundos)\b", " ", limpio, flags=re.IGNORECASE)
    limpio = re.sub(r"\[confirmar[^\]]*\]", " ", limpio, flags=re.IGNORECASE)
    return sorted(set(m.strip() for m in CIFRA_RE.findall(limpio) if not re.fullmatch(r"\d", m.strip())))


def verificar(texto: str, prohibidas: list, leyenda: str | None) -> dict:
    partes = secciones(texto)
    norm = sin_acentos(texto)
    reporte = {
        "caracteres_total": len(texto),
        "hashtags_total": len(HASHTAG_RE.findall(texto)),
        "emojis_total": len(EMOJI_RE.findall(texto)),
        "por_confirmar": CONFIRMAR_RE.findall(texto),
        "cifras_y_precios": cifras(texto),
        "prohibidas_encontradas": [],
        "leyenda": None,
        "linkedin": None,
        "reel": None,
        "registro_guardian": None,
        "alertas": [],
    }
    for palabra in prohibidas:
        p = sin_acentos(palabra.strip())
        if p and re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", norm):
            reporte["prohibidas_encontradas"].append(palabra.strip())
    if reporte["prohibidas_encontradas"]:
        reporte["alertas"].append("Aparecen palabras prohibidas: " + ", ".join(reporte["prohibidas_encontradas"]))

    if leyenda:
        reporte["leyenda"] = {"texto": leyenda, "apariciones": norm.count(sin_acentos(leyenda))}
        if reporte["leyenda"]["apariciones"] == 0:
            reporte["alertas"].append("Falta la leyenda obligatoria.")

    titulo, cuerpo = buscar(partes, "linkedin")
    if cuerpo:
        primeras = " ".join(cuerpo.splitlines()[:2])
        reporte["linkedin"] = {"seccion": titulo, "caracteres": len(cuerpo),
                               "caracteres_primeras_2_lineas": len(primeras), "hashtags": len(HASHTAG_RE.findall(cuerpo))}
        if len(cuerpo) > LIMITE_LINKEDIN:
            reporte["alertas"].append(f"El post de LinkedIn pasa de {LIMITE_LINKEDIN} caracteres.")
        if len(primeras) > CORTE_VER_MAS_LINKEDIN:
            reporte["alertas"].append("Las 2 primeras líneas de LinkedIn quizá se corten antes del 'ver más'.")

    titulo, cuerpo = buscar(partes, "reel", "guion")
    if cuerpo:
        reporte["reel"] = tiempos_reel(cuerpo, titulo)
        if reporte["reel"].get("filas") and not reporte["reel"]["cuadra"]:
            reporte["alertas"].append("Los tiempos del Reel no cuadran con la duración (revisa huecos, solapes o el total).")

    m = REGISTRO_RE.findall(texto)
    if m:
        try:
            json.loads(m[-1])
            reporte["registro_guardian"] = "válido"
        except json.JSONDecodeError as e:
            reporte["registro_guardian"] = f"inválido: {e}"
            reporte["alertas"].append("La línea REGISTRO-GUARDIAN no es JSON válido.")
    else:
        reporte["registro_guardian"] = "no hay"

    for nombre, cuerpo in partes.items():
        if "caption" in sin_acentos(nombre) and len(cuerpo) > LIMITE_CAPTION_IG:
            reporte["alertas"].append(f"La sección '{nombre}' pasa de {LIMITE_CAPTION_IG} caracteres.")
    if reporte["por_confirmar"]:
        reporte["alertas"].append(f"Hay {len(reporte['por_confirmar'])} datos por confirmar antes de enviar.")
    return reporte


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivo", nargs="?")
    ap.add_argument("--prohibidas", default="", help="Lista separada por comas")
    ap.add_argument("--leyenda", default=None)
    ap.add_argument("--json", action="store_true", help="Salida en JSON")
    args = ap.parse_args()
    texto = open(args.archivo, encoding="utf-8").read() if args.archivo else sys.stdin.read()
    rep = verificar(texto, [p for p in args.prohibidas.split(",") if p.strip()], args.leyenda)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return
    print("Verificación mecánica")
    print(f"- Caracteres: {rep['caracteres_total']} · hashtags: {rep['hashtags_total']} · emojis: {rep['emojis_total']}")
    if rep["linkedin"]:
        li = rep["linkedin"]
        print(f"- LinkedIn: {li['caracteres']} caracteres, {li['hashtags']} hashtags, 2 primeras líneas: {li['caracteres_primeras_2_lineas']}")
    if rep["reel"] and rep["reel"].get("filas"):
        r = rep["reel"]
        print(f"- Reel: {r['filas']} tomas, de {r['inicio']:g} a {r['fin']:g} s (declarada: {r['duracion_declarada']}) · cuadra: {'sí' if r['cuadra'] else 'NO'}")
    print(f"- Registro del Guardián: {rep['registro_guardian']}")
    if rep["cifras_y_precios"]:
        print("- Cifras y precios a verificar contra la fuente: " + ", ".join(rep["cifras_y_precios"]))
    print("- Alertas:" if rep["alertas"] else "- Sin alertas.")
    for a in rep["alertas"]:
        print(f"  · {a}")


if __name__ == "__main__":
    main()
