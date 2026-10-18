import Link from 'next/link'
import Reveal from '@/components/Reveal'
import EcgLine from '@/components/EcgLine'
import LiteYouTube from '@/components/LiteYouTube'
import IntroPortail from '@/components/IntroPortail'
import EtudesScientifiques from '@/components/EtudesScientifiques'
import { CHIFFRES, PROFESSIONS, TEL_AFFICHE, TEL_HREF, YOUTUBE_ID } from '@/lib/infos'

export default function Accueil() {
  return (
    <>
      <IntroPortail />
      {/* ---- Héro ---- */}
      <section className="relative overflow-hidden bg-marine text-white">
        <div aria-hidden="true" className="orbe -top-32 left-1/4 h-96 w-96 bg-sapin-clair/40" />
        <div aria-hidden="true" className="orbe top-1/3 -right-24 h-80 w-80 bg-accent/25" style={{ animationDelay: '-6s' }} />
        <div aria-hidden="true" className="orbe -bottom-40 left-0 h-72 w-72 bg-ecume/15" style={{ animationDelay: '-11s' }} />

        <div className="conteneur relative flex min-h-[82vh] flex-col justify-center py-20">
          <Reveal>
            <p className="etiquette !bg-white/10 !text-ecume">
              <span aria-hidden="true" className="point-vif h-2 w-2 rounded-full bg-accent" />
              Écoute dédiée aux soignants — 7 j/7
            </p>
            <h1 className="titre-hero mt-6 max-w-3xl">
              Vous soignez les autres.
              <br />
              <span className="text-ecume/90">Qui prend soin de vous ?</span>
            </h1>
            <p className="mt-6 max-w-2xl text-lg text-white/80">
              Depuis 2010, des médecins spécifiquement formés écoutent et accompagnent les
              professionnels de santé qui traversent une période difficile — épuisement,
              santé, organisation du travail. Gratuitement, en toute confidentialité.
            </p>
            <div className="mt-9 flex flex-wrap items-center gap-4">
              <a href={TEL_HREF} className="bouton-appel !px-8 !py-4 text-lg">
                Appeler le {TEL_AFFICHE}
              </a>
              <Link href="/aide-accompagnement" className="bouton-secondaire !border-white/30 !bg-white/10 !text-white hover:!bg-white/20">
                Comment ça se passe ?
              </Link>
            </div>
            <p className="mt-4 text-sm text-white/60">
              Appel confidentiel, pris par un répondant formé. Vous n’êtes pas seul·e.
            </p>
          </Reveal>
        </div>
        <EcgLine className="h-16 w-full text-ecume/50" />
      </section>

      {/* ---- Chiffres clés ---- */}
      <section aria-label="Chiffres clés" className="conteneur -mt-2 py-14">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {CHIFFRES.map((c, i) => (
            <Reveal key={c.legende} delay={i * 90}>
              <div className="carte text-center">
                <p className="text-3xl font-bold tracking-tight text-sapin">{c.valeur}</p>
                <p className="mt-1 text-sm text-brume">{c.legende}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---- Ce que dit la science ---- */}
      <EtudesScientifiques />

      {/* ---- Le parcours en bref ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <p className="etiquette">Un accompagnement pensé par des pairs</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">
            Un appel suffit pour enclencher un vrai parcours d’aide
          </h2>
        </Reveal>
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {[
            {
              titre: '1 · Vous appelez',
              texte:
                'La ligne dédiée répond 7 jours sur 7. Un répondant formé vous écoute, sans jugement et sans dossier à remplir.',
            },
            {
              titre: '2 · Un pair vous reçoit',
              texte:
                'Un médecin effecteur — formé au soin des soignants — vous propose un entretien confraternel strictement confidentiel.',
            },
            {
              titre: '3 · Vous avancez, accompagné·e',
              texte:
                'Santé, travail, organisation : un accompagnement global sur plusieurs semaines, avec un objectif — retrouver votre autonomie.',
            },
          ].map((e, i) => (
            <Reveal key={e.titre} delay={i * 110}>
              <article className="carte h-full border-t-4 !border-t-sapin">
                <h3 className="font-bold text-marine">{e.titre}</h3>
                <p className="mt-2 text-encre/75">{e.texte}</p>
              </article>
            </Reveal>
          ))}
        </div>
        <Reveal className="mt-8">
          <Link href="/aide-accompagnement" className="bouton-secondaire">
            Découvrir le dispositif complet →
          </Link>
        </Reveal>
      </section>

      {/* ---- Vidéo officielle ---- */}
      <section className="bg-sable/60 py-16">
        <div className="conteneur grid items-center gap-10 lg:grid-cols-2">
          <Reveal>
            <p className="etiquette">En vidéo</p>
            <h2 className="titre-section mt-3 text-marine">Prendre soin des soignants, c’est un métier</h2>
            <p className="mt-4 text-encre/75">
              L’association MOTS est née à Toulouse, portée par des médecins convaincus qu’un
              soignant en difficulté doit pouvoir parler à un pair qui comprend son quotidien.
              Cette vidéo officielle résume l’esprit du dispositif.
            </p>
            <p className="mt-4 text-encre/75">
              Chaque médecin effecteur est formé — notamment via le diplôme inter-universitaire
              « Soigner les soignants », co-créé à l’initiative de l’association en 2015.
            </p>
          </Reveal>
          <Reveal delay={120}>
            <LiteYouTube videoId={YOUTUBE_ID} title="Association MOTS, prendre soin des soignants" />
          </Reveal>
        </div>
      </section>

      {/* ---- À qui s'adresse MOTS ---- */}
      <section className="conteneur py-16">
        <Reveal>
          <p className="etiquette">Depuis 2018, tous les soignants à ordre professionnel</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">MOTS s’adresse à vous</h2>
        </Reveal>
        <Reveal delay={100}>
          <ul className="mt-8 flex flex-wrap gap-3">
            {PROFESSIONS.map((p) => (
              <li key={p} className="rounded-full border border-sapin/25 bg-white px-4 py-2 font-medium text-sapin">
                {p}
              </li>
            ))}
          </ul>
        </Reveal>
        <Reveal delay={180}>
          <p className="mt-6 max-w-2xl text-encre/75">
            Épuisement professionnel, surinvestissement, problème de santé, addiction, difficultés
            administratives, financières ou juridiques : quelle que soit la porte d’entrée,
            l’accompagnement est gratuit et confidentiel.
          </p>
        </Reveal>
      </section>

      {/* ---- Bandeau final ---- */}
      <section className="conteneur pb-4 pt-2">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-marine p-10 text-white sm:p-14">
            <div aria-hidden="true" className="orbe -right-20 -top-20 h-64 w-64 bg-accent/30" />
            <h2 className="titre-section relative max-w-xl">Le premier pas tient en dix chiffres.</h2>
            <p className="relative mt-3 max-w-xl text-white/80">
              Vous hésitez pour vous-même, ou vous vous inquiétez pour un confrère ou une consœur ?
              Appelez : la conversation reste entre soignants.
            </p>
            <div className="relative mt-7 flex flex-wrap gap-4">
              <a href={TEL_HREF} className="bouton-appel !px-8 !py-4 text-lg">
                {TEL_AFFICHE} — 7 j/7
              </a>
              <Link href="/je-deviens-adherent" className="bouton-secondaire !border-white/30 !bg-white/10 !text-white hover:!bg-white/20">
                Soutenir l’association
              </Link>
            </div>
          </div>
        </Reveal>
      </section>
    </>
  )
}
