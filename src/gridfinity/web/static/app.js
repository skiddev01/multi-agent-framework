"use strict";

const els = {
  dropzone: document.getElementById("dropzone"),
  imageInput: document.getElementById("imageInput"),
  preview: document.getElementById("preview"),
  dropPrompt: document.getElementById("dropPrompt"),
  widthUnits: document.getElementById("widthUnits"),
  depthUnits: document.getElementById("depthUnits"),
  researchToggle: document.getElementById("researchToggle"),
  analyzeBtn: document.getElementById("analyzeBtn"),
  status: document.getElementById("status"),
  emptyState: document.getElementById("emptyState"),
  results: document.getElementById("results"),
  notes: document.getElementById("notes"),
  cards: document.getElementById("cards"),
  canvas: document.getElementById("layoutCanvas"),
  layoutMeta: document.getElementById("layoutMeta"),
  visionBadge: document.getElementById("visionBadge"),
};

let selectedFile = null;

// ---- Vision status badge ----------------------------------------------------
fetch("/api/health")
  .then((r) => r.json())
  .then((h) => {
    if (h.vision_enabled) {
      els.visionBadge.textContent = "Claude vision: on";
      els.visionBadge.className = "badge badge-good";
    } else {
      els.visionBadge.textContent = "Demo mode (no API key)";
      els.visionBadge.className = "badge badge-muted";
    }
  })
  .catch(() => {
    els.visionBadge.textContent = "offline";
  });

// ---- File selection & drag-drop --------------------------------------------
function setFile(file) {
  if (!file || !file.type.startsWith("image/")) return;
  selectedFile = file;
  const url = URL.createObjectURL(file);
  els.preview.src = url;
  els.preview.hidden = false;
  els.dropPrompt.hidden = true;
}

els.imageInput.addEventListener("change", (e) => setFile(e.target.files[0]));

["dragenter", "dragover"].forEach((ev) =>
  els.dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    els.dropzone.classList.add("dragover");
  })
);
["dragleave", "drop"].forEach((ev) =>
  els.dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    els.dropzone.classList.remove("dragover");
  })
);
els.dropzone.addEventListener("drop", (e) => {
  if (e.dataTransfer.files.length) setFile(e.dataTransfer.files[0]);
});

// ---- Analyze ----------------------------------------------------------------
els.analyzeBtn.addEventListener("click", analyze);

async function analyze() {
  const width = parseInt(els.widthUnits.value, 10);
  const depth = parseInt(els.depthUnits.value, 10);
  if (!width || !depth || width < 1 || depth < 1) {
    els.status.textContent = "Please enter a valid grid size (at least 1 x 1).";
    return;
  }

  const form = new FormData();
  form.append("width_units", width);
  form.append("depth_units", depth);
  form.append("research", els.researchToggle.checked);
  if (selectedFile) form.append("image", selectedFile);

  els.analyzeBtn.disabled = true;
  els.status.textContent = selectedFile
    ? "Analyzing photo and researching bins…"
    : "Running demo (no photo)…";

  try {
    const res = await fetch("/api/plan", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Request failed");
    render(data);
    els.status.textContent = "Done.";
  } catch (err) {
    els.status.textContent = "Error: " + err.message;
  } finally {
    els.analyzeBtn.disabled = false;
  }
}

// ---- Render -----------------------------------------------------------------
function render(data) {
  els.emptyState.hidden = true;
  els.results.hidden = false;

  els.notes.innerHTML = "";
  (data.notes || []).forEach((n) => {
    const div = document.createElement("div");
    div.className = "note";
    div.textContent = n;
    els.notes.appendChild(div);
  });

  renderLayout(data.layout);

  els.cards.innerHTML = "";
  (data.recommendations || []).forEach((rec) => {
    els.cards.appendChild(renderCard(rec));
  });
}

function renderCard(rec) {
  const card = document.createElement("div");
  card.className = "card";

  const head = document.createElement("div");
  head.className = "card-head";
  const title = document.createElement("span");
  title.className = "card-title";
  title.textContent = `${rec.group_name} (${rec.item_count})`;
  const tag = document.createElement("span");
  tag.className = "bin-tag";
  tag.textContent = rec.bin_label;
  head.append(title, tag);
  card.appendChild(head);

  const meta = document.createElement("div");
  meta.className = "card-meta";
  meta.textContent =
    `${rec.category} · usable ${rec.usable_width_mm} × ` +
    `${rec.usable_depth_mm} × ${rec.usable_height_mm} mm`;
  card.appendChild(meta);

  if (rec.rationale) {
    const r = document.createElement("p");
    r.className = "rationale";
    r.textContent = rec.rationale;
    card.appendChild(r);
  }

  if (rec.fit_warning) {
    const w = document.createElement("div");
    w.className = "fit-warn";
    w.textContent = "⚠ " + rec.fit_warning;
    card.appendChild(w);
  }

  if (rec.printable_models && rec.printable_models.length) {
    const ul = document.createElement("ul");
    ul.className = "models";
    rec.printable_models.forEach((m) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = m.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = m.title;
      li.appendChild(a);
      if (m.source) {
        const s = document.createElement("span");
        s.className = "src";
        s.textContent = " · " + m.source;
        li.appendChild(s);
      }
      ul.appendChild(li);
    });
    card.appendChild(ul);
  }

  return card;
}

// ---- Layout visualization ---------------------------------------------------
const PALETTE = [
  "#2f6feb", "#1f9d57", "#c9760f", "#8b5cf6",
  "#e0518a", "#0ea5a5", "#d4451f", "#5b6470",
];

function renderLayout(layout) {
  const canvas = els.canvas;
  const ctx = canvas.getContext("2d");
  if (!layout) return;

  const W = layout.grid_width_units;
  const D = layout.grid_depth_units;
  const cell = Math.max(24, Math.min(80, Math.floor(480 / Math.max(W, 1))));
  canvas.width = W * cell + 1;
  canvas.height = D * cell + 1;

  const styles = getComputedStyle(document.body);
  const cellColor = styles.getPropertyValue("--cell") || "#eef1f6";
  const border = styles.getPropertyValue("--border") || "#e2e5ea";

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Empty grid
  ctx.fillStyle = cellColor.trim();
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = border.trim();
  ctx.lineWidth = 1;
  for (let x = 0; x <= W; x++) {
    ctx.beginPath();
    ctx.moveTo(x * cell + 0.5, 0);
    ctx.lineTo(x * cell + 0.5, D * cell);
    ctx.stroke();
  }
  for (let y = 0; y <= D; y++) {
    ctx.beginPath();
    ctx.moveTo(0, y * cell + 0.5);
    ctx.lineTo(W * cell, y * cell + 0.5);
    ctx.stroke();
  }

  // Placed bins
  (layout.placed || []).forEach((p, i) => {
    const color = PALETTE[i % PALETTE.length];
    const px = p.x * cell;
    const py = p.y * cell;
    const pw = p.width_units * cell;
    const ph = p.depth_units * cell;
    ctx.fillStyle = hexToRgba(color, 0.22);
    ctx.fillRect(px + 2, py + 2, pw - 3, ph - 3);
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.strokeRect(px + 2, py + 2, pw - 3, ph - 3);

    ctx.fillStyle = color;
    ctx.font = "600 11px -apple-system, sans-serif";
    ctx.textBaseline = "top";
    wrapLabel(ctx, p.group_name, px + 6, py + 6, pw - 10);
    ctx.fillStyle = color;
    ctx.font = "10px ui-monospace, monospace";
    ctx.fillText(p.bin_label, px + 6, py + ph - 16);
  });

  els.layoutMeta.textContent =
    `${W} × ${D} grid · ${layout.placed.length} bin(s) placed · ` +
    `${layout.free_cells ?? free(layout)} free cell(s)` +
    (layout.unplaced_groups && layout.unplaced_groups.length
      ? ` · ${layout.unplaced_groups.length} did not fit`
      : "");
}

function free(layout) {
  const total = layout.grid_width_units * layout.grid_depth_units;
  const used = (layout.placed || []).reduce(
    (s, p) => s + p.width_units * p.depth_units, 0);
  return total - used;
}

function wrapLabel(ctx, text, x, y, maxWidth) {
  const words = text.split(" ");
  let line = "";
  let yy = y;
  for (const word of words) {
    const test = line ? line + " " + word : word;
    if (ctx.measureText(test).width > maxWidth && line) {
      ctx.fillText(line, x, yy);
      line = word;
      yy += 13;
    } else {
      line = test;
    }
  }
  if (line) ctx.fillText(line, x, yy);
}

function hexToRgba(hex, alpha) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
}
