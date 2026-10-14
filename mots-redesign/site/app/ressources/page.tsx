import Link from 'next/link'
import PageHero from '@/components/PageHero'
import Reveal from '@/components/Reveal'
import { TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

export const metadata = {
  title: 'Ressources',
  description:
    'Repères thématiques sur la santé des soignants — épuisement, stress, addictions, équilibre de vie —, outil d’autoévaluation OASIS et numéros utiles.',
}

const THEMES = [
  {
    titre: 'Épuisement professionnel et burn-out',
    texte:
      'La charge de travail, la responsabilité permanente et la difficulté à dire non exposent particulièrement les soignants à l’épuisement. S’informer sur ses mécanismes aide à reconnaître les premiers signes — chez soi comme chez un confrère — avant que la situation ne s’installe.',
  },
  {
    titre: 'Stress et anxiété',
    texte:
      'Urgences, décisions lourdes, interruptions constantes : le stress fait partie du quotidien du soin. Comprendre comment il agit sur le corps et l’esprit permet de repérer le moment où il cesse d’être un moteur pour devenir une usure.',
  },
  {
    titre: 'Dépression',
    texte:
      'Les professionnels de santé tardent souvent à se reconnaître malades et à consulter pour eux-mêmes. Mettre des mots sur la perte d’élan, le repli ou les idées sombres est une étape essentielle pour accepter d’être aidé à son tour.',
  },
  {
    titre: 'Addictions',
    texte:
      'L’accès facilité aux substances et la banalisation de l’automédication rendent les soignants vulnérables aux conduites addictives. En parler sans honte, avec un pair qui comprend ce contexte, change profondément la manière d’aborder le soin.',
  },
  {
    titre: 'Harcèlement et conflits au travail',
    texte:
      'Tensions d’équipe, pressions hiérarchiques ou relations dégradées avec des patients pèsent lourdement sur la santé psychique. Identifier ces situations pour ce qu’elles sont permet de sortir de l’isolement et d’envisager des recours.',
  },
  {
    titre: 'Équilibre vie professionnelle / vie personnelle',
    texte:
      'Gardes, horaires étendus et disponibilité permanente grignotent le temps du repos, de la famille et des projets personnels. Réfléchir à son organisation et à ses limites n’est pas un luxe : c’est une condition pour durer dans le métier.',
  },
]

const NUMEROS = [
  {
    titre: 'La ligne MOTS',
    numero: TEL_AFFICHE,
    href: TEL_HREF,
    texte:
      'Écoute dédiée aux professionnels de santé, 7 j/7. Un répondant formé vous oriente en toute confidentialité.',
  },
  {
    titre: 'Le 3114',
    numero: '3114',
    href: 'tel:3114',
    texte:
      'Numéro national de prévention du suicide. Gratuit, accessible 24 h/24, pour vous ou pour un proche en souffrance.',
  },
  {
    titre: 'Le 15',
    numero: '15',
    href: 'tel:15',
    texte:
      'En cas d’urgence vitale immédiate, pour vous-même ou pour autrui, composez le 15 sans attendre.',
  },
]

export default function Ressources() {
  return (
    <>
      <PageHero
        surtitre="Pour s’informer et se situer"
        titre="Ressources"
        intro="Des repères pour comprendre ce que traversent les soignants, un outil pour faire le point sur sa propre situation, et les numéros à garder à portée de main."
      />

      {/* ---- Bibliothèque thématique ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <p className="etiquette">Bibliothèque thématique</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">
            Comprendre, c’est déjà commencer à se protéger
          </h2>
          <p className="mt-4 max-w-2xl text-encre/75">
            Ces grands thèmes reviennent dans la plupart des situations que rencontre
            l’association. Chacun mérite qu’on s’y attarde — pour soi, ou pour mieux accompagner
            un collègue.
          </p>
        </Reveal>
        <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {THEMES.map((t, i) => (
            <Reveal key={t.titre} delay={i * 90}>
              <article className="carte h-full border-t-4 !border-t-sapin">
                <h3 className="font-bold text-marine">{t.titre}</h3>
                <p className="mt-2 text-encre/75">{t.texte}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---- Autoévaluation OASIS ---- */}
      <section className="bg-sable/60 py-16">
        <div className="conteneur">
          <Reveal>
            <p className="etiquette">Autoévaluation</p>
            <h2 className="titre-section mt-3 max-w-2xl text-marine">
              OASIS, faire le point en quelques minutes
            </h2>
          </Reveal>
          <Reveal delay={100}>
            <div className="mt-8 max-w-3xl space-y-4 text-encre/80">
              <p>
                OASIS est un outil numérique d’autoévaluation développé à l’initiative de MOTS en
                2024. Ce questionnaire en ligne vous aide à évaluer votre fatigue, à objectiver
                votre charge et à repérer d’éventuels signaux de souffrance.
              </p>
              <p>
                Quelques minutes suffisent pour obtenir une photographie honnête de votre situation
                — un premier pas concret, à votre rythme, sans engagement. Et si le résultat vous
                interroge, la ligne d’écoute est là pour en parler.
              </p>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ---- Numéros utiles ---- */}
      <section className="conteneur py-16">
        <Reveal>
          <p className="etiquette">À garder à portée de main</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">Les numéros utiles</h2>
        </Reveal>
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {NUMEROS.map((n, i) => (
            <Reveal key={n.titre} delay={i * 110}>
              <article className="carte h-full text-center">
                <h3 className="font-bold text-marine">{n.titre}</h3>
                <p className="mt-3">
                  <a
                    href={n.href}
                    className="text-2xl font-bold tracking-tight text-sapin underline-offset-4 hover:underline"
                  >
                    {n.numero}
                  </a>
                </p>
                <p className="mt-3 text-sm text-encre/75">{n.texte}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---- Bandeau final ---- */}
      <section className="conteneur pb-4 pt-2">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-marine p-10 text-white sm:p-14">
            <div aria-hidden="true" className="orbe -right-20 -top-20 h-64 w-64 bg-accent/30" />
            <h2 className="titre-section relative max-w-xl">Lire aide. Parler change tout.</h2>
            <p className="relative mt-3 max-w-xl text-white/80">
              Si un de ces thèmes résonne avec ce que vous vivez, n’attendez pas d’être à bout : un
              appel confidentiel suffit pour être écouté par un pair.
            </p>
            <div className="relative mt-7 flex flex-wrap gap-4">
              <a href={TEL_HREF} className="bouton-appel !px-8 !py-4 text-lg">
                {TEL_AFFICHE} — 7 j/7
              </a>
              <Link href="/aide-accompagnement" className="bouton-secondaire !border-white/30 !bg-white/10 !text-white hover:!bg-white/20">
                Comment se passe l’accompagnement ?
              </Link>
            </div>
          </div>
        </Reveal>
      </section>
    </>
  )
}
