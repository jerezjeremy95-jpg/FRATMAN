"""Prueba para medir a Claude como detector: 240 documentos en español de etiqueta conocida, todos de la
partición de prueba (nunca usados para entrenar).

Uso: python3 model/bench_claude.py <carpeta_salida>
Escribe en la carpeta: bench.json (con etiquetas, solo para puntuar), lotes sin etiquetas para cada versión de
la instrucción (A = la anterior, por oraciones; B = la nueva, por bloques) y guarda los grupos elegidos en
model/bench_claude_ids.json. Los textos no se incluyen en el repositorio.
"""
import json
import os
import random
import sys

import regex as re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_es  # noqa: E402
import evaluate as ev  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
HUMAN = {"cows": 30, "fakenews": 25, "ancora": 20, "europarl": 15, "autext": 20, "efe": 10}
AI = {"ia-generado": 90, "autext": 20, "es-ia-moderno": 10}


def trim(text, max_words=350):
    out, n = [], 0
    for s in re.split(r"(?<=[.!?…])\s+", text.strip()):
        if n and n + len(s.split()) > max_words:
            break
        out.append(s)
        n += len(s.split())
    return " ".join(out) if out else text


def blocks_input(text):
    """Como la página: bloques de ~150 palabras marcados [B1], [B2]…"""
    bl = ev.blocks(ev.sentences(text)) or [(text, 1)]
    return "\n\n".join(f"[B{k + 1}] {t}" for k, (t, _) in enumerate(bl))


def sentences_input(text):
    """Como la versión anterior de la página: una oración por línea con su índice."""
    lines = [re.sub(r"\s+", " ", s.strip()) for s, _ in ev.sentences(text)]
    return "\n".join(f"{i}\t{s}" for i, s in enumerate(lines))


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    rnd = random.Random(23)
    frozen = data_es.frozen_groups()
    test = [d for d in data_es.load_docs() if data_es.is_test(d["group"], frozen)]
    gen_model = {}
    for k in range(150):
        gen_model[f"gen-b{k:04d}"] = ("haiku", "sonnet", "opus")[k // 50]
    chosen = []
    for quotas, y in ((HUMAN, 0), (AI, 1)):
        for src, n in quotas.items():
            pool = [d for d in test if d["source"] == src and d["y"] == y and len(d["text"].split()) >= (40 if src == "autext" else 60)]
            if src == "ia-generado":  # 30 por modelo
                per = []
                for m in ("haiku", "sonnet", "opus"):
                    pm = [d for d in pool if gen_model.get(d["group"]) == m]
                    rnd.shuffle(pm)
                    per += pm[: n // 3]
                pool = per
            else:
                rnd.shuffle(pool)
                pool = pool[:n]
            chosen += pool
    rnd.shuffle(chosen)
    bench = []
    for k, d in enumerate(chosen):
        t = trim(d["text"])
        bench.append({"id": f"t{k:03d}", "text": t, "y": d["y"], "source": d["source"], "group": d["group"],
                      "gen_model": gen_model.get(d["group"], "autext" if d["source"] == "autext" else d["source"])})
    json.dump(bench, open(os.path.join(out, "bench.json"), "w"), ensure_ascii=False, indent=1)
    json.dump([b["group"] for b in bench], open(os.path.join(HERE, "bench_claude_ids.json"), "w"), indent=0)
    size = 16
    for v, fn in (("B", blocks_input), ("A", sentences_input)):
        items = bench if v == "B" else bench[:96]
        for k in range(0, len(items), size):
            json.dump([{"id": b["id"], "texto": fn(b["text"])} for b in items[k:k + size]],
                      open(os.path.join(out, f"in_{v}_{k // size:02d}.json"), "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(len(bench), Counter((b["y"], b["source"]) for b in bench))
    print("palabras (mediana):", sorted(len(b["text"].split()) for b in bench)[len(bench) // 2])


if __name__ == "__main__":
    main()
