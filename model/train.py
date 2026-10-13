"""Entrena el clasificador de Lupa (regresión logística sobre rasgos hasheados + estilométricos).

Uso: python3 model/train.py --data /home/user/data --ghost /home/user/vivek3141/ghostbuster-data \
       --hd /home/user/jenna-russell/human_detectors/human_detectors.json

Los corpus de entrenamiento no se incluyen en el repositorio; solo se publican los pesos (model/lupa-model.json).
"""
import argparse
import base64
import glob
import json
import os
import random
import sys
import zlib
from multiprocessing import Pool

import numpy as np
import pandas as pd
import regex as re
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

sys.path.insert(0, os.path.dirname(__file__))
from features import D, N_DENSE, TOK, HAS_WORD, featurize, normalize  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SENT = re.compile(r"(?<=[.!?…])\s+|\n+")


def rng_for(name):
    return random.Random(f"lupa-v2-{name}")


def detok(s):
    s = re.sub(r" ([,.;:!?)\]%])", r"\1", s)
    s = re.sub(r"([(\[¿¡]) ", r"\1", s)
    return s


def split_sents(text):
    return [s.strip() for s in SENT.split(text.strip()) if s.strip()]


def chunks_of(text, lo, hi, rng, limit=None):
    """Corta un texto en fragmentos consecutivos de entre lo y hi palabras respetando oraciones."""
    out, cur, n = [], [], 0
    target = rng.randint(lo, hi)
    for s in split_sents(text):
        cur.append(s)
        n += len(s.split())
        if n >= target:
            out.append(" ".join(cur))
            cur, n, target = [], 0, rng.randint(lo, hi)
            if limit and len(out) >= limit:
                break
    if cur and n >= lo:
        out.append(" ".join(cur))
    return out


def span(sents, lo, hi, rng):
    """Un fragmento de lo-hi palabras que empieza en una oración al azar (como las ventanas y bloques de la página)."""
    if not sents:
        return None
    target = rng.randint(lo, hi)
    start = rng.randrange(len(sents))
    cur, n = [], 0
    for s in sents[start:]:
        cur.append(s)
        n += len(s.split())
        if n >= target:
            break
    if n < lo:  # demasiado cerca del final: completa hacia atrás
        for s in reversed(sents[:start]):
            cur.insert(0, s)
            n += len(s.split())
            if n >= lo:
                break
    return " ".join(cur) if n >= min(lo, 20) else None


def load(args):
    rows = []  # (text, label 1=IA, lang, source, group)

    for lang in ("es", "en"):
        df = pd.read_csv(f"{args.data}/AUTEXTIFICATION/subtask_1/{lang}/train.tsv", sep="\t")
        for r in df.itertuples():
            rows.append((r.text, int(r.label == "generated"), lang, "autext", f"autext-{lang}-{r.id}"))

    # Ghostbuster: ensayos, noticias (Reuters) y relatos; humanos vs ChatGPT y Claude.
    # Se toman fragmentos de cualquier parte del documento (no solo el inicio) y con la misma
    # distribución de longitudes para ambas clases, igual que los usa la página.
    for dom in ("essay", "reuter", "wp"):
        for sub, label, take in (("human", 0, 3000), ("claude", 1, 1800), ("gpt", 1, 900),
                                 ("gpt_writing", 1, 300), ("gpt_semantic", 1, 300), ("gpt_prompt1", 1, 300)):
            rng = rng_for(f"{dom}-{sub}")
            files = sorted(glob.glob(f"{args.ghost}/{dom}/{sub}/**/*.txt", recursive=True))
            rng.shuffle(files)
            for f in files[:take]:
                t = open(f, encoding="utf-8", errors="ignore").read().strip()
                if len(t.split()) < 30:
                    continue
                g = f"ghost-{dom}-{os.path.basename(os.path.dirname(f))}-{os.path.basename(f)}-{label}"
                sents = split_sents(t)
                for lo, hi in ((25, 60), (25, 60), (120, 220)):
                    c = span(sents, lo, hi, rng)
                    if c:
                        rows.append((c, label, "en", f"ghost-{dom}", g))

    # Español humano formal: Europarl y noticias EFE (CoNLL-2002).
    rng = rng_for("europarl")
    ep = []
    for f in sorted(glob.glob(f"{args.data}/europarl_raw/spanish/*.es")):
        txt = detok("\n".join(l.strip() for l in open(f, encoding="utf-8", errors="ignore") if l.strip()))
        ep.extend((c, os.path.basename(f)) for c in chunks_of(txt, 25, 220, rng))
    rng.shuffle(ep)
    for c, f in ep[:5000]:
        rows.append((c, 0, "es", "europarl", f"ep-{f}"))
    rng = rng_for("efe")
    for split in ("esp.train", "esp.testa", "esp.testb"):
        sent, sents = [], []
        for line in open(f"{args.data}/conll2002/{split}", encoding="latin-1"):
            line = line.strip()
            if not line:
                if sent:
                    sents.append(detok(" ".join(sent)))
                sent = []
            elif not line.startswith("-DOCSTART-"):
                sent.append(line.split(" ")[0])
        doc = "\n".join(s for s in sents if len(s.split()) > 3)
        for i, c in enumerate(chunks_of(doc, 25, 200, rng)):
            rows.append((c, 0, "es", "efe", f"efe-{split}-{i // 10}"))

    # Español de IA actual (escrito con un asistente de IA para este proyecto).
    rng = rng_for("esai")
    es_ai = [t.strip() for t in open(f"{HERE}/data/es_ia_moderno.txt", encoding="utf-8").read().split("\n===\n") if t.strip()]
    for i, t in enumerate(es_ai):
        sents = split_sents(t)
        rows.append((" ".join(sents), 1, "es", "es-ia-moderno", f"esai-{i}"))
        for _ in range(2):
            c = span(sents, 25, 60, rng)
            if c:
                rows.append((c, 1, "es", "es-ia-moderno", f"esai-{i}"))
    return rows


def is_test(group, test_groups):
    """Prueba = los documentos congelados en test_groups.json (y un 15 % fijo de EFE)."""
    if group.startswith("efe-"):
        return zlib.crc32(group.encode()) % 100 < 15
    return group in test_groups


def feat_row(text):
    h, d = featurize(text)
    return (np.fromiter(h.keys(), np.int32, len(h)), np.fromiter(h.values(), np.float32, len(h)),
            np.asarray(d, np.float32))


def build(texts, workers=4):
    idx, val, dense, indptr = [], [], [], [0]
    with Pool(workers) as p:
        for i, v, d in p.imap(feat_row, texts, chunksize=100):
            idx.append(i)
            val.append(v)
            dense.append(d)
            indptr.append(indptr[-1] + len(i))
    X = sparse.csr_matrix((np.concatenate(val), np.concatenate(idx), np.array(indptr, np.int64)), shape=(len(texts), D))
    return X, np.vstack(dense)


def stack(Xh, Xd, mu, sd, alpha):
    return sparse.hstack([Xh, sparse.csr_matrix((Xd - mu) / sd * alpha)]).tocsr()


def report(name, y, p, thr=0.5):
    y, p = np.asarray(y), np.asarray(p)
    out = {"n": int(len(y)), "acc": round(float(accuracy_score(y, p >= thr)), 4)}
    if len(set(y)) > 1:
        out["auroc"] = round(float(roc_auc_score(y, p)), 4)
        out["f1"] = round(float(f1_score(y, p >= thr)), 4)
    if (y == 0).any():
        out["fpr_humano"] = round(float((p[y == 0] >= thr).mean()), 4)
    if (y == 1).any():
        out["recall_ia"] = round(float((p[y == 1] >= thr).mean()), 4)
    print(f"  {name:28s} {out}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="/home/user/data")
    ap.add_argument("--ghost", default="/home/user/vivek3141/ghostbuster-data")
    ap.add_argument("--hd", default="/home/user/jenna-russell/human_detectors/human_detectors.json")
    ap.add_argument("--C", type=float, default=0)
    ap.add_argument("--alpha", type=float, default=0.3)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows = load(args)
    df = pd.DataFrame(rows, columns=["text", "y", "lang", "source", "group"])
    df = df[df.text.str.split().str.len() >= 8].reset_index(drop=True)
    test_groups = set(json.load(open(f"{HERE}/test_groups.json")))
    df["split"] = np.where(df.group.map(lambda g: is_test(g, test_groups)), "test", "train")
    print(df.groupby(["source", "lang", "y", "split"]).size().unstack(fill_value=0))

    Xh, Xd = build(df.text.tolist())
    tr = (df.split == "train").values
    mu = Xd[tr].mean(0)
    sd = Xd[tr].std(0) + 1e-6
    # Equilibra idioma x clase para que ninguna combinación domine.
    key = df.lang + "-" + df.y.astype(str)
    w = (1.0 / key.map(key[tr].value_counts())).values
    w = w / w[tr].mean()
    w[(df.source == "es-ia-moderno").values] *= 3.0

    best = None
    X = stack(Xh, Xd, mu, sd, args.alpha)
    for C in ([args.C] if args.C else [8.0, 32.0]):
        clf = LogisticRegression(C=C, max_iter=3000, solver="liblinear")
        # Validación interna: 10 % de los grupos de entrenamiento.
        vg = {g for g in df.group[tr].unique() if zlib.crc32(g.encode()) % 10 == 0}
        vmask = df.group.isin(vg).values & tr
        fit = tr & ~vmask
        clf.fit(X[fit], df.y.values[fit], sample_weight=w[fit])
        auc = roc_auc_score(df.y.values[vmask], clf.predict_proba(X[vmask])[:, 1])
        print(f"C={C}: AUROC validación {auc:.4f}")
        if best is None or auc > best[0]:
            best = (auc, C)
    C = best[1]
    clf = LogisticRegression(C=C, max_iter=3000, solver="liblinear")
    clf.fit(X[tr], df.y.values[tr], sample_weight=w[tr])

    # Cuantización a int8 de los pesos hasheados (lo que usa el navegador).
    coef = clf.coef_[0].astype(np.float64)
    wh, wd, b = coef[:D], coef[D:], float(clf.intercept_[0])
    scale = float(np.abs(wh).max() / 127)
    q = np.clip(np.round(wh / scale), -127, 127).astype(np.int8)
    wq = q.astype(np.float64) * scale

    def predict(Xh_, Xd_):
        z = Xh_ @ wq + ((Xd_ - mu) / sd * args.alpha) @ wd + b
        return 1 / (1 + np.exp(-z))

    te = ~tr
    p = predict(Xh[te], Xd[te])
    sub = df[te].assign(p=p)
    print("\nPrueba (15 % de documentos nunca vistos):")
    results = {"global": report("global", sub.y, sub.p)}
    for (src, lang), g in sub.groupby(["source", "lang"]):
        results[f"{src}-{lang}"] = report(f"{src}-{lang}", g.y, g.p)
    for lang, g in sub.groupby("lang"):
        results[f"idioma-{lang}"] = report(f"idioma-{lang}", g.y, g.p)

    # Prueba fuera de distribución: artículos de 2024 (GPT-4o, Claude 3.5 Sonnet, o1) frente a humanos.
    hd = json.load(open(args.hd))
    ys, ps = [], []
    for item in hd.values():
        text = item["article"]
        cs = chunks_of(text, 150, 150, rng_for("hd")) or [text]
        Hh, Hd = build(cs, workers=1)
        z = np.log(predict(Hh, Hd) / (1 - predict(Hh, Hd)))
        ys.append(int(item["ground_truth"] != "Human-written"))
        ps.append(float(1 / (1 + np.exp(-z.mean()))))
    print("\nFuera de distribución (human_detectors, 300 artículos en inglés de 2024):")
    results["human_detectors-2024"] = report("human_detectors-2024", ys, ps)
    gens = [item["generation_model"] for item in hd.values()]
    for m in sorted(set(gens)):
        sel = [i for i, g in enumerate(gens) if g == m]
        report(f"  modelo {m}", [ys[i] for i in sel], [ps[i] for i in sel])

    model = {
        "version": 2,
        "dBits": int(np.log2(D)),
        "scale": scale,
        "bias": b,
        "alpha": args.alpha,
        "mu": [round(float(x), 6) for x in mu],
        "sd": [round(float(x), 6) for x in sd],
        "wd": [round(float(x), 6) for x in wd],
        "w": base64.b64encode(q.tobytes()).decode(),
        "C": C,
        "metrics": results,
    }
    out = args.out or f"{HERE}/lupa-model.json"
    json.dump(model, open(out, "w"))
    # Muestras para comprobar que el navegador calcula lo mismo.
    probe = sub.sample(200, random_state=1)
    json.dump([{"text": t, "p": float(pp)} for t, pp in zip(probe.text, probe.p)],
              open(os.environ.get("LUPA_PROBE", "lupa-probe.json"), "w"), ensure_ascii=False)
    print(f"\nPesos guardados: {out} ({os.path.getsize(out) // 1024} KB), C={C}")


if __name__ == "__main__":
    main()
