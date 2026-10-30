// Render Act 1's in-world screens (overlays/screens.html, cues from scripts/overlay_cues.py) to PNG sequences the
// Blender set maps onto their surfaces (scenes/blender/screens.py): renders/screens/<name>/f_0001.png ... one per
// timeline frame from the screen's start, and range.json with the timeline frame of f_0001 and the count. After
// Not Yet's overlays/screen.mjs. A looping screen (the ticker) renders exactly one loop.
//
// Usage: node overlays/screens.mjs [--only name,...] [--at t1,t2,...]   (--at: stills only, to renders/screens/stills)
import { mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import puppeteer from "puppeteer";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const cues = JSON.parse(readFileSync(join(ROOT, "overlays/cues.json"), "utf8"));
const args = process.argv.slice(2);
const opt = (k, d) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const only = opt("--only", Object.keys(cues.screens).join(",")).split(",");
const FPS = cues.fps, PRE = cues.pre;

// --no-sandbox as the project's other Puppeteer scripts: this Ubuntu blocks Chrome's user-namespace sandbox, and the
// page only loads local project files.
const browser = await puppeteer.launch({ headless: "shell", args: ["--no-sandbox", "--allow-file-access-from-files"] });
try {
  const p = await browser.newPage();
  await p.goto(pathToFileURL(join(ROOT, "overlays/screens.html")).href);
  if (!(await p.evaluate(c => setup(c), cues))) throw new Error("fonts did not load");
  for (const name of only) {
    const S = cues.screens[name];
    const [W, H] = S.size;
    await p.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
    const snap = async (t, file) => {
      await p.evaluate((n, t) => show(n, t), name, t);
      writeFileSync(file, await p.screenshot({ type: "png", clip: { x: 0, y: 0, width: W, height: H } }));
    };
    if (args.includes("--at")) {
      const out = "renders/screens/stills";
      mkdirSync(out, { recursive: true });
      for (const t of opt("--at", "").split(",").map(Number)) await snap(t, join(out, `${name}_${t.toFixed(2)}.png`));
      continue;
    }
    const out = join("renders/screens", name);
    mkdirSync(out, { recursive: true });
    const f0 = Math.round((PRE + S.from) * FPS);
    const n = S.loop ? Math.round((S.to - S.from) * FPS) : Math.round((PRE + S.to) * FPS) - f0 + 1;
    for (let k = 0; k < n; k++) await snap((f0 + k) / FPS - PRE, join(out, `f_${String(k + 1).padStart(4, "0")}.png`));
    writeFileSync(join(out, "range.json"), JSON.stringify({ first_frame: f0, count: n, loop: !!S.loop, size: S.size }) + "\n");
    console.log(`screen ${name}: ${n} frames from timeline frame ${f0} -> ${out}`);
  }
} finally {
  await browser.close();
}
