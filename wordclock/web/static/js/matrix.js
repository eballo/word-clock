/* Mini Matrix Simulator: draws the matrix as printed (face, windows,
   rivets, camera and button) and lights it with the frames that the Python
   scenes send to the strip. Sizes come from matrix.scad through window.FACE. */

'use strict';

const F = window.FACE;
const PANEL_W = F.cols * F.pitch + 2 * F.margin;
const PANEL_H = F.rows * F.pitch + F.margin + F.margin_bottom;
const POLL_MS = 50;
const PHOTO_S = 3;
const OFF_S = 10;

// Rivet centres, as in matrix.scad (y up from the bottom edge).
const RIVET_X0 = F.margin / 2;
const RIVET_X1 = PANEL_W - F.margin / 2;
const RIVET_NX = Math.round((RIVET_X1 - RIVET_X0) / F.rivet_pitch);
const RIVET_BOTTOM = F.outer_t + 0.4 + F.cam_lens[1];
const RIVET_TOP = PANEL_H - F.margin / 2;
const RIVET_NY = Math.round((RIVET_TOP - RIVET_BOTTOM) / F.rivet_pitch);
const rivetX = (i) => RIVET_X0 + (i * (RIVET_X1 - RIVET_X0)) / RIVET_NX;
const rivetY = (j) => RIVET_BOTTOM + (j * (RIVET_TOP - RIVET_BOTTOM)) / RIVET_NY;

const CAMERA = [rivetX(F.cam_rivet), RIVET_BOTTOM];
const BUTTON = [rivetX(RIVET_NX - F.cam_rivet), RIVET_BOTTOM];

function rivets() {
  const points = [];
  for (let i = 0; i <= RIVET_NX; i++) points.push([rivetX(i), RIVET_TOP], [rivetX(i), RIVET_BOTTOM]);
  for (let j = 1; j < RIVET_NY; j++) points.push([RIVET_X0, rivetY(j)], [RIVET_X1, rivetY(j)]);
  return points;
}

const canvas = document.getElementById('matrix');
const ctx = canvas.getContext('2d');
const statusEl = document.getElementById('status');
const holdBar = document.getElementById('hold-bar');
const video = document.getElementById('video');
const controls = {
  scene: document.getElementById('scene'),
  text: document.getElementById('text'),
  color: document.getElementById('color'),
  brightness: document.getElementById('brightness'),
  webcam: document.getElementById('webcam'),
};

let frame = null;
let lastCapture = null;
let pressedAt = null;
let scale = 1;

// ── Drawing ─────────────────────────────────────────────────────────

function resize() {
  const width = canvas.clientWidth * window.devicePixelRatio;
  canvas.width = width;
  canvas.height = (width * PANEL_H) / PANEL_W;
  scale = width / PANEL_W;
}

// Panel point (mm, y up) to canvas pixels.
const px = (x) => x * scale;
const py = (y) => (PANEL_H - y) * scale;

// LEDs give out light in proportion to their value: show what the eye sees.
function ledToScreen(value, brightness) {
  return Math.round(255 * Math.pow((value / 255) * (brightness / 255), 1 / 2.2));
}

function roundRect(x, y, w, h, r) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
}

function drawRivet([x, y], kind) {
  const r = (F.rivet_d / 2) * scale;
  ctx.beginPath();
  ctx.arc(px(x), py(y), r, 0, Math.PI * 2);
  ctx.fillStyle = kind === 'camera' ? '#05070c' : '#0b0b0b';
  ctx.fill();
  ctx.lineWidth = Math.max(1, scale * 0.4);
  ctx.strokeStyle = '#262626';
  ctx.stroke();
  if (kind === 'camera') {
    ctx.beginPath();
    ctx.arc(px(x) - r * 0.25, py(y) - r * 0.25, r * 0.22, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(90, 130, 200, 0.6)';
    ctx.fill();
  }
  if (kind === 'button') {
    ctx.beginPath();
    ctx.arc(px(x), py(y), r * (pressedAt === null ? 0.25 : 0.4), 0, Math.PI * 2);
    ctx.fillStyle = pressedAt === null ? '#3a3a3a' : '#4caf50';
    ctx.fill();
  }
}

function draw() {
  ctx.fillStyle = '#141414';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const size = F.pitch - F.bar_w;
  const brightness = frame ? frame.brightness : 0;
  for (let r = 0; r < F.rows; r++) {
    for (let c = 0; c < F.cols; c++) {
      const [red, green, blue] = frame ? frame.cells[r][c] : [0, 0, 0];
      const color = [red, green, blue].map((v) => ledToScreen(v, brightness));
      const lit = color.some((v) => v > 8);
      const x = px(F.margin + c * F.pitch + F.bar_w / 2);
      const y = py(PANEL_H - F.margin - r * F.pitch - F.bar_w / 2);
      ctx.save();
      roundRect(x, y, size * scale, size * scale, F.window_r * scale);
      if (lit) {
        const [cr, cg, cb] = color;
        const glow = ctx.createRadialGradient(
          x + (size * scale) / 2, y + (size * scale) / 2, 0,
          x + (size * scale) / 2, y + (size * scale) / 2, size * scale * 0.75,
        );
        glow.addColorStop(0, `rgb(${Math.min(255, cr + 40)}, ${Math.min(255, cg + 40)}, ${Math.min(255, cb + 40)})`);
        glow.addColorStop(1, `rgb(${Math.round(cr * 0.7)}, ${Math.round(cg * 0.7)}, ${Math.round(cb * 0.7)})`);
        ctx.shadowColor = `rgb(${cr}, ${cg}, ${cb})`;
        ctx.shadowBlur = size * scale * 0.35;
        ctx.fillStyle = glow;
      } else {
        // Tracing paper with no light behind it.
        ctx.fillStyle = '#1d1c19';
      }
      ctx.fill();
      ctx.restore();
    }
  }

  for (const point of rivets()) {
    const isCamera = point[0] === CAMERA[0] && point[1] === CAMERA[1];
    const isButton = point[0] === BUTTON[0] && point[1] === BUTTON[1];
    drawRivet(point, isCamera ? 'camera' : isButton ? 'button' : 'rivet');
  }
}

// ── Button ──────────────────────────────────────────────────────────

function overButton(event) {
  const rect = canvas.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * PANEL_W;
  const y = PANEL_H - ((event.clientY - rect.top) / rect.height) * PANEL_H;
  return Math.hypot(x - BUTTON[0], y - BUTTON[1]) < F.rivet_d * 1.5;
}

async function post(path, body) {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error((await response.json()).detail || response.statusText);
  return response.json();
}

function showHold() {
  if (pressedAt === null) {
    holdBar.style.width = '0';
    holdBar.className = 'hold-bar';
    return;
  }
  const held = (performance.now() - pressedAt) / 1000;
  holdBar.style.width = `${Math.min(100, (held / OFF_S) * 100)}%`;
  holdBar.className = `hold-bar${held >= OFF_S ? ' off' : held >= PHOTO_S ? ' photo' : ''}`;
  requestAnimationFrame(showHold);
}

canvas.addEventListener('pointermove', (event) => {
  canvas.classList.toggle('over-button', overButton(event));
});

canvas.addEventListener('pointerdown', (event) => {
  if (!overButton(event)) return;
  canvas.setPointerCapture(event.pointerId);
  pressedAt = performance.now();
  post('/api/matrix/button', { down: true }).catch(showError);
  showHold();
});

async function release() {
  if (pressedAt === null) return;
  pressedAt = null;
  try {
    const { action } = await post('/api/matrix/button', { down: false });
    if (action === 'photo' && !controls.webcam.checked) {
      showError(new Error('Photo: tick "Webcam as camera" to use your webcam.'));
    }
  } catch (error) {
    showError(error);
  }
}

canvas.addEventListener('pointerup', release);
canvas.addEventListener('pointercancel', release);

// ── Camera ──────────────────────────────────────────────────────────

async function startWebcam() {
  try {
    video.srcObject = await navigator.mediaDevices.getUserMedia({ video: true });
    await video.play();
  } catch (error) {
    controls.webcam.checked = false;
    showError(new Error(`Webcam: ${error.message}`));
  }
}

function stopWebcam() {
  if (video.srcObject) video.srcObject.getTracks().forEach((track) => track.stop());
  video.srcObject = null;
}

async function capture() {
  if (!video.srcObject || !video.videoWidth) return;
  const shot = document.createElement('canvas');
  shot.width = 320;
  shot.height = Math.round((320 * video.videoHeight) / video.videoWidth);
  shot.getContext('2d').drawImage(video, 0, 0, shot.width, shot.height);
  try {
    await post('/api/matrix/photo', { image: shot.toDataURL('image/jpeg', 0.85) });
  } catch (error) {
    showError(error);
  }
}

controls.webcam.addEventListener('change', () => (controls.webcam.checked ? startWebcam() : stopWebcam()));

// ── Controls ────────────────────────────────────────────────────────

function sendScene() {
  post('/api/matrix/scene', {
    name: controls.scene.value,
    text: controls.text.value || ' ',
    color: controls.color.value.slice(1),
  }).catch(showError);
}

controls.scene.addEventListener('change', sendScene);
controls.text.addEventListener('change', sendScene);
controls.color.addEventListener('change', sendScene);
controls.brightness.addEventListener('input', () => {
  post('/api/matrix/brightness', { brightness: Number(controls.brightness.value) }).catch(showError);
});
document.getElementById('controls').addEventListener('submit', (event) => event.preventDefault());

// ── Frames ──────────────────────────────────────────────────────────

// Keep a message on screen for a few seconds before the status comes back.
function showError(error) {
  statusEl.textContent = error.message;
  statusEl.dataset.error = '1';
  clearTimeout(showError.timer);
  showError.timer = setTimeout(() => delete statusEl.dataset.error, 4000);
}

async function poll() {
  try {
    const response = await fetch('/api/matrix/frame');
    frame = await response.json();
    if (lastCapture === null) {
      lastCapture = frame.capture;
      controls.scene.value = frame.scene;
      controls.brightness.value = frame.brightness;
    } else if (frame.capture !== lastCapture) {
      lastCapture = frame.capture;
      capture();
    }
    if (!statusEl.dataset.error) {
      statusEl.textContent = `${frame.scene} · lights ${frame.lights ? 'on' : 'off'} · last press: ${frame.action}`;
    }
    draw();
  } catch (error) {
    statusEl.textContent = 'The simulator is not running: start it with `uv run wordclock-matrix --web`.';
  }
  setTimeout(poll, POLL_MS);
}

window.addEventListener('resize', () => {
  resize();
  draw();
});
resize();
draw();
poll();
