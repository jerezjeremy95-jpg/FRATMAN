#!/usr/bin/env python3
"""Calificación de las pruebas del agente.

Subcomandos:
    paquetes   <dir_skill_iteracion>   Arma, por caso, un paquete anónimo (A, B, C…) para el juez.
    consolidar <dir_skill_iteracion>   Une el juicio del juez con los chequeos automáticos y
                                       escribe grading.json en cada run.
    resumen    <dir_skill_iteracion>   Métricas por configuración (modelo y con o sin skill).

<dir_skill_iteracion> es, por ejemplo, evals/workspace/iteration-1/guardian-marca.

Los chequeos automáticos del Guardián (registro JSON, veredicto, frases riesgosas que
sobreviven en la versión corregida) se hacen aquí con código. La detección de cada riesgo
sembrado, que admite paráfrasis y agrupaciones, la decide un juez LLM a ciegas.
"""
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]  # agente-astra/
EVALS = RAIZ / "evals"
SEV = {"ninguna": 0, "baja": 1, "media": 2, "alta": 3}
LETRAS = "ABCDEFGH"


# ---------- utilidades ----------

def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def cargar_casos(skill: str) -> dict:
    datos = json.loads((EVALS / f"{skill}.evals.json").read_text())
    return {c["id"]: c for c in datos["evals"]}


def runs_de(eval_dir: Path) -> dict:
    """config -> run_dir, solo los que tienen respuesta."""
    out = {}
    for config_dir in sorted(p for p in eval_dir.iterdir() if p.is_dir() and p.name != "juicio"):
        run = config_dir / "run-1"
        if (run / "outputs" / "respuesta.md").exists():
            out[config_dir.name] = run
    return out


def eval_id(eval_dir: Path) -> int:
    return json.loads((eval_dir / "eval_metadata.json").read_text())["eval_id"]


# ---------- chequeos automáticos ----------

REGISTRO_RE = re.compile(r"REGISTRO-GUARDIAN\s*:?\s*(\{.*\})")


def leer_registro(texto: str):
    """Devuelve (dict | None, error | None) del último registro en el texto."""
    encontrados = REGISTRO_RE.findall(texto)
    if not encontrados:
        return None, "no hay línea REGISTRO-GUARDIAN"
    bruto = encontrados[-1].strip()
    try:
        return json.loads(bruto), None
    except json.JSONDecodeError as e:
        return None, f"JSON inválido: {e}"


def veredicto_de_texto(texto: str):
    """Veredicto declarado en el texto, para salidas sin registro."""
    m = re.search(r"veredicto[^\n]{0,40}", texto, re.IGNORECASE)
    zona = normalizar(m.group(0)) if m else ""
    for marca, valor in (("🔴", "rojo"), ("🟡", "amarillo"), ("🟢", "verde")):
        if marca in (m.group(0) if m else ""):
            return valor
    for clave, valor in (("no publicar", "rojo"), ("ajustar", "amarillo"), ("listo", "verde")):
        if clave in zona:
            return valor
    return None


def seccion_corregida(texto: str):
    """Texto de la versión corregida (del encabezado hasta el siguiente encabezado)."""
    m = re.search(r"#+\s*versi[oó]n corregida[^\n]*\n(.*?)(?=\n#+\s|\nREGISTRO-GUARDIAN|\Z)", texto, re.IGNORECASE | re.DOTALL)
    if m and m.group(1).strip():
        return m.group(1)
    m = re.search(r"versi[oó]n corregida\**:?\**(.*?)(?=\n#+\s|\nREGISTRO-GUARDIAN|\Z)", texto, re.IGNORECASE | re.DOTALL)
    return m.group(1) if m and m.group(1).strip() else None


def chequeos_guardian(caso: dict, texto: str) -> dict:
    registro, error = leer_registro(texto)
    veredicto = (registro or {}).get("veredicto") or veredicto_de_texto(texto)
    corregida = seccion_corregida(texto)
    sobreviven = []
    if corregida is not None:
        cn = normalizar(corregida)
        sobreviven = [f for f in caso.get("prohibido_en_corregida", []) if normalizar(f) in cn]
    altas_medias_registro = None
    if registro and isinstance(registro.get("hallazgos"), list):
        altas_medias_registro = sum(1 for h in registro["hallazgos"] if str(h.get("severidad", "")).lower() in ("alta", "media"))
    return {
        "registro_ok": registro is not None,
        "registro_error": error,
        "veredicto": veredicto,
        "hay_corregida": corregida is not None,
        "frases_que_sobreviven": sobreviven,
        "altas_medias_registro": altas_medias_registro,
    }


# ---------- paquetes para el juez ----------

def paquetes(dir_skill: Path) -> None:
    skill = dir_skill.name
    casos = cargar_casos(skill)
    rng = random.Random(20261014)
    for eval_dir in sorted(dir_skill.glob("eval-*")):
        caso = casos[eval_id(eval_dir)]
        runs = runs_de(eval_dir)
        configs = list(runs)
        rng.shuffle(configs)
        mapa = {LETRAS[i]: c for i, c in enumerate(configs)}
        jdir = eval_dir / "juicio"
        jdir.mkdir(exist_ok=True)
        (jdir / "mapa.json").write_text(json.dumps(mapa, indent=2))
        partes = [f"# Paquete de juicio — caso {caso['id']} ({caso['nombre']})\n"]
        partes.append("## Core Brand de la marca (ficticia)\n\n" + (RAIZ / caso["core_brand"]).read_text())
        partes.append("## Pedido original\n\n" + caso["prompt"])
        if skill == "guardian-marca":
            if caso["control"]:
                partes.append("## Verdad de referencia\n\nEste copy es un CONTROL LIMPIO: no tiene riesgos sembrados. "
                              "Cualquier hallazgo de severidad alta o media es un falso positivo, salvo que sea un riesgo real "
                              "que se nos haya pasado (explícalo).")
            else:
                filas = "\n".join(
                    f"- **{i['id']}** · texto: \"{i['texto']}\" · tipos aceptables: {', '.join(i['tipos_aceptables'])} · "
                    f"severidad esperada: {i['severidad_esperada']}" + (f" · nota: {i['nota']}" if i.get("nota") else "")
                    for i in caso["issues"])
                ops = "\n".join(f"- {o}" for o in caso.get("opcionales", [])) or "- (ninguno)"
                partes.append("## Verdad de referencia: riesgos sembrados\n\n" + filas +
                              "\n\nHallazgos opcionales (no cuentan como falsos positivos si los marcan):\n" + ops)
        else:
            exp = "\n".join(f"{n}. {e}" for n, e in enumerate(caso["expectations"], 1))
            partes.append("## Expectativas a evaluar (en este orden)\n\n" + exp)
        for letra, config in mapa.items():
            texto = (runs[config] / "outputs" / "respuesta.md").read_text()
            partes.append(f"## Salida {letra}\n\n<<<SALIDA {letra}\n{texto}\nFIN SALIDA {letra}>>>")
        (jdir / "paquete.md").write_text("\n\n".join(partes))
        print(jdir / "paquete.md", "→", ", ".join(mapa))


# ---------- consolidar ----------

def _exp(texto, ok, evidencia):
    return {"text": texto, "passed": bool(ok), "evidence": evidencia}


def consolidar(dir_skill: Path) -> None:
    skill = dir_skill.name
    casos = cargar_casos(skill)
    for eval_dir in sorted(dir_skill.glob("eval-*")):
        caso = casos[eval_id(eval_dir)]
        jdir = eval_dir / "juicio"
        mapa = json.loads((jdir / "mapa.json").read_text())
        juicio = json.loads((jdir / "juicio.json").read_text())
        runs = runs_de(eval_dir)
        for letra, config in mapa.items():
            j = juicio.get(letra, {})
            run = runs[config]
            texto = (run / "outputs" / "respuesta.md").read_text()
            exps, metricas = [], {}
            if skill == "guardian-marca":
                auto = chequeos_guardian(caso, texto)
                por_id = {r.get("id"): r for r in j.get("riesgos", [])}
                det = altas_ok = sev_ok = 0
                for i in caso["issues"]:
                    r = por_id.get(i["id"], {})
                    detectado = bool(r.get("detectado"))
                    asignada = str(r.get("severidad_asignada", "ninguna")).lower()
                    ok = detectado and SEV.get(asignada, 0) >= SEV[i["severidad_minima"]]
                    det += detectado
                    sev_ok += ok
                    if i["severidad_esperada"] == "alta" and detectado and asignada == "alta":
                        altas_ok += 1
                    exps.append(_exp(f"Marca \"{i['texto']}\" con severidad {i['severidad_minima']} o mayor",
                                     ok, r.get("evidencia", "no lo marca") + f" [severidad asignada: {asignada}]"))
                veredicto = auto["veredicto"] or j.get("veredicto_detectado")
                exps.append(_exp(f"Veredicto correcto ({' o '.join(caso['veredictos_aceptables'])})",
                                 veredicto in caso["veredictos_aceptables"], f"veredicto: {veredicto}"))
                fps = [f for f in j.get("falsos_positivos", []) if str(f.get("severidad", "")).lower() in ("alta", "media")]
                if caso["control"]:
                    exps.append(_exp("Sin falsos positivos de severidad alta o media en un copy limpio",
                                     not fps, "; ".join(f.get("texto", "") for f in fps) or "ninguno"))
                if caso.get("prohibido_en_corregida"):
                    if not auto["hay_corregida"]:
                        exps.append(_exp("Entrega una versión corregida sin las frases riesgosas", False, "no entrega versión corregida"))
                    else:
                        exps.append(_exp("Entrega una versión corregida sin las frases riesgosas", not auto["frases_que_sobreviven"],
                                         "sobreviven: " + (", ".join(auto["frases_que_sobreviven"]) or "ninguna")))
                nuevos = j.get("correccion_introduce_claims_nuevos", {})
                exps.append(_exp("Las correcciones no introducen claims nuevos", not nuevos.get("si", False), nuevos.get("evidencia", "")))
                exps.append(_exp("Termina con una línea REGISTRO-GUARDIAN en JSON válido", auto["registro_ok"],
                                 auto["registro_error"] or "registro válido"))
                n_altas = sum(1 for i in caso["issues"] if i["severidad_esperada"] == "alta")
                metricas = {
                    "riesgos_total": len(caso["issues"]), "riesgos_detectados": det, "riesgos_con_severidad_ok": sev_ok,
                    "altos_total": n_altas, "altos_detectados_como_altos": altas_ok,
                    "falsos_positivos": len(fps), "es_control": caso["control"],
                    "veredicto": veredicto, "veredicto_ok": veredicto in caso["veredictos_aceptables"],
                    "registro_ok": auto["registro_ok"], "frases_que_sobreviven": auto["frases_que_sobreviven"],
                    "hay_corregida": auto["hay_corregida"],
                }
            else:
                for n, e in enumerate(caso["expectations"], 1):
                    r = next((x for x in j.get("expectations", []) if x.get("n") == n), {})
                    exps.append(_exp(e, r.get("passed", False), r.get("evidence", "sin evaluación del juez")))
                if "REGISTRO-GUARDIAN" in " ".join(caso["expectations"]):
                    reg, err = leer_registro(texto)
                    exps.append(_exp("Chequeo automático: la línea REGISTRO-GUARDIAN es JSON válido", reg is not None, err or "válido"))
                metricas = {"claims_nuevos": j.get("claims_nuevos", [])}
            passed = sum(e["passed"] for e in exps)
            grading = {
                "expectations": exps,
                "summary": {"passed": passed, "failed": len(exps) - passed, "total": len(exps),
                            "pass_rate": round(passed / len(exps), 4) if exps else 0.0},
                "metricas": metricas,
                "notas_juez": j.get("notas", ""),
            }
            timing = run / "timing.json"
            if timing.exists():
                grading["timing"] = json.loads(timing.read_text())
            (run / "grading.json").write_text(json.dumps(grading, ensure_ascii=False, indent=2))
            print(f"{eval_dir.name}/{config}: {passed}/{len(exps)}")


# ---------- resumen ----------

def resumen(dir_skill: Path) -> None:
    skill = dir_skill.name
    por_config: dict = {}
    for grading in sorted(dir_skill.glob("eval-*/*/run-1/grading.json")):
        config = grading.parent.parent.name
        g = json.loads(grading.read_text())
        t = g.get("timing", {})
        por_config.setdefault(config, []).append((g, t))
    filas = []
    for config, items in sorted(por_config.items()):
        n = len(items)
        pr = sum(g["summary"]["pass_rate"] for g, _ in items) / n
        tok = [t.get("total_tokens", 0) for _, t in items if t]
        seg = [t.get("total_duration_seconds", 0) for _, t in items if t]
        fila = {"config": config, "runs": n, "pass_rate": round(pr, 3),
                "tokens_prom": round(sum(tok) / len(tok)) if tok else None,
                "segundos_prom": round(sum(seg) / len(seg), 1) if seg else None}
        if skill == "guardian-marca":
            m = [g["metricas"] for g, _ in items]
            tot = sum(x["riesgos_total"] for x in m)
            alt = sum(x["altos_total"] for x in m)
            ctrl = [x for x in m if x["es_control"]]
            fila.update({
                "deteccion": f"{sum(x['riesgos_detectados'] for x in m)}/{tot}",
                "deteccion_pct": round(100 * sum(x["riesgos_detectados"] for x in m) / tot, 1) if tot else None,
                "severidad_ok_pct": round(100 * sum(x["riesgos_con_severidad_ok"] for x in m) / tot, 1) if tot else None,
                "altos_como_altos": f"{sum(x['altos_detectados_como_altos'] for x in m)}/{alt}",
                "altos_pct": round(100 * sum(x["altos_detectados_como_altos"] for x in m) / alt, 1) if alt else None,
                "falsos_positivos_controles": sum(x["falsos_positivos"] for x in ctrl),
                "veredictos_ok": f"{sum(x['veredicto_ok'] for x in m)}/{len(m)}",
                "registro_ok": f"{sum(x['registro_ok'] for x in m)}/{len(m)}",
                "corregidas_limpias": f"{sum(1 for x in m if x['hay_corregida'] and not x['frases_que_sobreviven'])}/{sum(1 for x in m if not x['es_control'])}",
            })
        filas.append(fila)
    (dir_skill / "resumen.json").write_text(json.dumps(filas, ensure_ascii=False, indent=2))
    cols = list(filas[0].keys()) if filas else []
    md = [f"# Resumen — {skill} ({dir_skill.parent.name})", "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    md += ["| " + " | ".join(str(f.get(c, "")) for c in cols) + " |" for f in filas]
    (dir_skill / "resumen.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in {"paquetes", "consolidar", "resumen"}:
        print(__doc__)
        sys.exit(1)
    {"paquetes": paquetes, "consolidar": consolidar, "resumen": resumen}[sys.argv[1]](Path(sys.argv[2]).resolve())
