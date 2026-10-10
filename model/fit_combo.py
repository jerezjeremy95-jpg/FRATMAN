"""Mide a Claude como detector y ajusta cómo combinarlo con el modelo local.

Uso: python3 model/fit_combo.py <carpeta_prueba> [--model model/lupa-model.json] [--write]

<carpeta_prueba> contiene bench.json (de bench_claude.py) y las respuestas de Claude:
  out_B_*.jsonl  (instrucción nueva: {"id", "ai", ...})
  out_A_*.jsonl  (instrucción anterior: {"id", "overall", ...})
La combinación es una regresión logística z = c + a·z_modelo + b·logit(Claude); su precisión se estima con
validación cruzada de 10 bloques (cada texto se puntúa con pesos ajustados sin él).
Con --write guarda los pesos (combo) y las métricas (claude_bench) dentro del modelo.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evaluate as ev  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def read_jsonl(pattern, key):
    out = {}
    for f in sorted(glob.glob(pattern)):
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                j = json.loads(line)
                v = float(j[key])
            except Exception:
                continue
            out[str(j["id"])] = min(100.0, max(0.0, v))
    return out


def lg(p):
    p = np.clip(np.asarray(p, float), 0.01, 0.99)
    return np.log(p / (1 - p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--model", default=os.path.join(HERE, "lupa-model.json"))
    ap.add_argument("--features", default=os.path.join(HERE, "features.py"))
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    ev.setup([(args.model, args.features)])
    bench = json.load(open(os.path.join(args.folder, "bench.json")))
    cB = read_jsonl(os.path.join(args.folder, "out_B_*.jsonl"), "ai")
    cA = read_jsonl(os.path.join(args.folder, "out_A_*.jsonl"), "overall")
    print(f"respuestas de Claude: instrucción nueva {len(cB)}/{len(bench)}, anterior {len(cA)}")

    items = [b for b in bench if b["id"] in cB]
    y = np.array([b["y"] for b in items])
    pm = ev.doc_scores([b["text"] for b in items])
    zm = lg(pm)
    pc = np.array([cB[b["id"]] for b in items]) / 100
    zc = lg(pc)

    rep = {"n": int(len(items)), "modelo": ev.metrics(y, pm), "claude": ev.metrics(y, pc)}
    old = 1 / (1 + np.exp(-(0.5 * zm + 0.5 * zc)))
    rep["mitad_y_mitad"] = ev.metrics(y, old)

    X = np.c_[zm, zc]
    cv = np.zeros(len(y))
    for tr, te in StratifiedKFold(10, shuffle=True, random_state=0).split(X, y):
        clf = LogisticRegression(C=1.0).fit(X[tr], y[tr])
        cv[te] = clf.predict_proba(X[te])[:, 1]
    rep["combinado"] = ev.metrics(y, cv)
    clf = LogisticRegression(C=1.0).fit(X, y)
    combo = {"a": round(float(clf.coef_[0][0]), 4), "b": round(float(clf.coef_[0][1]), 4), "c": round(float(clf.intercept_[0]), 4)}
    rep["pesos"] = combo
    for thr in (0.5, 0.7, 0.85):
        rep[f"combinado_umbral_{thr}"] = ev.metrics(y, cv, thr)

    print("\nPrueba con Claude (Sonnet 5.5, esfuerzo medio), textos en español de etiqueta conocida:")
    for k in ("modelo", "claude", "mitad_y_mitad", "combinado", "combinado_umbral_0.7", "combinado_umbral_0.85"):
        print(f"  {k:22s} {rep[k]}")
    print("  pesos:", combo)

    print("\nPor fuente (umbral 50 %): aciertos modelo / Claude / combinado")
    rep["por_fuente"] = {}
    keys = sorted(set((b["y"], b["gen_model"] if b["y"] else b["source"]) for b in items))
    for yy, g in keys:
        m = np.array([(b["y"] == yy and (b["gen_model"] if b["y"] else b["source"]) == g) for b in items])
        r = {k: round(float(((p[m] >= 0.5) == y[m]).mean()), 3) for k, p in (("modelo", pm), ("claude", pc), ("combinado", cv))}
        r["n"] = int(m.sum())
        rep["por_fuente"][f"{'IA' if yy else 'humano'}-{g}"] = r
        print(f"  {('IA ' if yy else 'humano ') + g:22s} n={r['n']:3d}  {r['modelo']:.2f} / {r['claude']:.2f} / {r['combinado']:.2f}")

    if cA:
        ia = [b for b in bench if b["id"] in cA and b["id"] in cB]
        ya = np.array([b["y"] for b in ia])
        pa = np.array([cA[b["id"]] for b in ia]) / 100
        pb = np.array([cB[b["id"]] for b in ia]) / 100
        pma = ev.doc_scores([b["text"] for b in ia])
        rep["instruccion_anterior"] = {"n": len(ia), "claude_A": ev.metrics(ya, pa), "claude_B": ev.metrics(ya, pb),
                                       "pagina_anterior_mitad_y_mitad": ev.metrics(ya, 1 / (1 + np.exp(-(0.5 * lg(pma) + 0.5 * lg(pa)))))}
        print("\nInstrucción anterior frente a la nueva (mismos textos):")
        for k, v in rep["instruccion_anterior"].items():
            print(f"  {k:30s} {v}")
        print(f"  media de Claude en textos de IA: anterior {pa[ya == 1].mean() * 100:.0f} %, nueva {pb[ya == 1].mean() * 100:.0f} %")
        print(f"  media de Claude en textos humanos: anterior {pa[ya == 0].mean() * 100:.0f} %, nueva {pb[ya == 0].mean() * 100:.0f} %")

    json.dump(rep, open(os.path.join(args.folder, "fit.json"), "w"), indent=1)
    if args.write:
        m = json.load(open(args.model))
        m["combo"] = combo
        m["claude_bench"] = {"n": rep["n"], "modelo": rep["modelo"], "claude": rep["claude"], "combinado": rep["combinado"],
                             "umbral_0.7": rep["combinado_umbral_0.7"], "por_fuente": rep["por_fuente"]}
        json.dump(m, open(args.model, "w"))
        print("Pesos y métricas guardados en", args.model)


if __name__ == "__main__":
    main()
