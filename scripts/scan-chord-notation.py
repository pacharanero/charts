import re
from pathlib import Path

CHORD = r"[A-G][b#]?(?:m|maj|min|dim|aug|sus|add|[0-9+#°ø-]|/[A-G][b#]?)*"
CHORD_RE = re.compile(r"^" + CHORD + r"$")
PAREN_RE = re.compile(r"\((" + CHORD + r")\)")
SEQUENCE_RE = re.compile(
    r"^(?:\*+)?(?:intro|verse|chorus|bridge|solo|outro|middle|pre-chorus|tag|riff)?(?:\*+)?[: ]*"
    r"(" + CHORD + r"(?:\s*(?:/|\||-)?\s*" + CHORD + r"|\s+x\s*\d+)*)"
    r"\s*(?:\*+)?\s*$",
    re.I,
)
SKIP_WORDS = {
    "intro",
    "verse",
    "chorus",
    "bridge",
    "solo",
    "outro",
    "middle",
    "pre",
    "tag",
    "riff",
    "x",
}

hits = []
for path in sorted(Path("charts").glob("*.md")):
    in_frontmatter = False
    in_fence = False
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if line_no == 1 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            continue
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if (
            in_fence
            or not stripped
            or stripped.startswith("#")
            or stripped.startswith("|")
        ):
            continue
        scrubbed = re.sub(r"\[[^\]]*\]|\{[^}]*\}|`[^`]*`", " ", stripped)
        if PAREN_RE.findall(scrubbed):
            hits.append((path, line_no, "paren", stripped))
        plain = re.sub(r"[*_\\]", "", scrubbed).strip()
        tokens = [tok for tok in re.split(r"[\s|/-]+", plain.replace(":", " ")) if tok]
        if SEQUENCE_RE.match(plain) and any(
            CHORD_RE.match(tok) for tok in tokens if tok.lower() not in SKIP_WORDS
        ):
            hits.append((path, line_no, "bare-seq", stripped))

for path, line_no, kind, text in hits:
    print(f"{path}:{line_no}:{kind}: {text}")
print(f"TOTAL {len(hits)}")
