#!/usr/bin/env python3
"""Checks that every field in the content files is editable in /admin (Decap drops unknown fields when saving)."""
import glob, re
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parent.parent
cfg = yaml.safe_load(open(ROOT / "static/admin/config.yml"))
def fieldmap(fields):
    out = {}
    for f in fields:
        if f["widget"] == "object": out[f["name"]] = fieldmap(f["fields"])
        elif f["widget"] == "list" and "fields" in f: out[f["name"]] = [fieldmap(f["fields"])]
        else: out[f["name"]] = None
    return out
def check(data, fm, path):
    probs = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k not in fm: probs.append(f"{path}.{k}"); continue
            sub = fm[k]
            if isinstance(sub, dict): probs += check(v, sub, f"{path}.{k}")
            elif isinstance(sub, list) and isinstance(v, list):
                for i, it in enumerate(v): probs += check(it, sub[0], f"{path}.{k}[{i}]")
    return probs
def load(p):
    raw = open(p, encoding="utf-8").read()
    if p.endswith(".md"):
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S); d = yaml.safe_load(m.group(1)); d["body"] = m.group(2); return d
    return yaml.safe_load(raw)
problems, files = [], 0
for col in cfg["collections"]:
    if "files" in col:
        for f in col["files"]:
            files += 1; problems += check(load(str(ROOT / f["file"])), fieldmap(f["fields"]), f["file"])
    else:
        for p in sorted(glob.glob(str(ROOT / col["folder"]) + "/*")):
            files += 1; problems += check(load(p), fieldmap(col["fields"]), p.replace(str(ROOT) + "/", ""))
print("\n".join(problems) if problems else f"OK: all fields in {files} content files are editable in /admin")
