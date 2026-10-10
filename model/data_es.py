"""Corpus en español de Lupa: documentos humanos y de IA, con su partición fija de prueba.

Los textos no se incluyen en el repositorio (salvo los generados para este proyecto); este módulo
los lee de las copias locales de cada corpus. Ver model/README.md.
"""
import glob
import json
import os
import zlib

import pandas as pd
import regex as re

HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULTS = {
    "data": "/home/user/data",  # AUTEXTIFICATION/, europarl_raw/, conll2002/
    "cows": "/home/user/ucdaviscl/cowsl2h",
    "gsd": "/home/user/universaldependencies/ud_spanish-gsd",
    "ancora": "/home/user/universaldependencies/ud_spanish-ancora",
    "fakenews": "/home/user/jpposadas/fakenewscorpusspanish",
    "gen": os.path.join(HERE, "data", "es_ia_generado.txt"),
}


def detok(s):
    s = re.sub(r" ([,.;:!?)\]%»])", r"\1", s)
    s = re.sub(r"([(\[¿¡«]) ", r"\1", s)
    return s


def read_conllu_docs(path, doc_of):
    """Agrupa las oraciones (# text = ...) de un CoNLL-U en documentos."""
    docs, cur_doc, newdoc = {}, None, None
    for line in open(path, encoding="utf-8"):
        if line.startswith("# newdoc id ="):
            newdoc = line.split("=", 1)[1].strip()
        elif line.startswith("# sent_id ="):
            cur_doc = doc_of(line.split("=", 1)[1].strip(), newdoc)
        elif line.startswith("# text ="):
            docs.setdefault(cur_doc, []).append(line.split("=", 1)[1].strip())
    return {k: " ".join(v) for k, v in docs.items()}


def parse_generated(path):
    """Archivo con bloques '### <id>' seguidos del texto."""
    if not os.path.exists(path):
        return {}
    out, cur, buf = {}, None, []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^###\s+(\S+)\s*$", line)
        if m:
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1), []
        elif cur:
            buf.append(line.rstrip("\n"))
    if cur:
        out[cur] = "\n".join(buf).strip()
    return {k: v for k, v in out.items() if len(v.split()) >= 8}


def load_docs(paths=None):
    """Devuelve una lista de dicts {text, y (1 = IA), source, group}."""
    p = dict(DEFAULTS, **(paths or {}))
    docs = []

    def add(text, y, source, group):
        text = text.strip()
        if len(text.split()) >= 8:
            docs.append({"text": text, "y": y, "source": source, "group": group})

    # AuTexTification (IberLEF 2023), subtarea 1: humanos frente a GPT-3 y BLOOM.
    df = pd.read_csv(f"{p['data']}/AUTEXTIFICATION/subtask_1/es/train.tsv", sep="\t")
    seen = set()
    for r in df.itertuples():
        add(r.text, int(r.label == "generated"), "autext", f"autext-es-{r.id}")
        seen.add(r.text.strip())
    # Subtarea 2: más textos generados (seis modelos); sin repetir los de la subtarea 1.
    df2 = pd.read_csv(f"{p['data']}/AUTEXTIFICATION/subtask_2/es/train.tsv", sep="\t")
    for r in df2.itertuples():
        if r.text.strip() not in seen:
            add(r.text, 1, "autext2", f"autext2-es-{r.id}")
            seen.add(r.text.strip())

    # Europarl (debates parlamentarios) y CoNLL-2002 (noticias de la agencia EFE): humano formal.
    for f in sorted(glob.glob(f"{p['data']}/europarl_raw/spanish/*.es")):
        lines = [detok(l.strip()) for l in open(f, encoding="utf-8", errors="ignore") if l.strip()]
        for k in range(0, len(lines), 12):  # documentos de ~12 intervenciones/oraciones
            add("\n".join(lines[k:k + 12]), 0, "europarl", f"ep-{os.path.basename(f)}")
    for split in ("esp.train", "esp.testa", "esp.testb"):
        sent, sents = [], []
        for line in open(f"{p['data']}/conll2002/{split}", encoding="latin-1"):
            line = line.strip()
            if not line:
                if sent:
                    sents.append(detok(" ".join(sent)))
                sent = []
            elif not line.startswith("-DOCSTART-"):
                sent.append(line.split(" ")[0])
        sents = [s for s in sents if len(s.split()) > 3]
        for k in range(0, len(sents), 10):
            add("\n".join(sents[k:k + 10]), 0, "efe", f"efe-{split}-{k // 100}")

    # AnCora (prensa) y GSD (textos web), Universal Dependencies.
    for f in sorted(glob.glob(f"{p['ancora']}/*.conllu")):
        for d, t in read_conllu_docs(f, lambda sid, nd: nd or sid.rsplit("-s", 1)[0]).items():
            add(t, 0, "ancora", f"ancora-{d}")
    # GSD no marca dónde empieza cada página web: se agrupan 6 oraciones consecutivas.
    for f in sorted(glob.glob(f"{p['gsd']}/*.conllu")):
        sents = [l.split("=", 1)[1].strip() for l in open(f, encoding="utf-8") if l.startswith("# text =")]
        for k in range(0, len(sents), 6):
            add(" ".join(sents[k:k + 6]), 0, "gsd", f"gsd-{os.path.basename(f)}-{k // 60}")

    # Spanish Fake News Corpus: noticias reales y falsas, todas escritas por personas (2018-2021).
    for f in ("train", "development", "test"):
        d = pd.read_excel(f"{p['fakenews']}/{f}.xlsx")
        d.columns = [str(c).lower() for c in d.columns]
        for i, r in d.iterrows():
            add(str(r["text"]), 0, "fakenews", f"fn-{f}-{i}")

    # COWS-L2H: redacciones de estudiantes universitarios de español (L2 y de herencia), sin corregir.
    for f in sorted(glob.glob(f"{p['cows']}/*/*/essays/*.txt")):
        add(open(f, encoding="utf-8", errors="ignore").read(), 0, "cows", "cows-" + "-".join(f.split("/")[-4:]))

    # IA actual: textos escritos para este proyecto con asistentes (Haiku, Sonnet, Opus y el conjunto inicial).
    es_ai = [t.strip() for t in open(os.path.join(HERE, "data", "es_ia_moderno.txt"), encoding="utf-8").read().split("\n===\n") if t.strip()]
    for i, t in enumerate(es_ai):
        add(t, 1, "es-ia-moderno", f"esai-{i}")
    for gid, t in parse_generated(p["gen"]).items():
        add(t, 1, "ia-generado", f"gen-{gid}")
    return docs


def is_test(group, frozen):
    """Partición fija: los grupos congelados en test_groups.json, los textos generados de prueba (b*)
    y un 15 % fijo (por hash) de las fuentes nuevas."""
    if group in frozen:
        return True
    if group.startswith(("autext-es-", "ep-", "esai-")):
        return False  # su partición ya está fijada por test_groups.json
    if group.startswith("gen-"):
        return group.startswith("gen-b")
    return zlib.crc32(group.encode()) % 100 < 15


def frozen_groups():
    return set(json.load(open(os.path.join(HERE, "test_groups.json"))))
