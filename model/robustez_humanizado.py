"""Prueba de resistencia frente a texto «humanizado» (prueba interna del detector).

Uso:
  python3 model/robustez_humanizado.py preparar <carpeta>   # junta meta.json + out.txt, guarda data/es_ia_humanizado.txt
  python3 model/robustez_humanizado.py medir <carpeta> [--claude <carpeta_eval>]

<carpeta> contiene meta.json (id, split, estrategia, original) y out.txt (reescrituras '### <id>').
Las reescrituras de entrenamiento se guardan como IA para entrenar; las de prueba solo se usan para medir.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_es  # noqa: E402
import evaluate as ev  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ESTRATEGIAS = {"A": "parafraseo genérico", "B": "voz personal", "C": "imperfecciones", "D": "sin frases típicas ni plantilla"}


def load(folder):
    meta = json.load(open(os.path.join(folder, "meta.json")))
    out = data_es.parse_generated(os.path.join(folder, "out.txt"))
    for m in meta:
        m["humanizado"] = out.get(m["id"])
        m["new_id"] = ("hp" if m["split"] == "test" else "he") + m["id"][2:]
    return [m for m in meta if m["humanizado"]]


def preparar(folder):
    items = load(folder)
    path = os.path.join(HERE, "data", "es_ia_humanizado.txt")
    with open(path, "w", encoding="utf-8") as f:
        for m in items:
            f.write(f"### {m['new_id']}\n{m['humanizado']}\n\n")
    print(f"{len(items)} reescrituras guardadas en {path}")


def medir(folder, claude_folder=None):
    ev.setup([(os.path.join(HERE, "lupa-model.json"), os.path.join(HERE, "features.py"))])
    items = [m for m in load(folder) if m["split"] == "test"]
    po = ev.doc_scores([m["original"] for m in items])
    ph = ev.doc_scores([m["humanizado"] for m in items])
    est = np.array([m["estrategia"] for m in items])
    print(f"\nModelo local, {len(items)} textos de IA de prueba: IA detectada (umbral 50 %) original → humanizado")
    print(f"  todos                         {np.mean(po >= .5):.0%} → {np.mean(ph >= .5):.0%}   (media {po.mean():.0%} → {ph.mean():.0%})")
    for e, name in ESTRATEGIAS.items():
        m = est == e
        print(f"  {name:30s}{np.mean(po[m] >= .5):.0%} → {np.mean(ph[m] >= .5):.0%}   (media {po[m].mean():.0%} → {ph[m].mean():.0%})")
    rep = {"modelo": {"original": float(np.mean(po >= .5)), "humanizado": float(np.mean(ph >= .5))}}
    if claude_folder:
        bench = json.load(open(os.path.join(claude_folder, "bench.json")))
        cl = {}
        for line in open(os.path.join(claude_folder, "out_B_00.jsonl"), encoding="utf-8"):
            if line.strip():
                j = json.loads(line)
                cl[str(j["id"])] = float(j["ai"])
        byid = {b["id"]: b for b in bench}
        hum = [b for b in bench if b["y"] == 1 and b["id"] in cl]
        ctrl = [b for b in bench if b["y"] == 0 and b["id"] in cl]
        ch = np.array([cl[b["id"]] for b in hum]) / 100
        cc = np.array([cl[b["id"]] for b in ctrl]) / 100
        print(f"\nClaude Sonnet 5.5: textos humanizados con nota ≥ 50 %: {np.mean(ch >= .5):.0%} (media {ch.mean():.0%});"
              f" controles humanos con nota ≥ 50 %: {np.mean(cc >= .5):.0%} (media {cc.mean():.0%}, máximo {cc.max():.0%})")
        print(f"  separación humanizados / humanos (AUROC): {ev.metrics([1] * len(ch) + [0] * len(cc), list(ch) + list(cc))}")
        est_c = np.array([byid[b['id']]['estrategia'] for b in hum])
        for e, name in ESTRATEGIAS.items():
            m = est_c == e
            if m.any():
                print(f"  {name:30s} nota media {ch[m].mean():.0%}, ≥ 50 %: {np.mean(ch[m] >= .5):.0%}")
        rep["claude"] = {"humanizado_ge50": float(np.mean(ch >= .5)), "controles_ge50": float(np.mean(cc >= .5))}
    return rep


if __name__ == "__main__":
    cmd, folder = sys.argv[1], sys.argv[2]
    if cmd == "preparar":
        preparar(folder)
    else:
        medir(folder, sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--claude" else None)
