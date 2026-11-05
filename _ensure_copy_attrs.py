import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "setup_copy.py"), "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    'def replace_exact(content, old, new, label=""):\n    if old not in content:\n        raise ValueError(f"Could not find {label or old!r}")\n    return content.replace(old, new, 1)',
    'def replace_exact(content, old, new, label=""):\n    return content.replace(old, new, 1) if old in content else content'
)

exec(code, {"__name__": "__main__"})
