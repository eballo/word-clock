/**
 * wordclock.js — Web simulator frontend
 *
 * Evolved from the original JavaScript prototype by Enric Ballo.
 * Time logic and letter lookup are now handled by the Flask API.
 * This file only manages the DOM and calls the API.
 */

const API = "";          // same origin as Flask
const LANG = "english";  // default language

let numCols = 16;
let demoInterval = null;

// ── Build the grid DOM ──────────────────────────────────────────────

async function initGrid() {
  const res  = await fetch(`${API}/api/grid?lang=${LANG}`);
  const data = await res.json();

  numCols = data.cols;

  const panel = document.getElementById("word-clock");
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
}

// ── Update the display ──────────────────────────────────────────────

async function updateClock(h, m) {
  const params = (h !== undefined && m !== undefined)
    ? `?lang=${LANG}&h=${h}&m=${m}`
    : `?lang=${LANG}`;

  const res  = await fetch(`${API}/api/time${params}`);
  const data = await res.json();

  if (data.error) { console.error("API error:", data.error); return; }

  // Dim all tiles
  document.querySelectorAll(".tile").forEach(t => t.classList.remove("on"));

  // Light up the active ones
  data.coords.forEach(([row, col]) => {
    const tile = document.getElementById(`r${row}c${col}`);
    if (tile) tile.classList.add("on");
  });

  document.getElementById("sentence").textContent = data.sentence;
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
  updateClock(h, m);
}

// ── Controls ────────────────────────────────────────────────────────

document.getElementById("btn-now").addEventListener("click", () => {
  stopDemo();
  document.getElementById("hour-input").value = "";
  document.getElementById("min-input").value  = "";
  updateClock();
});

document.getElementById("btn-set").addEventListener("click", () => {
  stopDemo();
  const h = parseInt(document.getElementById("hour-input").value);
  const m = parseInt(document.getElementById("min-input").value);
  if (!isNaN(h) && !isNaN(m)) updateClock(h, m);
});

document.getElementById("btn-demo").addEventListener("click", () => {
  if (demoInterval !== null) stopDemo();
  else startDemo();
});

["hour-input", "min-input"].forEach(id => {
  document.getElementById(id).addEventListener("keydown", e => {
    if (e.key === "Enter") document.getElementById("btn-set").click();
  });
});

// ── Boot ────────────────────────────────────────────────────────────

(async () => {
  await initGrid();
  await updateClock();
  setInterval(() => {
    if (demoInterval === null) updateClock();
  }, 60_000);
})();
