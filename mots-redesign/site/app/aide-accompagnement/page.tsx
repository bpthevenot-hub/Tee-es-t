import Link from 'next/link'
import PageHero from '@/components/PageHero'
import Reveal from '@/components/Reveal'
import LiteYouTube from '@/components/LiteYouTube'
import EcgLine from '@/components/EcgLine'
import { TEL_AFFICHE, TEL_HREF, YOUTUBE_ID } from '@/lib/infos'

export const metadata = {
  title: 'Aide & accompagnement',
  description:
    'Le parcours d’aide MOTS en 5 étapes : un appel 7 j/7, une écoute par un répondant formé, un entretien confraternel confidentiel, puis un accompagnement global et personnalisé. Gratuit, confidentiel, entre pairs.',
}

const ETAPES = [
  {
    numero: '1',
    titre: 'Vous appelez la ligne dédiée',
    texte: `Composez le ${TEL_AFFICHE}, 7 jours sur 7. Pas de dossier à constituer, pas de justification à fournir : un appel suffit pour enclencher le dispositif.`,
  },
  {
    numero: '2',
    titre: 'Un répondant formé vous écoute',
    texte:
      'Au bout du fil, une personne formée à l’écoute des soignants prend le temps de comprendre votre situation, sans jugement. C’est elle qui oriente la suite du parcours.',
  },
  {
    numero: '3',
    titre: 'Un médecin effecteur vous reçoit',
    texte:
      'Un médecin effecteur vous propose un entretien confraternel strictement confidentiel. Vous parlez d’égal à égal, avec un pair qui connaît la réalité de votre métier.',
  },
  {
    numero: '4',
    titre: 'Un accompagnement global et personnalisé',
    texte:
      'Santé, organisation du travail, et si besoin dimensions administratives, financières ou juridiques : l’accompagnement s’adapte à votre situation, de quelques semaines à quelques mois.',
  },
  {
    numero: '5',
    titre: 'Vous retrouvez équilibre et autonomie',
    texte:
      'L’objectif n’est pas de faire à votre place, mais de vous permettre de reprendre pied durablement : retrouver votre équilibre, votre autonomie et le goût d’exercer.',
  },
]

const DIFFICULTES = [
  {
    titre: 'Épuisement professionnel',
    texte: 'Burn-out, fatigue qui ne passe plus, sentiment de ne plus y arriver.',
  },
  {
    titre: 'Surinvestissement',
    texte:
      'Un engagement sans limite qui finit par déborder sur votre santé et votre vie personnelle.',
  },
  {
    titre: 'Problème de santé',
    texte:
      'Une maladie, physique ou psychique, difficile à concilier avec l’exercice de votre métier.',
  },
  {
    titre: 'Addictions',
    texte:
      'Alcool, médicaments ou autres dépendances : en parler à un pair, sans crainte d’être jugé.',
  },
  {
    titre: 'Difficultés administratives, financières ou juridiques',
    texte:
      'Des situations complexes qui pèsent sur l’exercice et méritent d’être démêlées avec méthode.',
  },
  {
    titre: 'Souffrance au travail',
    texte: 'Conflits, isolement, perte de sens, conditions d’exercice devenues intenables.',
  },
]

const PRINCIPES = [
  {
    titre: 'Gratuité',
    texte:
      'L’accompagnement ne vous coûte rien : il repose sur un esprit d’entraide entre soignants.',
  },
  {
    titre: 'Confidentialité stricte',
    texte:
      'Ce que vous confiez reste entre vous et le médecin qui vous accompagne. Rien ne sort du cadre de l’entretien.',
  },
  {
    titre: 'Entre pairs',
    texte:
      'Vous êtes écouté·e et accompagné·e par des soignants qui connaissent votre quotidien de l’intérieur.',
  },
]

export default function AideAccompagnement() {
  return (
    <>
      <PageHero
        surtitre="Le dispositif d’aide"
        titre="Un appel, puis un vrai parcours d’accompagnement"
        intro="Du premier coup de fil au retour à l’équilibre, le dispositif MOTS suit un chemin simple et balisé, pensé par des soignants pour des soignants. Voici comment cela se passe, étape par étape."
      >
        <a href={TEL_HREF} className="bouton-appel">
          Appeler le {TEL_AFFICHE} — 7 j/7
        </a>
      </PageHero>

      {/* ---- Le parcours en cinq étapes ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <p className="etiquette">Étape par étape</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">Le parcours d’aide en cinq étapes</h2>
          <p className="mt-4 max-w-2xl text-encre/75">
            Chaque parcours est unique, mais tous commencent de la même façon : par un appel.
            Ensuite, vous n’avancez jamais seul·e.
          </p>
        </Reveal>
        <ol className="mt-10 space-y-6">
          {ETAPES.map((e, i) => (
            <li key={e.numero}>
              <Reveal delay={i * 90}>
                <article
                  className={`carte flex max-w-2xl items-start gap-5 border-l-4 !border-l-sapin ${i % 2 === 1 ? 'md:ml-auto' : ''}`}
                >
                  <span
                    aria-hidden="true"
                    className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-sapin text-xl font-bold text-white"
                  >
                    {e.numero}
                  </span>
                  <div>
                    <h3 className="text-lg font-bold text-marine">
                      <span className="sr-only">Étape {e.numero} — </span>
                      {e.titre}
                    </h3>
                    <p className="mt-2 text-encre/75">{e.texte}</p>
                  </div>
                </article>
              </Reveal>
            </li>
          ))}
        </ol>
      </section>

      {/* ---- Pour quelles difficultés ---- */}
      <section className="bg-sable/60 py-16">
        <div className="conteneur">
          <Reveal>
            <p className="etiquette">Toutes les portes d’entrée sont légitimes</p>
            <h2 className="titre-section mt-3 max-w-2xl text-marine">Pour quelles difficultés ?</h2>
            <p className="mt-4 max-w-2xl text-encre/75">
              Il n’y a pas de « bon » ou de « mauvais » motif d’appel. Si quelque chose pèse sur
              votre exercice ou sur votre santé, c’est une raison suffisante.
            </p>
          </Reveal>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {DIFFICULTES.map((d, i) => (
              <Reveal key={d.titre} delay={i * 80}>
                <article className="carte h-full">
                  <h3 className="font-bold text-marine">{d.titre}</h3>
                  <p className="mt-2 text-sm text-encre/75">{d.texte}</p>
                </article>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ---- Les trois principes ---- */}
      <section className="conteneur py-16">
        <Reveal>
          <p className="etiquette">Le cadre de l’accompagnement</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">Trois principes, sans exception</h2>
        </Reveal>
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {PRINCIPES.map((p, i) => (
            <Reveal key={p.titre} delay={i * 110}>
              <article className="carte h-full border-t-4 !border-t-sapin">
                <h3 className="font-bold text-marine">{p.titre}</h3>
                <p className="mt-2 text-encre/75">{p.texte}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---- Vidéo officielle ---- */}
      <section className="bg-ecume py-16">
        <div className="conteneur grid items-center gap-10 lg:grid-cols-2">
          <Reveal>
            <p className="etiquette">En vidéo</p>
            <h2 className="titre-section mt-3 text-marine">Le dispositif expliqué en images</h2>
            <p className="mt-4 text-encre/75">
              Quelques minutes pour comprendre l’esprit de l’association et la façon dont
              l’accompagnement se déroule, racontés par ceux qui le font vivre.
            </p>
          </Reveal>
          <Reveal delay={120}>
            <LiteYouTube videoId={YOUTUBE_ID} title="Association MOTS, prendre soin des soignants" />
          </Reveal>
        </div>
      </section>

      {/* ---- Bandeau final ---- */}
      <section className="conteneur pb-4 pt-2">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-marine p-10 text-white sm:p-14">
            <div aria-hidden="true" className="orbe -right-20 -top-20 h-64 w-64 bg-accent/30" />
            <h2 className="titre-section relative max-w-xl">La première étape ne demande qu’un appel.</h2>
            <p className="relative mt-3 max-w-xl text-white/80">
              Que vous appeliez pour vous-même ou pour un confrère ou une consœur qui vous inquiète,
              la ligne répond 7 jours sur 7 — et la conversation reste entre soignants.
            </p>
            <div className="relative mt-7 flex flex-wrap gap-4">
              <a href={TEL_HREF} className="bouton-appel !px-8 !py-4 text-lg">
                Appeler le {TEL_AFFICHE}
              </a>
              <Link href="/faq" className="bouton-secondaire !border-white/30 !bg-white/10 !text-white hover:!bg-white/20">
                Consulter les questions fréquentes
              </Link>
            </div>
            <EcgLine className="relative mt-8 h-10 w-full text-ecume/40" />
          </div>
        </Reveal>
      </section>
    </>
  )
}
