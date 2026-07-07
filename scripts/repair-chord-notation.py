import re
from pathlib import Path

for path in Path("charts").glob("*.md"):
    text = path.read_text()
    original = text
    while True:
        new = re.sub(r"\[\[([^\[\]]+)\]\]", r"[\1]", text)
        if new == text:
            break
        text = new
    text = re.sub(r"\*\*\(([A-G])♭\)\*\*", r"**[\1b]**", text)
    text = re.sub(r"\*\*\(([A-G])♯\)\*\*", r"**[\1#]**", text)
    text = re.sub(r"\(\[([A-G])\]♭\)", r"[\1b]", text)
    text = re.sub(r"\(\[([A-G])\]♯\)", r"[\1#]", text)
    text = text.replace("[Ab-]-[G]", "[Ab]--[G]")
    text = text.replace("[B][G] [D#7][B7]", "[B] [G] [D#7] [B7]")
    text = text.replace("[E][C] [Em][Cm] [B][G]", "[E] [C] [Em] [Cm] [B] [G]")
    text = text.replace(
        "[G7] / [E7] [Am] [E7] [Am] / [G] [C] [G] [C] / [B7] EmD [G] [D] [Gm] [D]",
        "[G7] / [E7] [Am] [E7] [Am] / [G] [C] [G] [C] / [B7] [Em] [D] [G] [D] [Gm] [D]",
    )
    if text != original:
        path.write_text(text)
        print(path)
