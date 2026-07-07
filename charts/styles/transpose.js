/* MBCS transposer: adds a +/- semitone control and rewrites [chord] and
 * {octaved} tokens in place. Leaves section headings, performance directions,
 * chord voicings, and tab blocks alone. */
(function () {
  "use strict";

  const ITALIC_STORAGE_KEY = "mbcs-italic";
  const ZOOM_STORAGE_KEY = "mbcs-zoom";
  const DEFAULT_ZOOM = 100;
  const MIN_ZOOM = 75;
  const MAX_ZOOM = 150;
  const ZOOM_STEP = 5;

  function readItalicPref() {
    try {
      const v = localStorage.getItem(ITALIC_STORAGE_KEY);
      return v === null ? true : v === "on";
    } catch (_) {
      return true;
    }
  }
  function writeItalicPref(on) {
    try {
      localStorage.setItem(ITALIC_STORAGE_KEY, on ? "on" : "off");
    } catch (_) {}
  }
  function applyItalicPref(on) {
    document.documentElement.setAttribute(
      "data-mbcs-italic",
      on ? "on" : "off",
    );
  }
  function readZoomPref() {
    try {
      const raw = parseInt(localStorage.getItem(ZOOM_STORAGE_KEY), 10);
      if (Number.isFinite(raw))
        return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, raw));
    } catch (_) {}
    return DEFAULT_ZOOM;
  }
  function writeZoomPref(zoom) {
    try {
      localStorage.setItem(ZOOM_STORAGE_KEY, String(zoom));
    } catch (_) {}
  }
  function applyZoomPref(zoom) {
    document.documentElement.style.setProperty(
      "--mbcs-chart-font-size",
      `${0.8 * (zoom / 100)}rem`,
    );
    document.querySelectorAll(".md-content__inner").forEach((content) => {
      content.style.fontSize = `${0.8 * (zoom / 100)}rem`;
    });
  }
  // Apply stored preferences ASAP so body text doesn't flash in the wrong state.
  applyItalicPref(readItalicPref());
  applyZoomPref(readZoomPref());

  const SHARPS = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
  ];
  const FLATS = [
    "C",
    "Db",
    "D",
    "Eb",
    "E",
    "F",
    "Gb",
    "G",
    "Ab",
    "A",
    "Bb",
    "B",
  ];
  const NOTE_INDEX = {
    C: 0,
    "C#": 1,
    Db: 1,
    D: 2,
    "D#": 3,
    Eb: 3,
    E: 4,
    F: 5,
    "F#": 6,
    Gb: 6,
    G: 7,
    "G#": 8,
    Ab: 8,
    A: 9,
    "A#": 10,
    Bb: 10,
    B: 11,
  };

  function transposeNote(note, semitones, preferFlat) {
    const idx = NOTE_INDEX[note];
    if (idx === undefined) return note;
    const newIdx = (((idx + semitones) % 12) + 12) % 12;
    return preferFlat ? FLATS[newIdx] : SHARPS[newIdx];
  }

  // Is this bracket content a chord (starts with capital A-G)?
  const CHORD_RE = /^[A-G][b#]?/;
  // Is this bracket content a lowercase note run? "g f# e" / "bb a g"
  const NOTE_RUN_RE = /^[a-g](?:[b#])?(?:\s+[a-g](?:[b#])?)+$/;
  // Is this a single note (curly-brace content like "Eb" or "F")?
  const SINGLE_NOTE_RE = /^[A-Ga-g][b#]?$/;

  function transposeChord(chord, semitones) {
    // Pull the root note (and optional accidental) off the front.
    const m = chord.match(/^([A-G])([b#])?(.*)$/);
    if (!m) return chord;
    const [, root, acc, rest] = m;
    const noteName = root + (acc || "");
    const preferFlat = acc === "b";
    const newRoot = transposeNote(noteName, semitones, preferFlat);
    // Handle slash bass: Dm7/F#
    const restRewritten = rest.replace(
      /\/([A-G])([b#])?/,
      (_, r, a) => "/" + transposeNote(r + (a || ""), semitones, a === "b"),
    );
    return newRoot + restRewritten;
  }

  function transposeNoteRun(run, semitones) {
    return run.replace(/([a-g])([b#])?/g, (_, n, acc) => {
      const upper = n.toUpperCase() + (acc || "");
      const preferFlat = acc === "b";
      return transposeNote(upper, semitones, preferFlat).toLowerCase();
    });
  }

  function transposeSingleNote(note, semitones) {
    const isLower = note[0] >= "a" && note[0] <= "g";
    const upper = note[0].toUpperCase() + (note.slice(1) || "");
    const preferFlat = note.includes("b");
    const result = transposeNote(upper, semitones, preferFlat);
    return isLower ? result.toLowerCase() : result;
  }

  function classifyAndTranspose(inner, semitones) {
    const trimmed = inner.trim();
    if (CHORD_RE.test(trimmed)) return transposeChord(trimmed, semitones);
    if (NOTE_RUN_RE.test(trimmed)) return transposeNoteRun(trimmed, semitones);
    if (SINGLE_NOTE_RE.test(trimmed))
      return transposeSingleNote(trimmed, semitones);
    return null;
  }

  function wrapChartTokens(root) {
    // Walk visible text nodes in the rendered content, find [X] and {X}, and
    // wrap the matching ones in <span class="mbcs-token">.
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(n) {
        if (!n.nodeValue || !/[\[{]/.test(n.nodeValue))
          return NodeFilter.FILTER_REJECT;
        const parent = n.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        if (
          parent.closest(
            "pre, code, h1, h2, h3, h4, h5, h6, .mbcs-token, #mbcs-transpose",
          )
        ) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    });

    const texts = [];
    let n;
    while ((n = walker.nextNode())) texts.push(n);

    const RE = /\[([^\]]+)\]|\{([^}]+)\}/g;
    for (const node of texts) {
      const text = node.nodeValue;
      RE.lastIndex = 0;
      if (!RE.test(text)) continue;
      RE.lastIndex = 0;
      const frag = document.createDocumentFragment();
      let last = 0;
      let m;
      while ((m = RE.exec(text)) !== null) {
        if (m.index > last)
          frag.appendChild(document.createTextNode(text.slice(last, m.index)));
        const isSquare = m[1] !== undefined;
        const inner = isSquare ? m[1] : m[2];
        const open = isSquare ? "[" : "{";
        const close = isSquare ? "]" : "}";
        const transposed = classifyAndTranspose(inner, 0);
        if (transposed !== null) {
          const span = document.createElement("span");
          span.className = "mbcs-token";
          span.dataset.mbcsOriginal = inner;
          span.dataset.mbcsBracket = isSquare ? "square" : "curly";
          span.textContent = open + inner + close;
          frag.appendChild(span);
        } else {
          frag.appendChild(document.createTextNode(m[0]));
        }
        last = m.index + m[0].length;
      }
      if (last < text.length)
        frag.appendChild(document.createTextNode(text.slice(last)));
      node.parentNode.replaceChild(frag, node);
    }
  }

  function looksLikeTabBlock(text) {
    return /^[a-gA-G][#b]?\s*\|/m.test(text) && /\d/.test(text);
  }

  function registerTabBlocks(root) {
    root.querySelectorAll("pre code").forEach((code) => {
      if (code.dataset.mbcsTabOriginal || !looksLikeTabBlock(code.textContent))
        return;
      code.dataset.mbcsTabOriginal = code.textContent;
      code.classList.add("mbcs-tab-block");
    });
  }

  function transposeTabBlocks(semitones) {
    let hasNegativeFrets = false;
    document.querySelectorAll("pre code.mbcs-tab-block").forEach((code) => {
      const original = code.dataset.mbcsTabOriginal || code.textContent;
      code.textContent = original.replace(/\d+/g, (raw) => {
        const fret = parseInt(raw, 10) + semitones;
        if (fret < 0) {
          hasNegativeFrets = true;
          return "!";
        }
        return String(fret);
      });
      code.classList.toggle("mbcs-tab-needs-arrangement", hasNegativeFrets);
    });
    document.querySelectorAll(".mbcs-tab-warning").forEach((warning) => {
      warning.hidden = !hasNegativeFrets;
    });
  }

  function applyTransposition(semitones) {
    document.querySelectorAll(".mbcs-token").forEach((el) => {
      const inner = el.dataset.mbcsOriginal;
      const open = el.dataset.mbcsBracket === "square" ? "[" : "{";
      const close = el.dataset.mbcsBracket === "square" ? "]" : "}";
      const result =
        semitones === 0
          ? inner
          : (classifyAndTranspose(inner, semitones) ?? inner);
      el.textContent = open + result + close;
    });
    transposeTabBlocks(semitones);
  }

  function addControl(root) {
    // Remove any pre-existing control from prior navigation so we can rebuild
    // it. Zensical keeps some page chrome around during instant navigation but
    // the chart content changes, so we need to re-evaluate per page.
    const existing = document.getElementById("mbcs-transpose");
    if (existing) existing.remove();
    const hasTransposableContent =
      !!document.querySelector(".mbcs-token") ||
      !!document.querySelector(".mbcs-tab-block");

    const ctl = document.createElement("aside");
    ctl.id = "mbcs-transpose";
    ctl.className = "mbcs-tools";
    ctl.setAttribute("aria-label", "Chart tools");
    ctl.innerHTML = `
      <div class="mbcs-tool-group" aria-label="Transpose" data-mbcs-transpose-available="${hasTransposableContent ? "true" : "false"}">
        <span class="mbcs-t-label">Transpose</span>
        <button type="button" class="mbcs-t-btn" data-dir="-1" title="Down one semitone" aria-label="Transpose down one semitone">−</button>
        <span class="mbcs-t-val" aria-live="polite">0</span>
        <button type="button" class="mbcs-t-btn" data-dir="1" title="Up one semitone" aria-label="Transpose up one semitone">+</button>
        <button type="button" class="mbcs-t-btn mbcs-t-reset" title="Reset transposition" aria-label="Reset transposition">↺</button>
      </div>
      <div class="mbcs-tool-group" aria-label="Zoom">
        <span class="mbcs-t-label">Zoom</span>
        <button type="button" class="mbcs-t-btn mbcs-zoom-out" title="Zoom out" aria-label="Zoom out">−</button>
        <span class="mbcs-zoom-val" aria-live="polite">100%</span>
        <button type="button" class="mbcs-t-btn mbcs-zoom-in" title="Zoom in" aria-label="Zoom in">+</button>
        <button type="button" class="mbcs-t-btn mbcs-zoom-reset" title="Reset zoom" aria-label="Reset zoom">↺</button>
      </div>
      <div class="mbcs-tool-group mbcs-tool-group--compact" aria-label="Display">
        <button type="button" class="mbcs-t-btn mbcs-t-italic" title="Toggle italic body text" aria-pressed="false">I</button>
        <button type="button" class="mbcs-t-btn mbcs-t-print" title="Print (A4, single page)" aria-label="Print">🖨</button>
      </div>
      <p class="mbcs-tab-warning" hidden>Tab contains fret(s) below 0: rearrange by hand.</p>
    `;

    document.body.appendChild(ctl);

    if (!hasTransposableContent) {
      ctl.querySelectorAll("[data-dir], .mbcs-t-reset").forEach((btn) => {
        btn.disabled = true;
        btn.title = "No chords or tablature to transpose on this chart";
      });
    }

    let semitones = 0;
    const val = ctl.querySelector(".mbcs-t-val");
    const update = () => {
      val.textContent = (semitones > 0 ? "+" : "") + semitones;
      applyTransposition(semitones);
    };
    if (hasTransposableContent) {
      ctl.querySelectorAll("[data-dir]").forEach((btn) => {
        btn.addEventListener("click", () => {
          semitones += parseInt(btn.dataset.dir, 10);
          if (semitones > 11) semitones -= 12;
          if (semitones < -11) semitones += 12;
          update();
        });
      });
      ctl.querySelector(".mbcs-t-reset").addEventListener("click", () => {
        semitones = 0;
        update();
      });
    }
    const zoomVal = ctl.querySelector(".mbcs-zoom-val");
    let zoom = readZoomPref();
    const syncZoom = () => {
      zoomVal.textContent = zoom + "%";
      applyZoomPref(zoom);
      writeZoomPref(zoom);
    };
    ctl.querySelector(".mbcs-zoom-out").addEventListener("click", () => {
      zoom = Math.max(MIN_ZOOM, zoom - ZOOM_STEP);
      syncZoom();
    });
    ctl.querySelector(".mbcs-zoom-in").addEventListener("click", () => {
      zoom = Math.min(MAX_ZOOM, zoom + ZOOM_STEP);
      syncZoom();
    });
    ctl.querySelector(".mbcs-zoom-reset").addEventListener("click", () => {
      zoom = DEFAULT_ZOOM;
      syncZoom();
    });
    syncZoom();

    const printBtn = ctl.querySelector(".mbcs-t-print");
    if (printBtn) printBtn.addEventListener("click", () => window.print());

    const italicBtn = ctl.querySelector(".mbcs-t-italic");
    if (italicBtn) {
      const syncItalicBtn = (on) => {
        italicBtn.setAttribute("aria-pressed", on ? "true" : "false");
        italicBtn.title = on
          ? "Italics on (click to turn off)"
          : "Italics off (click to turn on)";
      };
      syncItalicBtn(readItalicPref());
      italicBtn.addEventListener("click", () => {
        const next = !readItalicPref();
        writeItalicPref(next);
        applyItalicPref(next);
        syncItalicBtn(next);
      });
    }
    return ctl;
  }

  function init() {
    const root =
      document.querySelector(".md-content__inner") ||
      document.querySelector(".md-content") ||
      document.body;
    if (!root) return;
    // Avoid re-wrapping on instant-nav transitions
    if (!root.dataset.mbcsWrapped) {
      wrapChartTokens(root);
      registerTabBlocks(root);
      root.dataset.mbcsWrapped = "true";
    }
    applyZoomPref(readZoomPref());
    addControl(root);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Zensical instant navigation observable, if present.
  if (
    typeof window !== "undefined" &&
    typeof window.document$ !== "undefined" &&
    typeof window.document$.subscribe === "function"
  ) {
    window.document$.subscribe(init);
  }
})();
