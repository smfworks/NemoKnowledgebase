#!/usr/bin/env python3
"""Extract the first complete HTML fence from a one-shot content.md."""
import re
import sys
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
text = src.read_text()
m = re.search(r"```html\s*\n(.*?)```", text, re.S | re.I)
if not m:
    m = re.search(r"(<!DOCTYPE html>.*?</html>)", text, re.S | re.I)
if not m:
    raise SystemExit(f"no HTML fence or doctype found in {src}")
html = m.group(1).strip() + "\n"
if not html.lower().startswith("<!doctype html>"):
    raise SystemExit("extracted block is not a full HTML document")
if "</html>" not in html.lower():
    raise SystemExit("extracted HTML missing </html> — likely truncated")
dst.write_text(html)
print(f"wrote {dst} bytes={dst.stat().st_size} lines={html.count(chr(10))+1}")
