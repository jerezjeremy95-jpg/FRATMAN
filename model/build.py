"""Inserta los pesos entrenados (model/lupa-model.json) en la página y genera index.html."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "src", "index.src.html"), encoding="utf-8").read()
model = json.load(open(os.path.join(ROOT, "model", "lupa-model.json"), encoding="utf-8"))
blob = json.dumps(model, separators=(",", ":"), ensure_ascii=True).replace("</", "<\\/")
prompt = open(os.path.join(ROOT, "model", "claude_prompt.txt"), encoding="utf-8").read()
page = src.replace("__LUPA_MODEL__", blob).replace("__CLAUDE_PROMPT__", json.dumps(prompt, ensure_ascii=False).replace("</", "<\\/"))
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)
if len(sys.argv) > 1:  # versión sin envoltorio para publicar como artifact
    frag = "".join(l for l in page.splitlines(keepends=True) if "<!--wrap-->" not in l)
    open(sys.argv[1], "w", encoding="utf-8").write(frag)
print(f"index.html: {len(page) // 1024} KB")
