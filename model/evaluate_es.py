"""Auditoría del modelo en español con la lógica exacta de la página (ver evaluate.py).

Uso: python3 model/evaluate_es.py [--model model/lupa-model.json] [--out informe.json] [--write-metrics]
Prueba = documentos que data_es.is_test() marca como prueba (nunca usados para entrenar).
"""
import argparse
import json
import os
import random
import sys

import numpy as np
import regex as re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_es  # noqa: E402
import evaluate as ev  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = {
    "autext": "Tuits, manuales y textos legales (AuTexTification, humanos y GPT-3/BLOOM)",
    "autext2": "Más texto de GPT-3/BLOOM (AuTexTification)",
    "europarl": "Debates parlamentarios (humanos)",
    "efe": "Noticias de agencia EFE (humanos)",
    "ancora": "Prensa española, AnCora (humanos)",
    "gsd": "Textos web, GSD (humanos)",
    "fakenews": "Noticias reales y falsas escritas por personas",
    "cows": "Redacciones de estudiantes universitarios",
    "es-ia-moderno": "IA actual: conjunto inicial",
    "ia-generado": "IA actual: Haiku, Sonnet y Opus (temas no vistos)",
}


def truncate(text, max_words=600):
    words = 0
    out = []
    for s in re.split(r"(?<=[.!?…])\s+", text):
        out.append(s)
        words += len(s.split())
        if words >= max_words:
            break
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.path.join(HERE, "lupa-model.json"))
    ap.add_argument("--features", default=os.path.join(HERE, "features.py"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--write-metrics", action="store_true")
    ap.add_argument("--max-per-source", type=int, default=2500)
    args = ap.parse_args()
    ev.setup([(args.model, args.features)])

    frozen = data_es.frozen_groups()
    rnd = random.Random(17)
    test = [d for d in data_es.load_docs() if data_es.is_test(d["group"], frozen)]
    by_src = {}
    for d in test:
        by_src.setdefault(d["source"], []).append(d)
    bench = []
    for s, ds in sorted(by_src.items()):
        rnd.shuffle(ds)
        bench += ds[: args.max_per_source]
    texts = [truncate(d["text"]) for d in bench]
    ys = np.array([d["y"] for d in bench])
    src = np.array([d["source"] for d in bench])
    nw = np.array([len(ev.WORDS.findall(t)) for t in texts])
    p = ev.doc_scores(texts)
    rep = {"documentos": {}, "longitud": {}, "umbrales": {}}

    print("\n1) Documentos de prueba en español (puntuación global de la página, umbral 50 %)")
    rep["documentos"]["todo-es"] = ev.metrics(ys, p)
    print(f"  {'todo':16s} {rep['documentos']['todo-es']}")
    for s in sorted(set(src)):
        rep["documentos"][s] = ev.metrics(ys[src == s], p[src == s])
        print(f"  {s:16s} {rep['documentos'][s]}")
    modern = np.isin(src, ["ia-generado", "es-ia-moderno"]) | (ys == 0)
    rep["documentos"]["ia-actual-vs-humanos"] = ev.metrics(ys[modern], p[modern])
    print(f"  {'IA actual vs humanos':16s} {rep['documentos']['ia-actual-vs-humanos']}")

    print("\n2) Según longitud (todas las fuentes)")
    for lo, hi in ((40, 100), (100, 200), (200, 10**9)):
        m = (nw >= lo) & (nw < hi)
        key = f"es {lo}-{hi if hi < 10**9 else '+'}"
        rep["longitud"][key] = ev.metrics(ys[m], p[m])
        print(f"  {key:12s} {rep['longitud'][key]}")

    print("\n3) Umbrales (textos de 40+ palabras)")
    m40 = nw >= 40
    for thr in (0.5, 0.6, 0.7, 0.8, 0.85, 0.9):
        rep["umbrales"][str(thr)] = ev.metrics(ys[m40], p[m40], thr)
        r = rep["umbrales"][str(thr)]
        print(f"  {thr:.2f}: falsos positivos {r['fpr_humano']:.3f}  IA detectada {r['recall_ia']:.3f}")

    print("\n4) Documentos mezclados (oraciones)")
    # Párrafos humanos (cualquier fuente) intercalados con texto de IA actual.
    mix = [{"text": t, "y": int(y_), "source": s} for t, y_, s in zip(texts, ys, src)]
    pool = {0: [r["text"] for r in mix if r["y"] == 0 and len(r["text"].split()) >= 60],
            1: [r["text"] for r in mix if r["y"] == 1 and r["source"] in ("ia-generado", "es-ia-moderno") and len(r["text"].split()) >= 60]}
    docs = []
    rr = random.Random(5)
    for _ in range(300):
        ss, labs = [], []
        first = rr.randint(0, 1)
        for k in range(rr.randint(2, 4)):
            lab = (k + first) % 2
            st = ev.sentences(rr.choice(pool[lab]))
            ss += st
            labs += [lab] * len(st)
        docs.append(("es", ss, labs))
    wt, wy = [], []
    for _, ss, labs in docs:
        wt += ev.windows(ss, 40)
        wy += labs
    ps = ev.sig(ev.zs_of(wt))
    rep["oraciones"] = {f"umbral {t}": ev.metrics(wy, ps, t) for t in (0.5, 0.7)}
    for k, v in rep["oraciones"].items():
        print(f"  {k}: {v}")

    print("\n5) Robustez a renglones de PDF")
    idx = [i for i in range(len(texts)) if nw[i] >= 100]
    idx = random.Random(11).sample(idx, min(600, len(idx)))
    wrapped = ["\n".join(re.findall(r".{1,80}(?:\s+|$)", re.sub(r"\s+", " ", texts[i]))) for i in idx]
    pw = ev.doc_scores(wrapped)
    rep["pdf"] = {"cambio_medio": round(float(np.abs(p[idx] - pw).mean()), 4), "renglones_pdf": ev.metrics(ys[idx], pw)}
    print("  ", rep["pdf"])

    if args.out:
        json.dump(rep, open(args.out, "w"), indent=1)
    if args.write_metrics:
        m = json.load(open(args.model))
        m["metrics"] = {**rep["documentos"], "longitud": rep["longitud"], "oraciones": rep["oraciones"]["umbral 0.7"],
                        "umbrales": rep["umbrales"], "nombres": NAMES}
        json.dump(m, open(args.model, "w"))
        print("Métricas guardadas en", args.model)


if __name__ == "__main__":
    main()
