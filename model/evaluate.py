"""Auditoría de precisión de Lupa con la lógica exacta de la página (ventanas por oración y bloques por documento).

Uso:
  python3 model/evaluate.py --bench bench.json [--model model/lupa-model.json] [--features model/features.py]
                            [--hd human_detectors.json] [--out informe.json] [--write-metrics]

`bench.json` es la lista congelada de documentos de prueba ({text, y, lang, source, group}); sus grupos
están en model/test_groups.json y train.py nunca entrena con ellos. Los textos no se incluyen en el repo.
Con --write-metrics, las métricas que muestra la página se guardan dentro del modelo.
"""
import argparse
import base64
import importlib.util
import json
import os
import random
from multiprocessing import Pool

import numpy as np
import regex as re
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
SPLIT = re.compile(r"(?:[^.!?…\n]|\n(?![ \t]*\n))+(?:[.!?…]+[\"'”»)\]]*|(?=\n[ \t]*\n)|\Z)|\n+")
WORDS = re.compile(r"[\p{L}\p{M}\p{N}]+(?:'[\p{L}\p{M}]+)*")
HASW = re.compile(r"[\p{L}\p{N}]")
LEGACY_SPLIT = re.compile(r"[^.!?…\n]+(?:[.!?…]+[\"'”»)\]]*|\Z)|\n+")
CTX = {"legacy": False}


def clean(s):
    """Como la página: un salto de línea dentro de una oración cuenta como espacio."""
    return s.strip() if CTX["legacy"] else re.sub(r"\s*\n\s*", " ", s.strip())


def setup(pairs):
    """pairs: [(modelo.json, features.py), ...]; con varios, la puntuación es la media de sus logits."""
    CTX["models"] = []
    for k, (model_path, features_path) in enumerate(pairs):
        spec = importlib.util.spec_from_file_location(f"lupa_features_{k}", features_path)
        feats = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(feats)
        m = json.load(open(model_path))
        CTX["models"].append(dict(feats=feats, m=m, w=np.frombuffer(base64.b64decode(m["w"]), np.int8).astype(np.float64) * m["scale"],
                                  mu=np.array(m["mu"]), sd=np.array(m["sd"]), wd=np.array(m["wd"])))


def z_of(text):
    zs = []
    for c in CTX["models"]:
        h, d = c["feats"].featurize(text)
        w = c["w"]
        zs.append(c["m"]["bias"] + sum(v * w[i] for i, v in h.items()) + float(((np.array(d) - c["mu"]) / c["sd"] * c["m"]["alpha"]) @ c["wd"]))
    return float(np.mean(zs))


def zs_of(texts, workers=4):
    with Pool(workers) as p:
        return np.array(p.map(z_of, texts, chunksize=50))


def sig(z):
    return 1 / (1 + np.exp(-np.asarray(z, float)))


def sentences(text):
    """Igual que splitSentences() de la página."""
    out = []
    for mt in (LEGACY_SPLIT if CTX["legacy"] else SPLIT).finditer(text):
        s = mt.group(0)
        if not s or re.fullmatch(r"\s+", s) or not HASW.search(s):
            continue
        n = len(WORDS.findall(s))
        if n:
            out.append((s, n))
    return out


def windows(sents, target=40, spread=6):
    """Igual que la página: cada oración con sus vecinas hasta reunir `target` palabras."""
    out = []
    for i, (_, n0) in enumerate(sents):
        lo = hi = i
        n = n0
        while n < target and (lo > 0 or hi < len(sents) - 1) and hi - lo < spread:
            if hi < len(sents) - 1:
                hi += 1
                n += sents[hi][1]
            if n < target and lo > 0:
                lo -= 1
                n += sents[lo][1]
        out.append(" ".join(clean(s) for s, _ in sents[lo:hi + 1]))
    return out


def blocks(sents, size=150, tail=60):
    """Igual que la página: bloques de ~150 palabras; un resto de menos de 60 se une al último bloque."""
    out, cur, n = [], [], 0
    for s, k in sents:
        cur.append(clean(s))
        n += k
        if n >= size:
            out.append((" ".join(cur), n))
            cur, n = [], 0
    if cur:
        if out and n < tail:
            t, k = out[-1]
            out[-1] = (t + " " + " ".join(cur), k + n)
        else:
            out.append((" ".join(cur), n))
    return out


def doc_scores(texts):
    """Probabilidad global de la página: media de logits de los bloques, ponderada por palabras."""
    bl = [blocks(sentences(t)) or [(t, 1)] for t in texts]
    flat = [b for bs in bl for b, _ in bs]
    zs = zs_of(flat)
    out, k = [], 0
    for bs in bl:
        n = np.array([max(1, x) for _, x in bs], float)
        out.append(float(sig((zs[k:k + len(bs)] * n).sum() / n.sum())))
        k += len(bs)
    return np.array(out)


def metrics(y, p, thr=0.5):
    y, p = np.asarray(y), np.asarray(p)
    r = {"n": int(len(y)), "acc": float(((p >= thr) == y).mean())}
    if len(set(y.tolist())) > 1:
        r["auroc"] = float(roc_auc_score(y, p))
    if (y == 0).any():
        r["fpr_humano"] = float((p[y == 0] >= thr).mean())
    if (y == 1).any():
        r["recall_ia"] = float((p[y == 1] >= thr).mean())
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}


def mixed_docs(bench, seed=5, per_group=60):
    """Documentos que alternan fragmentos humanos y de IA del mismo tipo; etiqueta por oración."""
    rnd = random.Random(seed)
    groups = {}
    for r in bench:
        if len(r["text"].split()) >= 40:
            groups.setdefault((r["source"], r["lang"]), {0: [], 1: []})[r["y"]].append(r["text"])
    docs = []
    for key in sorted(groups):
        hu, ai = groups[key][0], groups[key][1]
        if len(hu) < 3 or len(ai) < 3:
            continue
        for _ in range(per_group):
            ss, labs = [], []
            first = rnd.randint(0, 1)
            for k in range(rnd.randint(2, 4)):
                lab = (k + first) % 2
                st = sentences(rnd.choice(ai if lab else hu))
                ss += st
                labs += [lab] * len(st)
            docs.append((key[1], ss, labs))
    return docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", required=True)
    ap.add_argument("--model", default=os.path.join(HERE, "lupa-model.json"))
    ap.add_argument("--features", default=os.path.join(HERE, "features.py"))
    ap.add_argument("--hd", default="/home/user/jenna-russell/human_detectors/human_detectors.json")
    ap.add_argument("--out", default=None)
    ap.add_argument("--write-metrics", action="store_true")
    ap.add_argument("--legacy", action="store_true", help="lógica de la versión publicada antes de la auditoría")
    ap.add_argument("--model2", default=None, help="segundo modelo para evaluar la combinación de ambos")
    ap.add_argument("--features2", default=None)
    args = ap.parse_args()
    setup([(args.model, args.features)] + ([(args.model2, args.features2)] if args.model2 else []))
    CTX["legacy"] = args.legacy
    bench = json.load(open(args.bench))
    rep = {}

    texts = [r["text"] for r in bench]
    ys = np.array([r["y"] for r in bench])
    nw = np.array([len(WORDS.findall(t)) for t in texts])
    p = doc_scores(texts)
    src = np.array([f"{r['source']}-{r['lang']}" for r in bench])
    lang = np.array([r["lang"] for r in bench])

    print("\n1) Documentos de prueba (puntuación global de la página, umbral 50 %)")
    rep["documentos"] = {}
    for name, mask in [("todo", np.ones(len(ys), bool)), ("idioma-es", lang == "es"), ("idioma-en", lang == "en")] + \
            [(s, src == s) for s in sorted(set(src))]:
        rep["documentos"][name] = metrics(ys[mask], p[mask])
        print(f"  {name:22s} {rep['documentos'][name]}")

    print("\n2) Según longitud")
    rep["longitud"] = {}
    for lg in ("es", "en"):
        for lo, hi in ((40, 100), (100, 200), (200, 10**9), (0, 40)):
            mask = (lang == lg) & (nw >= lo) & (nw < hi)
            if mask.sum() >= 50:
                key = f"{lg} {lo}-{hi if hi < 10**9 else '+'}"
                rep["longitud"][key] = metrics(ys[mask], p[mask])
                print(f"  {key:12s} {rep['longitud'][key]}")

    print("\n3) Umbrales (textos de 40+ palabras)")
    rep["umbrales"] = {}
    m40 = nw >= 40
    for thr in (0.5, 0.6, 0.7, 0.8, 0.85, 0.9):
        rep["umbrales"][str(thr)] = {lg: metrics(ys[m40 & (lang == lg)], p[m40 & (lang == lg)], thr) for lg in ("es", "en")}
        print(f"  {thr:.2f} " + "  ".join(f"{lg}: fpr {v['fpr_humano']:.3f} recall {v['recall_ia']:.3f}" for lg, v in rep["umbrales"][str(thr)].items()))

    print("\n4) Documentos mezclados: precisión por oración (ventanas de la página)")
    docs = mixed_docs(bench)
    rep["oraciones"] = {}
    for target in (40, 60):
        wt, wy, wl = [], [], []
        for lg, ss, labs in docs:
            wt += windows(ss, target)
            wy += labs
            wl += [lg] * len(labs)
        ps = sig(zs_of(wt))
        wy, wl = np.array(wy), np.array(wl)
        for thr in (0.5, 0.7):
            r = metrics(wy, ps, thr)
            rep["oraciones"][f"ventana {target} umbral {thr}"] = r
            print(f"  ventana {target} umbral {thr}: {r}")
        rep["oraciones"][f"ventana {target} por idioma"] = {lg: metrics(wy[wl == lg], ps[wl == lg], 0.7) for lg in ("es", "en")}

    print("\n6) Robustez: el mismo texto con renglones partidos como en un PDF (cada ~80 caracteres)")
    rnd = random.Random(11)
    idx = [i for i in range(len(texts)) if nw[i] >= 100]
    idx = rnd.sample(idx, min(800, len(idx)))
    wrapped = ["\n".join(re.findall(r".{1,80}(?:\s+|$)", re.sub(r"\s+", " ", texts[i]))) for i in idx]
    pw = doc_scores(wrapped)
    po = p[idx]
    rep["pdf"] = {"original": metrics(ys[idx], po), "renglones_pdf": metrics(ys[idx], pw),
                  "cambio_medio": round(float(np.abs(po - pw).mean()), 4)}
    for k, v in rep["pdf"].items():
        print(f"  {k:14s} {v}")

    print("\n5) Artículos de 2024 (human_detectors), fuera del entrenamiento")
    hd = json.load(open(args.hd))
    hy = np.array([int(x["ground_truth"] != "Human-written") for x in hd.values()])
    hp = doc_scores([x["article"] for x in hd.values()])
    rep["human_detectors-2024"] = metrics(hy, hp)
    print("  ", rep["human_detectors-2024"])
    gens = np.array([x["generation_model"] for x in hd.values()])
    rep["hd_por_modelo"] = {g: metrics(hy[gens == g], hp[gens == g]) for g in sorted(set(gens))}
    for g, r in rep["hd_por_modelo"].items():
        print(f"     {g:22s} {r}")

    if args.out:
        json.dump(rep, open(args.out, "w"), indent=1)
    if args.write_metrics:
        m = json.load(open(args.model))
        m["metrics"] = {**rep["documentos"], "human_detectors-2024": rep["human_detectors-2024"],
                        "longitud": rep["longitud"], "oraciones": rep["oraciones"]}
        json.dump(m, open(args.model, "w"))
        print("Métricas guardadas en", args.model)


if __name__ == "__main__":
    main()
