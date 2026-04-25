/**
 * wordclock.js — Web simulator frontend
 *
 * Evolved from the original JavaScript prototype by Enric Ballo.
 * Time logic and letter lookup are now handled by the FastAPI.
 * This file only manages the DOM and calls the API.
 */

const API = "";          // same origin as Flask
let currentLang = "english";

let numCols = 16;
let demoInterval = null;

// ── Helpers ────────────────────────────────────────────────────────

function getInputTime() {
  const h = parseInt(document.getElementById("hour-input").value);
  const m = parseInt(document.getElementById("min-input").value);
  return (!isNaN(h) && !isNaN(m)) ? { h, m } : null;
}

// ── Build the grid DOM ──────────────────────────────────────────────

async function initGrid() {
  const langSelect = document.getElementById("lang-select");
  if (langSelect) {
    currentLang = langSelect.value;
  }
  console.log(`[wordclock] Initializing grid for: ${currentLang}`);
  try {
    const res  = await fetch(`${API}/api/grid?lang=${currentLang}&t=${Date.now()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    numCols = data.cols;
    const panel = document.getElementById("word-clock");
    if (!panel) return;

    panel.innerHTML = "";
    panel.style.gridTemplateColumns = `repeat(${numCols}, 1fr)`;

    data.grid.forEach((row, r) => {
      row.forEach((char, c) => {
        const tile = document.createElement("div");
        tile.className   = "tile";
        tile.id          = `r${r}c${c}`;
        tile.textContent = char;
        panel.appendChild(tile);
      });
    });
  } catch (err) {
    console.error("[wordclock] Failed to init grid:", err);
  }
}

// ── Update the display ──────────────────────────────────────────────

async function updateClock(h, m) {
  const langSelect = document.getElementById("lang-select");
  if (langSelect) {
    currentLang = langSelect.value;
  }

  if (h === undefined || m === undefined) {
    const it = getInputTime();
    if (it) { h = it.h; m = it.m; }
  }

  const baseParams = (h !== undefined && m !== undefined)
    ? `lang=${currentLang}&h=${h}&m=${m}`
    : `lang=${currentLang}`;
  const params = `?${baseParams}&t=${Date.now()}`;

  console.log(`[wordclock] Updating clock: ${params}`);
  try {
    const res  = await fetch(`${API}/api/time${params}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (data.error) {
      console.error("[wordclock] API error:", data.error);
      return;
    }

    // Use placeholders for "Now" mode so the clock can keep ticking
    const hInput = document.getElementById("hour-input");
    const mInput = document.getElementById("min-input");
    if (hInput && hInput.value === "") {
        hInput.placeholder = String(data.hours).padStart(2, '0');
    }
    if (mInput && mInput.value === "") {
        mInput.placeholder = String(data.minutes).padStart(2, '0');
    }

    // Dim all tiles
    document.querySelectorAll(".tile").forEach(t => t.classList.remove("on"));

    // Light up the active ones
    data.coords.forEach(([row, col]) => {
      const tile = document.getElementById(`r${row}c${col}`);
      if (tile) tile.classList.add("on");
      else console.warn(`[wordclock] Tile not found: r${row}c${col}`);
    });

    document.getElementById("sentence").textContent = data.sentence;
  } catch (err) {
    console.error("[wordclock] Failed to update clock:", err);
  }
}

// ── Demo mode (port of the original JS demo()) ─────────────────────

function startDemo() {
  stopDemo();
  runDemo();
  demoInterval = setInterval(runDemo, 3000);
  document.getElementById("btn-demo").textContent = "Stop";
}

function stopDemo() {
  if (demoInterval !== null) {
    clearInterval(demoInterval);
    demoInterval = null;
    document.getElementById("btn-demo").textContent = "Demo";
  }
}

function runDemo() {
  const h = Math.floor(Math.random() * 24);
  const m = Math.floor(Math.random() * 12) * 5;   // multiples of 5
  // When in demo, we pass h/m explicitly to updateClock
  updateClock(h, m);
}

// ── Controls ────────────────────────────────────────────────────────

document.getElementById("btn-now").addEventListener("click", () => {
  stopDemo();
  const hInput = document.getElementById("hour-input");
  const mInput = document.getElementById("min-input");
  if (hInput) { hInput.value = ""; hInput.placeholder = "HH"; }
  if (mInput) { mInput.value = ""; mInput.placeholder = "MM"; }
  updateClock();
});

document.getElementById("btn-set").addEventListener("click", () => {
  stopDemo();
  const it = getInputTime();
  if (it) updateClock(it.h, it.m);
});

document.getElementById("btn-demo").addEventListener("click", () => {
  if (demoInterval !== null) stopDemo();
  else startDemo();
});

document.getElementById("lang-select").addEventListener("change", async (e) => {
  currentLang = e.target.value;
  console.log(`[wordclock] Language changed to: ${currentLang}`);
  
  // Wait for the grid to be fully initialized before updating the clock
  await initGrid();
  await updateClock();
});

["hour-input", "min-input"].forEach(id => {
  document.getElementById(id).addEventListener("keydown", e => {
    if (e.key === "Enter") document.getElementById("btn-set").click();
  });
});

// ── Boot ────────────────────────────────────────────────────────────

(async () => {
  const langSelect = document.getElementById("lang-select");
  if (langSelect) currentLang = langSelect.value;

  await initGrid();
  await updateClock();

  setInterval(() => {
    if (demoInterval === null) updateClock();
  }, 60_000);
})();
