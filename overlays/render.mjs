// Render Act 1's overlay (overlays/overlay.html, cues from scripts/overlay_cues.py) to transparent PNGs, one per
// timeline frame that shows something: <out>/f_<frame>.png, frame = round((pre-roll + song s) x fps), as the Blender
// frames, so the edit composites each over its picture. After Not Yet's overlays/render.mjs.
//
// Usage:
//   node overlays/render.mjs [--out renders/overlays/act1] [--size 1920x1080]
//   node overlays/render.mjs --at t1,t2,... [--out dir]          (stills at song times, for checks)
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import puppeteer from "puppeteer";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const cues = JSON.parse(readFileSync(join(ROOT, "overlays/cues.json"), "utf8"));
const args = process.argv.slice(2);
const opt = (k, d) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const [W, H] = opt("--size", "1920x1080").split("x").map(Number);
const FPS = cues.fps, PRE = cues.pre;
const out = opt("--out", args.includes("--at") ? "renders/overlays/stills" : "renders/overlays/act1");
mkdirSync(out, { recursive: true });

// --no-sandbox as the project's other Puppeteer scripts: this Ubuntu blocks Chrome's user-namespace sandbox, and the
// page only loads local project files.
const browser = await puppeteer.launch({ headless: "shell", args: ["--no-sandbox", "--allow-file-access-from-files"] });
try {
  const p = await browser.newPage();
  await p.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
  await p.goto(pathToFileURL(join(ROOT, "overlays/overlay.html")).href);
  if (!(await p.evaluate((c, w, h) => setup(c, w, h), cues, W, H))) throw new Error("fonts did not load");
  const shot = () => p.screenshot({ type: "png", omitBackground: true, clip: { x: 0, y: 0, width: W, height: H } });
  if (args.includes("--at")) {
    for (const t of opt("--at", "").split(",").map(Number)) {
      await p.evaluate(t => draw(t), t);
      writeFileSync(join(out, `t_${t.toFixed(2)}.png`), await shot());
    }
  } else {
    let n = 0;
    for (const o of cues.overlay) {
      for (let f = Math.floor((PRE + o.on) * FPS); f <= Math.ceil((PRE + o.off) * FPS); f++) {
        if (await p.evaluate(t => draw(t), f / FPS - PRE)) {
          writeFileSync(join(out, `f_${String(f).padStart(5, "0")}.png`), await shot());
          n++;
        }
      }
    }
    console.log(`overlay: ${n} frames (${W}x${H}) -> ${out}`);
  }
} finally {
  await browser.close();
}
