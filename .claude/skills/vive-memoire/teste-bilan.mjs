// Banc du bilan interactif : onglets, cases « fait », quiz, flèches clavier,
// largeur téléphone, thème sombre, erreurs JS.
// Usage : node teste-bilan.mjs <bilan.html> <dossier-captures>
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs'
import { mkdirSync } from 'node:fs'
import { resolve, join } from 'node:path'

const [fichier, dossier] = process.argv.slice(2)
if (!fichier || !dossier) { console.error('usage: node teste-bilan.mjs <bilan.html> <dossier-captures>'); process.exit(2) }
mkdirSync(dossier, { recursive: true })
const url = 'file://' + resolve(fichier)
const nav = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] })
const erreurs = []
const resultats = {}
for (const [nom, opts] of [['bureau-clair', { viewport: { width: 1280, height: 900 }, colorScheme: 'light' }], ['mobile-sombre', { viewport: { width: 390, height: 844 }, colorScheme: 'dark' }]]) {
  const ctx = await nav.newContext(opts); const p = await ctx.newPage()
  p.on('pageerror', (e) => erreurs.push(nom + ': ' + e))
  await p.goto(url, { waitUntil: 'load' })
  const debordement = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
  await p.screenshot({ path: join(dossier, `${nom}.png`), fullPage: true })
  await p.click('#o-attente')
  const avant = await p.textContent('#reste')
  if (await p.locator('.coche input').count()) await p.locator('.coche input').first().check()
  const apres = await p.textContent('#reste')
  await p.click('#o-quiz')
  if (await p.locator('.question').count()) await p.locator('.question').first().locator('button[data-juste]').click()
  const score = await p.textContent('#score')
  await p.screenshot({ path: join(dossier, `${nom}-quiz.png`), fullPage: true })
  await p.focus('#o-quiz'); await p.keyboard.press('ArrowRight')
  const fleche = await p.evaluate(() => document.activeElement.id)
  resultats[nom] = { debordement, resteAvant: avant, resteApres: apres, score, flecheVers: fleche }
  await ctx.close()
}
await nav.close()
const ok = erreurs.length === 0 && Object.values(resultats).every((r) => r.debordement <= 1 && r.flecheVers === 'o-temps')
console.log(JSON.stringify({ ok, resultats, erreurs }, null, 2))
process.exit(ok ? 0 : 1)
