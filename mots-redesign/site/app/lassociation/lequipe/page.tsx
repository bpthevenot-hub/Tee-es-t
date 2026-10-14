import Link from 'next/link'
import PageHero from '@/components/PageHero'
import Reveal from '@/components/Reveal'
import { TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

export const metadata = {
  title: 'L’équipe',
  description:
    'Répondants formés, médecins effecteurs, pôle médico-technique, équipe administrative et conseil d’administration : les rôles qui font vivre l’accompagnement MOTS.',
}

const ROLES = [
  {
    surtitre: 'Premier maillon',
    titre: 'Les répondants téléphoniques',
    texte:
      'Formés à l’écoute, ils accueillent chaque appel sur la ligne dédiée. Leur rôle : entendre ce qui se passe, sans jugement ni formalité, puis orienter vers la suite du parcours. C’est par eux que tout commence.',
  },
  {
    surtitre: 'Cœur du dispositif',
    titre: 'Les médecins effecteurs',
    texte:
      'Médecins en activité, spécifiquement formés au soin des soignants — beaucoup via le diplôme inter-universitaire « Soigner les soignants » —, ils mènent les entretiens confraternels et assurent l’accompagnement dans la durée. Un pair qui comprend votre quotidien, en toute confidentialité.',
  },
  {
    surtitre: 'Expertise',
    titre: 'Le pôle médico-technique',
    texte:
      'Il appuie les accompagnements sur le plan médical et organisationnel : coordination des situations, qualité du dispositif, lien entre les différents intervenants du parcours.',
  },
  {
    surtitre: 'Coulisses',
    titre: 'L’équipe administrative',
    texte:
      'Gestion, logistique, suivi au quotidien : l’équipe administrative fait tourner l’association pour que les soignants accompagnés — et ceux qui les accompagnent — puissent se concentrer sur l’essentiel.',
  },
  {
    surtitre: 'Gouvernance',
    titre: 'Le conseil d’administration',
    texte:
      'Composé de soignants bénévoles, il porte les orientations de l’association et veille à la fidélité au principe fondateur : des soignants qui prennent soin des soignants.',
    pleineLargeur: true,
  },
]

export default function LEquipePage() {
  return (
    <>
      <PageHero
        surtitre="L’association"
        titre="L’équipe"
        intro="Derrière chaque appel, une chaîne de personnes engagées : des répondants qui accueillent, des médecins formés qui accompagnent, et des équipes qui font vivre le dispositif au quotidien."
      />

      <nav aria-label="Fil d’Ariane" className="conteneur pt-8">
        <ol className="flex flex-wrap items-center gap-2 text-sm text-brume">
          <li>
            <Link href="/lassociation" className="font-medium text-sapin hover:underline">
              L’association
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li aria-current="page">L’équipe</li>
        </ol>
      </nav>

      {/* ---- Les rôles ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <p className="etiquette">Qui fait quoi</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">
            Une chaîne d’écoute, du premier appel à l’accompagnement
          </h2>
          <p className="mt-4 max-w-2xl text-encre/75">
            Chaque rôle a sa place dans le parcours. Ensemble, ils garantissent la même promesse : une
            écoute confraternelle, confidentielle et gratuite.
          </p>
        </Reveal>
        <div className="mt-10 grid gap-5 md:grid-cols-2">
          {ROLES.map((r, i) => (
            <Reveal key={r.titre} delay={i * 90} className={r.pleineLargeur ? 'md:col-span-2' : undefined}>
              <article className="carte h-full border-t-4 !border-t-sapin">
                <p className="text-sm font-bold tracking-wide text-sapin">{r.surtitre}</p>
                <h3 className="mt-1 font-bold text-marine">{r.titre}</h3>
                <p className="mt-2 text-encre/75">{r.texte}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---- Rejoindre l'équipe ---- */}
      <section className="conteneur pb-14">
        <Reveal>
          <div className="carte border-t-4 !border-t-accent bg-sable/60">
            <p className="text-sm font-bold tracking-wide text-accent-fonce">Rejoindre l’équipe</p>
            <h2 className="titre-section mt-2 max-w-2xl text-marine">Devenir médecin effecteur</h2>
            <p className="mt-3 max-w-2xl text-encre/75">
              Tout médecin en activité peut candidater pour devenir médecin effecteur et, après une
              formation dédiée, accompagner à son tour des confrères et consœurs en difficulté.
            </p>
            <div className="mt-6">
              <Link href="/nous-ecrire" className="bouton-secondaire">
                Nous écrire pour candidater →
              </Link>
            </div>
          </div>
        </Reveal>
      </section>

      {/* ---- Bandeau final ---- */}
      <section className="conteneur pb-16 pt-2">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-marine p-10 text-white sm:p-14">
            <div aria-hidden="true" className="orbe -right-20 -top-20 h-64 w-64 bg-accent/30" />
            <h2 className="titre-section relative max-w-xl">Toute cette équipe est à un appel de vous.</h2>
            <p className="relative mt-3 max-w-xl text-white/80">
              Vous traversez une période difficile, ou vous vous inquiétez pour un confrère ou une
              consœur ? Un répondant formé vous écoute, en toute confidentialité.
            </p>
            <div className="relative mt-7 flex flex-wrap gap-4">
              <a href={TEL_HREF} className="bouton-appel !px-8 !py-4 text-lg">
                Appeler le {TEL_AFFICHE}
              </a>
              <Link href="/lassociation" className="bouton-secondaire !border-white/30 !bg-white/10 !text-white hover:!bg-white/20">
                Découvrir l’association
              </Link>
            </div>
          </div>
        </Reveal>
      </section>
    </>
  )
}
