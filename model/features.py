"""Extracción de rasgos de Lupa. Debe coincidir exactamente con la versión JS de index.html."""
import math
import unicodedata

import regex as re

D_BITS = 18
D = 1 << D_BITS
TOK = re.compile(r"[\p{L}\p{M}\p{N}]+(?:'[\p{L}\p{M}]+)*|[^\s\p{L}\p{M}\p{N}]")
HAS_WORD = re.compile(r"[\p{L}\p{M}\p{N}]")
SENT_SPLIT = re.compile(r"[.!?…]+|\n+")
UPPER = re.compile(r"\p{Lu}")
LETTER = re.compile(r"\p{L}")
DIGIT = re.compile(r"\p{N}")
FIRST_PERSON = {"i", "me", "my", "mine", "i'm", "i've", "i'd", "i'll", "yo", "mi", "mis", "conmigo", "nosotros", "nosotras", "nuestro", "nuestra"}
TRANSITIONS = {"además", "asimismo", "sin", "adicionalmente", "igualmente", "finalmente", "furthermore", "moreover",
               "additionally", "however", "overall", "ultimately", "consequently", "therefore", "thus", "notably", "importantly"}
N_DENSE = 16


def normalize(text):
    t = unicodedata.normalize("NFC", text)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("«", '"'),
                 ("»", '"'), (" ", " "), ("﻿", ""), ("\r", "")):
        t = t.replace(a, b)
    return t


def fnv(s):
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def hashed(tokens):
    counts = {}

    def add(f):
        i = fnv(f) & (D - 1)
        counts[i] = counts.get(i, 0) + 1

    prev = None
    for t in tokens:
        add("u" + t)
        if prev is not None:
            add("b" + prev + "\x01" + t)
        prev = t
        if HAS_WORD.search(t) and len(t) <= 30:
            w = "<" + t + ">"
            for n in (3, 4, 5):
                for k in range(len(w) - n + 1):
                    add("c" + w[k:k + n])
    vals = {i: math.log1p(c) for i, c in counts.items()}
    norm = math.sqrt(sum(v * v for v in vals.values())) or 1.0
    return {i: v / norm for i, v in vals.items()}


def dense(text, tokens):
    words = [t for t in tokens if HAS_WORD.search(t)]
    n = len(words) or 1
    sents = [s for s in SENT_SPLIT.split(text) if HAS_WORD.search(s)]
    lens = [sum(1 for t in TOK.findall(s) if HAS_WORD.search(t)) for s in sents] or [n]
    mean = sum(lens) / len(lens)
    sd = math.sqrt(sum((x - mean) ** 2 for x in lens) / len(lens))
    nchar = len(text) or 1
    letters = len(LETTER.findall(text)) or 1
    cnt = {}
    for t in tokens:
        cnt[t] = cnt.get(t, 0) + 1
    first100 = words[:100]
    starts = 0
    for s in sents:
        ws = [t for t in TOK.findall(s.lower()) if HAS_WORD.search(t)]
        if ws and ws[0] in TRANSITIONS:
            starts += 1
    return [
        math.log1p(len(words)) / 8,
        mean / 30,
        sd / mean if mean else 0.0,
        cnt.get(",", 0) / n * 10,
        (cnt.get(";", 0) + cnt.get(":", 0)) / n * 10,
        (cnt.get("?", 0) + cnt.get("!", 0) + cnt.get("¿", 0) + cnt.get("¡", 0)) / len(lens),
        (cnt.get("(", 0) + cnt.get('"', 0)) / n * 10,
        (cnt.get("-", 0) + cnt.get("—", 0) + cnt.get("–", 0)) / n * 10,
        len(DIGIT.findall(text)) / nchar * 10,
        len(UPPER.findall(text)) / letters,
        sum(len(w) for w in words) / n / 10,
        len(set(first100)) / (len(first100) or 1),
        text.count("\n") / n * 10,
        sum(1 for w in words if "'" in w) / n * 10,
        sum(1 for w in words if w.lower() in FIRST_PERSON) / n * 10,
        starts / len(lens),
    ]


def featurize(text):
    t = normalize(text)
    tokens = TOK.findall(t.lower())
    return hashed(tokens), dense(t, TOK.findall(t))
