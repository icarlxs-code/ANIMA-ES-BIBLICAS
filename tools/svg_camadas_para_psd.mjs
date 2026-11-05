#!/usr/bin/env node
// Converte camadas SVG (camadas.json do gerador) em um PSD em camadas + PNG de prévia.
// Usa o Chromium do Playwright para rasterizar e o ag-psd (dependência do Rigby2D) para escrever o PSD.
// Uso: node tools/svg_camadas_para_psd.mjs <pasta_com_camadas.json> <saida.psd> <previa.png> <rigby2d_dir>
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { createRequire } from 'node:module';

const [dir, outPsd, outPng, rigbyDir] = process.argv.slice(2);
const require = createRequire(join(rigbyDir, 'package.json'));
const { writePsdBuffer } = require('ag-psd');
const { chromium } = createRequire(import.meta.url)('playwright');

const meta = JSON.parse(readFileSync(join(dir, 'camadas.json'), 'utf8'));
const { width: W, height: H } = meta;
const browser = await chromium.launch();
const page = await browser.newPage();
await page.setContent('<canvas id="c"></canvas>');

async function raster(svgText) {
  return page.evaluate(async ({ svgText, W, H }) => {
    const img = new Image();
    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgText)));
    await img.decode();
    const c = document.getElementById('c'); c.width = W; c.height = H;
    const g = c.getContext('2d'); g.clearRect(0, 0, W, H); g.drawImage(img, 0, 0);
    const d = g.getImageData(0, 0, W, H).data;
    let x0 = W, y0 = H, x1 = -1, y1 = -1;
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (d[(y * W + x) * 4 + 3]) {
      if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
    }
    const w = x1 - x0 + 1, h = y1 - y0 + 1;
    const crop = g.getImageData(x0, y0, w, h).data;
    let s = ''; for (let i = 0; i < crop.length; i += 0x8000) s += String.fromCharCode.apply(null, crop.subarray(i, i + 0x8000));
    return { x0, y0, w, h, b64: btoa(s) };
  }, { svgText, W, H });
}

const children = [];
const composite = new Uint8ClampedArray(W * H * 4);
for (const L of meta.layers) {
  const r = await raster(readFileSync(join(dir, 'svg', L.svg), 'utf8'));
  const data = new Uint8ClampedArray(Buffer.from(r.b64, 'base64'));
  children.push({ name: L.name, left: r.x0, top: r.y0, hidden: !L.visible,
    imageData: { width: r.w, height: r.h, data } });
  if (L.visible) for (let y = 0; y < r.h; y++) for (let x = 0; x < r.w; x++) { // composição "over"
    const s = (y * r.w + x) * 4, t = ((y + r.y0) * W + x + r.x0) * 4, a = data[s + 3] / 255;
    if (!a) continue;
    for (let k = 0; k < 3; k++) composite[t + k] = data[s + k] * a + composite[t + k] * (1 - a);
    composite[t + 3] = Math.min(255, data[s + 3] + composite[t + 3] * (1 - a));
  }
  console.error(`${L.name.padEnd(16)} ${r.x0},${r.y0} ${r.w}x${r.h}${L.visible ? '' : ' (oculta)'}`);
}
// PSD: ag-psd lista a primeira camada como a de baixo.
writeFileSync(outPsd, writePsdBuffer({ width: W, height: H, children,
  imageData: { width: W, height: H, data: composite } }, { generateThumbnail: false }));

// Prévia sobre fundo cinza.
const b64 = Buffer.from(composite).toString('base64');
const png = await page.evaluate(({ b64, W, H }) => {
  const bin = atob(b64); const arr = new Uint8ClampedArray(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  const c = document.getElementById('c'); c.width = W; c.height = H; const g = c.getContext('2d');
  const t = document.createElement('canvas'); t.width = W; t.height = H;
  t.getContext('2d').putImageData(new ImageData(arr, W, H), 0, 0);
  const bg = g.createLinearGradient(0, 0, 0, H); bg.addColorStop(0, '#5a5a5a'); bg.addColorStop(1, '#b4b4b4'); g.fillStyle = bg; g.fillRect(0, 0, W, H); g.fillStyle = 'rgba(40,40,40,.35)'; g.beginPath(); g.ellipse(W / 2 + 60, H - 225, 260, 22, -0.05, 0, Math.PI * 2); g.fill(); g.drawImage(t, 0, 0);
  return c.toDataURL('image/png').split(',')[1];
}, { b64, W, H });
writeFileSync(outPng, Buffer.from(png, 'base64'));
await browser.close();
console.error(`PSD: ${outPsd} (${children.length} camadas)`);
