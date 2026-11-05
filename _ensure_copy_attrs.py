import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(r"C:\Users\dejtu\.gemini\antigravity\brain\33c048ca-d984-4f03-92b7-49c2c0c8fdcd\scratch\setup_copy.py", "r", encoding="utf-8") as f:
    code = f.read()

# Run setup_copy logic safely (ignoring already-instrumented replacements)
def safe_replace(content, old, new):
    if old in content:
        return content.replace(old, new, 1)
    return content

code = code.replace("def replace_exact(content, old, new, label=\"\"):\n    if old not in content:\n        raise ValueError(f\"Could not find {label or old!r}\")\n    return content.replace(old, new, 1)",
                    "def replace_exact(content, old, new, label=\"\"):\n    return content.replace(old, new, 1) if old in content else content")

exec(code, {"__name__": "__main__"})
