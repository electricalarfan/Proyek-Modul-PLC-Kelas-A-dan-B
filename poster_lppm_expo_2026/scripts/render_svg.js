// usage: NODE_PATH=<global node_modules> node render_svg.js in.svg out.png widthPx
// Rasterises an SVG with a transparent background using the preinstalled Chromium.
const { chromium } = require("playwright");
const fs = require("fs");

(async () => {
  const [src, dst, w] = process.argv.slice(2);
  let svg = fs.readFileSync(src, "utf8").replace(/<\?xml[^>]*\?>/, "");
  const vb = svg.match(/viewBox="([^"]+)"/)[1].trim().split(/\s+/).map(Number);
  const W = Number(w);
  const H = Math.round((W * vb[3]) / vb[2]);
  svg = svg.replace(/width="[^"]*pt"/, `width="${W}"`).replace(/height="[^"]*pt"/, `height="${H}"`);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
  await page.screenshot({ path: dst, omitBackground: true, clip: { x: 0, y: 0, width: W, height: H } });
  await browser.close();
})();
