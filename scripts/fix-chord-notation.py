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
TOKEN_RE = re.compile(r"(?<![A-Za-z0-9#b/])" + CHORD + r"(?![A-Za-z0-9#b/])")


def is_candidate(stripped: str) -> bool:
    scrubbed = re.sub(r"\[[^\]]*\]|\{[^}]*\}|`[^`]*`", " ", stripped)
    if PAREN_RE.findall(scrubbed):
        return True
    plain = re.sub(r"[*_\\]", "", scrubbed).strip()
    tokens = [tok for tok in re.split(r"[\s|/-]+", plain.replace(":", " ")) if tok]
    return bool(SEQUENCE_RE.match(plain)) and any(
        CHORD_RE.match(tok) for tok in tokens if tok.lower() not in SKIP_WORDS
    )


def looks_like_ascii_tab(stripped: str) -> bool:
    plain = stripped.lstrip("*_")
    return bool(re.match(r"^[eBGDAE]\s*[-|]", plain)) or "-----" in stripped


def transform_segment(segment: str) -> str:
    segment = PAREN_RE.sub(lambda m: f"[{m.group(1)}]", segment)
    return TOKEN_RE.sub(lambda m: f"[{m.group(0)}]", segment)


def transform_line(line: str) -> str:
    out = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch in "[{`":
            close = {"[": "]", "{": "}", "`": "`"}[ch]
            j = line.find(close, i + 1)
            if j == -1:
                out.append(transform_segment(line[i:]))
                break
            out.append(line[i : j + 1])
            i = j + 1
            continue
        j = i + 1
        while j < len(line) and line[j] not in "[{`":
            j += 1
        out.append(transform_segment(line[i:j]))
        i = j
    return "".join(out)


changed = []
for path in sorted(Path("charts").glob("*.md")):
    lines = path.read_text().splitlines(keepends=True)
    in_frontmatter = False
    in_fence = False
    new_lines = []
    file_changed = False
    for line_no, line in enumerate(lines, 1):
        body = line.rstrip("\n")
        newline = line[len(body) :]
        stripped = body.strip()
        if line_no == 1 and stripped == "---":
            in_frontmatter = True
            new_lines.append(line)
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            new_lines.append(line)
            continue
        if stripped.startswith("```"):
            in_fence = not in_fence
            new_lines.append(line)
            continue
        if (
            in_fence
            or not stripped
            or stripped.startswith("#")
            or stripped.startswith("|")
            or looks_like_ascii_tab(stripped)
            or not is_candidate(stripped)
        ):
            new_lines.append(line)
            continue
        transformed = transform_line(body)
        if transformed != body:
            changed.append((path, line_no, body, transformed))
            file_changed = True
            new_lines.append(transformed + newline)
        else:
            new_lines.append(line)
    if file_changed:
        path.write_text("".join(new_lines))

for path, line_no, before, after in changed:
    print(f"{path}:{line_no}: {before} -> {after}")
print(f"TOTAL {len(changed)}")
