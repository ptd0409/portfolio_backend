from __future__ import annotations

import re
import unicodedata

def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text[:80]

def normalize_tag_slugs(items: list[str]) -> list[str]:
    out: list[str] = []
    seen = set()
    for x in items:
        s = (x or "").strip()
        if not s:
            continue
        slug = slugify(s)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        out.append(slug)
    return out