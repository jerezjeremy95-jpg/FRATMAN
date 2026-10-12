"""Entrena el modelo de Lupa solo con textos en español (versión 3).

Uso: python3 model/train_es.py [--out model/lupa-model.json]
Fuentes y partición: model/data_es.py. Los documentos de prueba nunca se usan para entrenar.
"""
import argparse
import base64
import json
import os
import random
import sys
import zlib

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_es  # noqa: E402
from features import D  # noqa: E402
from train import build, span, split_sents, stack  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def training_rows(docs):
    """Fragmentos como los que puntúa la página: ventanas de 25-60 palabras y bloques de 120-220,
    tomados de cualquier parte del documento; los textos cortos se usan enteros."""
    rows = []
    for d in docs:
        rng = random.Random(f"lupa-v3-{d['group']}")
        n = len(d["text"].split())
        if n <= 70:
            rows.append((d["text"], d["y"], d["source"], d["group"]))
            continue
        sents = split_sents(d["text"])
        for lo, hi in ((25, 60), (25, 60), (120, 220)):
            c = span(sents, lo, hi, rng)
            if c:
                rows.append((c, d["y"], d["source"], d["group"]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "lupa-model.json"))
    ap.add_argument("--alpha", type=float, default=0.3)
    ap.add_argument("--C", type=float, default=0)
    ap.add_argument("--modern-weight", type=float, default=2.0)
    args = ap.parse_args()

    docs = data_es.load_docs()
    frozen = data_es.frozen_groups()
    train_docs = [d for d in docs if not data_es.is_test(d["group"], frozen)]
    rows = training_rows(train_docs)
    texts = [r[0] for r in rows]
    y = np.array([r[1] for r in rows])
    src = np.array([r[2] for r in rows])
    groups = np.array([r[3] for r in rows])
    print(f"documentos de entrenamiento: {len(train_docs)}; fragmentos: {len(rows)} (IA {int(y.sum())}, humanos {int((1 - y).sum())})")
    for s in sorted(set(src)):
        m = src == s
        print(f"  {s:14s} {int(m.sum()):6d} fragmentos, IA {int(y[m].sum())}")

    Xh, Xd = build(texts)
    mu, sd = Xd.mean(0), Xd.std(0) + 1e-6
    X = stack(Xh, Xd, mu, sd, args.alpha)
    w = np.where(y == 1, 0.5 / y.mean(), 0.5 / (1 - y.mean()))
    modern = np.isin(src, ["ia-generado", "es-ia-moderno", "ia-humanizada"])
    w[modern] *= args.modern_weight
    w = w / w.mean()

    val = np.array([zlib.crc32(g.encode()) % 10 == 0 for g in groups])
    best = None
    for C in ([args.C] if args.C else [8.0, 32.0]):
        clf = LogisticRegression(C=C, max_iter=3000, solver="liblinear")
        clf.fit(X[~val], y[~val], sample_weight=w[~val])
        pv = clf.predict_proba(X[val])[:, 1]
        auc = roc_auc_score(y[val], pv)
        auc_m = roc_auc_score(y[val & (modern | (y == 0))], clf.predict_proba(X[val & (modern | (y == 0))])[:, 1])
        print(f"C={C}: AUROC validación {auc:.4f} (IA actual frente a humanos: {auc_m:.4f})")
        if best is None or auc + auc_m > best[0]:
            best = (auc + auc_m, C)
    C = best[1]
    clf = LogisticRegression(C=C, max_iter=3000, solver="liblinear")
    clf.fit(X, y, sample_weight=w)

    coef = clf.coef_[0].astype(np.float64)
    wh, wd, b = coef[:D], coef[D:], float(clf.intercept_[0])
    scale = float(np.abs(wh).max() / 127)
    q = np.clip(np.round(wh / scale), -127, 127).astype(np.int8)
    model = {
        "version": 3, "lang": "es", "dBits": int(np.log2(D)), "scale": scale, "bias": b, "alpha": args.alpha,
        "mu": [round(float(x), 6) for x in mu], "sd": [round(float(x), 6) for x in sd], "wd": [round(float(x), 6) for x in wd],
        "w": base64.b64encode(q.tobytes()).decode(), "C": C, "metrics": {},
    }
    json.dump(model, open(args.out, "w"))
    print(f"Pesos guardados: {args.out} ({os.path.getsize(args.out) // 1024} KB), C={C}")


if __name__ == "__main__":
    main()
