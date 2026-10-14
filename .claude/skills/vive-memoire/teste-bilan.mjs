// Banc du bilan interactif : onglets (clic + flèches), cases « fait », quiz, débordement à
// 390 px sur CHAQUE onglet, thèmes clair et sombre, erreurs JS.
// Usage : node teste-bilan.mjs <bilan.html> <dossier-captures-hors-dépôt>
// Playwright : variable PLAYWRIGHT_MJS, sinon conteneur cloud, sinon `npm root -g`.
// Navigateur : variable CHROMIUM_PATH, sinon celui du conteneur s'il existe, sinon Playwright choisit.
import { mkdirSync, existsSync } from 'node:fs'
import { resolve, join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { execSync } from 'node:child_process'

const [fichier, dossier] = process.argv.slice(2)
if (!fichier || !dossier) { console.error('usage: node teste-bilan.mjs <bilan.html> <dossier-captures>'); process.exit(2) }
mkdirSync(dossier, { recursive: true })

function modulePlaywright() {
  const candidats = [process.env.PLAYWRIGHT_MJS, '/opt/node22/lib/node_modules/playwright/index.mjs']
  try { candidats.push(join(execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(), 'playwright/index.mjs')) } catch {}
  const trouve = candidats.find((c) => c && existsSync(c))
  return trouve ? pathToFileURL(trouve).href : 'playwright'
}
const { chromium } = await import(modulePlaywright())
const executable = [process.env.CHROMIUM_PATH, '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].find((c) => c && existsSync(c))
const nav = await chromium.launch({ ...(executable ? { executablePath: executable } : {}), args: process.platform === 'linux' ? ['--no-sandbox'] : [] })

const url = pathToFileURL(resolve(fichier)).href
const erreurs = []
const resultats = {}
for (const [nom, opts] of [['bureau-clair', { viewport: { width: 1280, height: 900 }, colorScheme: 'light' }], ['mobile-sombre', { viewport: { width: 390, height: 844 }, colorScheme: 'dark' }]]) {
  const ctx = await nav.newContext(opts); const p = await ctx.newPage()
  p.on('pageerror', (e) => erreurs.push(nom + ': ' + e))
  await p.goto(url, { waitUntil: 'load' })
  await p.screenshot({ path: join(dossier, `${nom}.png`), fullPage: true })
  let debordement = 0
  for (const id of await p.$$eval('[role="tab"]', (els) => els.map((e) => e.id))) {
    await p.click('#' + id)
    debordement = Math.max(debordement, await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth))
  }
  await p.click('#o-attente')
  const nbCases = await p.locator('.coche input').count()
  const avant = Number(await p.textContent('#reste'))
  if (nbCases) await p.locator('.coche input').first().check()
  const apres = Number(await p.textContent('#reste'))
  await p.click('#o-quiz')
  const questions = await p.locator('.question').count()
  let score = ''
  if (questions) {
    const q = p.locator('.question').first()
    if (await q.locator('button[data-juste]').count() !== 1) erreurs.push(nom + ': question 1 sans bonne réponse unique')
    else { await q.locator('button[data-juste]').click(); score = await p.textContent('#score') }
    // Ouvrir aussi les autres questions par une mauvaise réponse : explications et verdicts visibles
    for (let i = 1; i < questions; i++) {
      const faux = p.locator('.question').nth(i).locator('.choix button:not([data-juste])').first()
      if (await faux.count()) await faux.click()
    }
    debordement = Math.max(debordement, await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth))
  }
  if (opts.colorScheme === 'dark') {
    const fond = await p.evaluate(() => getComputedStyle(document.body).backgroundColor)
    const clair = await p.evaluate(() => { const m = getComputedStyle(document.body).backgroundColor.match(/\d+/g) || []; return m.slice(0, 3).reduce((s, v) => s + Number(v), 0) > 382 })
    if (clair) erreurs.push(nom + ': thème sombre non appliqué (fond ' + fond + ')')
  }
  await p.screenshot({ path: join(dossier, `${nom}-quiz.png`), fullPage: true })
  await p.focus('#o-quiz'); await p.keyboard.press('ArrowRight')
  const fleche = await p.evaluate(() => document.activeElement.id)
  resultats[nom] = { debordement, cases: nbCases, resteAvant: avant, resteApres: apres, questions, score, flecheVers: fleche }
  await ctx.close()
}
await nav.close()
const ok = erreurs.length === 0 && Object.values(resultats).every((r) =>
  r.debordement <= 1 && r.flecheVers === 'o-temps' &&
  (!r.cases || r.resteApres === r.resteAvant - 1) &&
  (!r.questions || r.score.startsWith('Juste. 1 /')))
console.log(JSON.stringify({ ok, resultats, erreurs }, null, 2))
process.exit(ok ? 0 : 1)
