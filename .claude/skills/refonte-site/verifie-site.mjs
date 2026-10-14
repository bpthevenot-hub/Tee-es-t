// Banc de vérification du site Relève (build Next.js servi par `next start`).
// Usage : node verifie-site.mjs <url-base> <dossier-captures>
// Sortie : JSON { ok, defauts[], mesures{}, captures[] }.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs'
import { mkdirSync } from 'node:fs'

const [base, dossier] = process.argv.slice(2)
if (!base || !dossier) { console.error('usage: node verifie-site.mjs <url-base> <dossier-captures>'); process.exit(2) }
mkdirSync(dossier, { recursive: true })

const ROUTES = ['/', '/methode', '/demo/soignant', '/demo/equipe', '/demo/direction', '/preuves', '/mots', '/mentions']
// Lexique interdit (brief § 9) : wellness, gamification, paternalisme.
const INTERDITS = [/bien-être/i, /épanouissement/i, /\bboost/i, /bravo\s*!/i, /prenez soin de vous/i, /streak/i, /badge/i, /\bniveau \d/i, /mascotte/i]
const EMOJI = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/u
const CHIFFRES_INTERDITS = [/180\s?000/, /4\s?:\s?1/, /5\s?:\s?1/, /EOS Renaissance/i]

const defauts = []
const bloquant = (m) => defauts.push({ gravite: 'bloquant', message: m })
const mineur = (m) => defauts.push({ gravite: 'mineur', message: m })
const mesures = { routes: {}, debordementMobile: {}, externes: [], erreurs: [] }
const captures = []

const nav = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] })

async function contexte(opts = {}) {
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 900 }, ...opts })
  const page = await ctx.newPage()
  page.on('pageerror', (e) => mesures.erreurs.push(String(e).slice(0, 200)))
  page.on('console', (m) => { if (m.type() === 'error') mesures.erreurs.push('console: ' + m.text().slice(0, 200)) })
  page.on('request', (r) => { const u = r.url(); if (!u.startsWith(base) && !/^(data|blob|about):/.test(u)) mesures.externes.push(u) })
  return { ctx, page }
}

// ---- Bureau : chaque route ----
{
  const { ctx, page } = await contexte()
  for (const r of ROUTES) {
    const rep = await page.goto(base + r, { waitUntil: 'networkidle' })
    const statut = rep ? rep.status() : 0
    mesures.routes[r] = statut
    if (statut !== 200) { bloquant(`route ${r} : HTTP ${statut}`); continue }
    const texte = (await page.evaluate(() => document.body.innerText)).replace(/ | /g, ' ')
    if (!texte.includes('3114')) bloquant(`${r} : 3114 absent`)
    if (!/Démonstration/i.test(texte)) bloquant(`${r} : bandeau démonstration absent`)
    for (const re of INTERDITS) if (re.test(texte)) bloquant(`${r} : lexique interdit « ${re} »`)
    if (EMOJI.test(texte)) bloquant(`${r} : emoji présent`)
    for (const re of CHIFFRES_INTERDITS) if (re.test(texte)) bloquant(`${r} : chiffre interdit « ${re} »`)
    const h1 = await page.locator('h1').count()
    if (h1 !== 1) bloquant(`${r} : ${h1} balise(s) h1 (attendu 1)`)
    const sansAlt = await page.evaluate(() => Array.from(document.querySelectorAll('img:not([alt])')).length)
    if (sansAlt) bloquant(`${r} : ${sansAlt} image(s) sans alt`)
    const boutonsVides = await page.evaluate(() => Array.from(document.querySelectorAll('button, a')).filter((el) => !el.textContent.trim() && !el.getAttribute('aria-label') && !el.querySelector('[aria-label]')).length)
    if (boutonsVides) bloquant(`${r} : ${boutonsVides} bouton(s)/lien(s) sans nom accessible`)
    const nom = r === '/' ? 'accueil' : r.replace(/^\//, '').replace(/\//g, '-')
    await page.screenshot({ path: `${dossier}/${nom}-bureau.png`, fullPage: true })
    captures.push(`${dossier}/${nom}-bureau.png`)
  }
  // Clavier : lien d'évitement puis Tab jusqu'au premier lien de nav
  await page.goto(base + '/', { waitUntil: 'networkidle' })
  await page.keyboard.press('Tab')
  const premier = await page.evaluate(() => document.activeElement?.textContent?.trim())
  if (!/contenu/i.test(premier || '')) mineur(`premier Tab arrive sur « ${premier} » au lieu du lien d'évitement`)
  await ctx.close()
}

// ---- Mobile 390 px : débordement + menu ----
{
  const { ctx, page } = await contexte({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true })
  for (const r of ROUTES) {
    await page.goto(base + r, { waitUntil: 'networkidle' })
    const d = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
    mesures.debordementMobile[r] = d
    if (d > 1) bloquant(`débordement horizontal de ${d}px à 390px sur ${r}`)
    if (r === '/' || r === '/demo/soignant') {
      const nom = r === '/' ? 'accueil' : 'demo-soignant'
      await page.screenshot({ path: `${dossier}/${nom}-mobile.png`, fullPage: true })
      captures.push(`${dossier}/${nom}-mobile.png`)
    }
  }
  await page.goto(base + '/', { waitUntil: 'networkidle' })
  const menu = page.locator('button[aria-controls="menu-mobile"]')
  if (await menu.count()) {
    await menu.click(); await page.waitForTimeout(200)
    if ((await menu.getAttribute('aria-expanded')) !== 'true') bloquant('menu mobile : aria-expanded ne passe pas à true')
    const liens = await page.locator('#menu-mobile a').count()
    if (liens < 5) bloquant(`menu mobile : ${liens} lien(s)`)
    await menu.click(); await page.waitForTimeout(200)
    if ((await menu.getAttribute('aria-expanded')) !== 'false') bloquant('menu mobile : ne se referme pas')
  } else bloquant('bouton de menu mobile introuvable')
  await ctx.close()
}

// ---- Journal de garde : check-in interactif + modes ----
{
  const { ctx, page } = await contexte()
  await page.goto(base + '/demo/soignant', { waitUntil: 'networkidle' })
  const quadrants = page.locator('[data-quadrant]')
  const nbQ = await quadrants.count()
  if (nbQ < 4) bloquant(`journal de garde : ${nbQ} quadrant(s) de check-in (attendu 4, attribut data-quadrant)`)
  else {
    await quadrants.nth(2).click(); await page.waitForTimeout(250)
    const fond = await page.evaluate(() => getComputedStyle(document.querySelector('[data-checkin-fond]') || document.body).backgroundColor)
    mesures.fondApresCheckin = fond
    await page.screenshot({ path: `${dossier}/demo-soignant-checkin.png` })
    captures.push(`${dossier}/demo-soignant-checkin.png`)
  }
  const couloir = page.locator('[data-mode-couloir]')
  if (await couloir.count()) {
    await couloir.first().click(); await page.waitForTimeout(250)
    const texte = await page.evaluate(() => document.body.innerText)
    if (/Camille|\bAnne\b/.test(texte)) bloquant('mode couloir : le prénom ou le pair restent visibles')
    await page.screenshot({ path: `${dossier}/demo-soignant-couloir.png` })
    captures.push(`${dossier}/demo-soignant-couloir.png`)
  } else mineur('journal de garde : aucun bouton [data-mode-couloir]')
  await ctx.close()
}

// ---- Mouvement réduit : la page reste lisible ----
{
  const { ctx, page } = await contexte({ reducedMotion: 'reduce' })
  await page.goto(base + '/', { waitUntil: 'networkidle' })
  const invisibles = await page.evaluate(() => Array.from(document.querySelectorAll('main h1, main h2, main p')).filter((el) => el.offsetParent !== null && el.textContent.trim() && parseFloat(getComputedStyle(el).opacity) < 0.5).length)
  if (invisibles) bloquant(`sous prefers-reduced-motion, ${invisibles} bloc(s) de texte restent invisibles`)
  await ctx.close()
}

await nav.close()
mesures.externes = [...new Set(mesures.externes)]
for (const u of mesures.externes) bloquant(`requête externe : ${u}`)
for (const e of [...new Set(mesures.erreurs)]) bloquant(`erreur JS : ${e}`)
const ok = !defauts.some((d) => d.gravite === 'bloquant')
console.log(JSON.stringify({ ok, defauts, mesures, captures }, null, 2))
