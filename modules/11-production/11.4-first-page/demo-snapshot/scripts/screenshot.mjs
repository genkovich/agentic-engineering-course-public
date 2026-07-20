// Знімає сторінку у двох в'юпортах (1440×900 і 390×844, обидва @2x)
// і валить процес, якщо є горизонтальний скрол.
//
//   node scripts/screenshot.mjs <url> <basename> [outDir]
//   node scripts/screenshot.mjs http://localhost:5173 good-page shots/
//
// Результат: <outDir>/<basename>.png і <outDir>/<basename>-mobile.png

import { chromium } from "playwright"
import { mkdirSync } from "node:fs"
import { resolve } from "node:path"

const [url, basename, outDir = "shots"] = process.argv.slice(2)

if (!url || !basename) {
  console.error("usage: node scripts/screenshot.mjs <url> <basename> [outDir]")
  process.exit(1)
}

const VIEWPORTS = [
  { suffix: "", width: 1440, height: 900 },
  { suffix: "-mobile", width: 390, height: 844 },
]

mkdirSync(outDir, { recursive: true })

const browser = await chromium.launch({ channel: "chrome" })
let failed = false

for (const { suffix, width, height } of VIEWPORTS) {
  const page = await browser.newPage({
    viewport: { width, height },
    deviceScaleFactor: 2,
  })
  await page.goto(url, { waitUntil: "networkidle" })
  // даємо відпрацювати анімаціям появи карток
  await page.waitForTimeout(1200)

  const overflow = await page.evaluate(() => {
    const doc = document.documentElement
    return {
      scrollWidth: doc.scrollWidth,
      clientWidth: doc.clientWidth,
    }
  })
  if (overflow.scrollWidth > overflow.clientWidth) {
    console.error(
      `FAIL ${width}×${height}: горизонтальний скрол ` +
        `(scrollWidth ${overflow.scrollWidth} > clientWidth ${overflow.clientWidth})`
    )
    failed = true
  }

  const path = resolve(outDir, `${basename}${suffix}.png`)
  await page.screenshot({ path, fullPage: false })
  console.log(`OK ${width}×${height} → ${path}`)
  await page.close()
}

await browser.close()
process.exit(failed ? 1 : 0)
