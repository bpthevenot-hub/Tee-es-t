import Link from 'next/link'
import PageHero from '@/components/PageHero'
import Reveal from '@/components/Reveal'
import { PROFESSIONS, TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

export const metadata = {
  title: 'L’association',
  description:
    'Née en 2010 à Toulouse, l’association MOTS accompagne gratuitement et en toute confidentialité les professionnels de santé en difficulté. Découvrez son histoire, ses valeurs et son équipe.',
}

const PILIERS = [
  {
    lettre: 'M',
    titre: 'Médecin',
    texte:
      'L’accompagnement est porté par des médecins : un soignant en difficulté parle à un pair qui connaît son quotidien, ses contraintes et son langage.',
  },
  {
    lettre: 'O',
    titre: 'Organisation',
    texte:
      'Charge de travail, rythme, structure d’exercice : l’organisation professionnelle est souvent au cœur des difficultés — elle est regardée en tant que telle.',
  },
  {
    lettre: 'T',
    titre: 'Travail',
    texte:
      'Le travail peut épuiser comme il peut réparer. L’accompagnement s’attache à en refaire un lieu tenable, et si possible une ressource.',
  },
  {
    lettre: 'S',
    titre: 'Santé',
    texte:
      'La santé du soignant — physique comme psychique — n’est jamais un détail. Elle est le point de départ et la finalité de la démarche.',
  },
]

const VALEURS = [
  {
    titre: 'Entraide confraternelle',
    texte: 'Des soignants qui aident d’autres soignants, d’égal à égal, sans jugement.',
  },
  {
    titre: 'Confidentialité stricte',
    texte: 'Ce qui est confié à MOTS reste à MOTS. C’est la condition première de la confiance.',
  },
  {
    titre: 'Gratuité de l’accompagnement',
    texte: 'Aucune contrepartie financière n’est demandée à la personne accompagnée.',
  },
  {
    titre: 'Approche globale de la personne',
    texte: 'Santé, travail, organisation : les difficultés sont regardées ensemble, pas isolément.',
  },
]

export default function LAssociationPage() {
  return (
    <>
      <PageHero
        surtitre="Qui sommes-nous ?"
        titre="Une association de soignants, au service des soignants"
        intro="MOTS est née d’une conviction simple : un professionnel de santé en difficulté doit pouvoir se tourner vers des pairs, en toute confidentialité et sans rien débourser."
      />

      {/* ---- Origines ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <p className="etiquette">Pourquoi MOTS existe</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">
            Née en 2010 à Toulouse, d’une prise de conscience collective
          </h2>
        </Reveal>
        <div className="mt-8 grid gap-10 lg:grid-cols-2">
          <Reveal>
            <p className="text-encre/75">
              L’association a vu le jour en 2010 à Toulouse, à l’initiative du conseil départemental
              de l’Ordre des médecins de Haute-Garonne. Le constat était partagé : ceux qui prennent
              soin des autres peinent souvent à demander de l’aide pour eux-mêmes.
            </p>
            <p className="mt-4 text-encre/75">
              Son nom résume son approche : <strong className="text-marine">M</strong>édecin,{' '}
              <strong className="text-marine">O</strong>rganisation,{' '}
              <strong className="text-marine">T</strong>ravail,{' '}
              <strong className="text-marine">S</strong>anté — quatre piliers pour accompagner la
              personne dans sa globalité, et pas seulement son symptôme.
            </p>
            <p className="mt-4 text-encre/75">
              Depuis 2018, l’accompagnement est ouvert à l’ensemble des professions de santé dotées
              d’un ordre professionnel.
            </p>
          </Reveal>
          <Reveal delay={120}>
            <div className="carte h-full">
              <h3 className="font-bold text-marine">Ouverte à toutes les professions de santé à ordre</h3>
              <ul className="mt-4 flex flex-wrap gap-2">
                {PROFESSIONS.map((p) => (
                  <li
                    key={p}
                    className="rounded-full border border-sapin/25 bg-white px-3 py-1.5 text-sm font-medium text-sapin"
                  >
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ---- Valeurs ---- */}
      <section className="bg-sable/60 py-14">
        <div className="conteneur">
          <Reveal>
            <p className="etiquette">Ce qui ne se négocie pas</p>
            <h2 className="titre-section mt-3 max-w-2xl text-marine">Quatre valeurs fondatrices</h2>
          </Reveal>
          <div className="mt-8 grid gap-5 sm:grid-cols-2">
            {VALEURS.map((v, i) => (
              <Reveal key={v.titre} delay={i * 90}>
                <article className="carte h-full">
                  <h3 className="font-bold text-marine">{v.titre}</h3>
                  <p className="mt-2 text-encre/75">{v.texte}</p>
                </article>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ---- Les quatre piliers ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <p className="etiquette">Un nom qui dit tout</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">
            Les quatre lettres de MOTS, les quatre piliers de l’accompagnement
          </h2>
        </Reveal>
        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {PILIERS.map((p, i) => (
            <Reveal key={p.lettre} delay={i * 110}>
              <article className="carte h-full border-t-4 !border-t-sapin">
                <p aria-hidden="true" className="text-4xl font-bold tracking-tight text-sapin">
                  {p.lettre}
                </p>
                <h3 className="mt-2 font-bold text-marine">{p.titre}</h3>
                <p className="mt-2 text-encre/75">{p.texte}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---- Aller plus loin ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <p className="etiquette">Aller plus loin</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">Mieux connaître l’association</h2>
        </Reveal>
        <div className="mt-8 grid gap-5 md:grid-cols-2">
          <Reveal>
            <Link
              href="/lassociation/notre-histoire"
              className="carte group block h-full transition hover:shadow-carte-haute"
            >
              <h3 className="font-bold text-marine">Notre histoire</h3>
              <p className="mt-2 text-encre/75">
                De la création à Toulouse en 2010 à l’ouverture à toutes les professions de santé à
                ordre : les étapes qui ont façonné MOTS.
              </p>
              <p className="mt-4 font-semibold text-sapin group-hover:underline">Parcourir notre histoire →</p>
            </Link>
          </Reveal>
          <Reveal delay={120}>
            <Link
              href="/lassociation/lequipe"
              className="carte group block h-full transition hover:shadow-carte-haute"
            >
              <h3 className="font-bold text-marine">L’équipe</h3>
              <p className="mt-2 text-encre/75">
                Répondants, médecins effecteurs, bénévoles : celles et ceux qui font vivre l’entraide
                confraternelle au quotidien.
              </p>
              <p className="mt-4 font-semibold text-sapin group-hover:underline">Rencontrer l’équipe →</p>
            </Link>
          </Reveal>
        </div>
      </section>

      {/* ---- Bandeau final ---- */}
      <section className="conteneur pb-14 pt-2">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-marine p-10 text-white sm:p-14">
            <div aria-hidden="true" className="orbe -right-20 -top-20 h-64 w-64 bg-accent/30" />
            <h2 className="titre-section relative max-w-xl">Vous traversez une période difficile ?</h2>
            <p className="relative mt-3 max-w-xl text-white/80">
              Un appel suffit pour parler à un pair. La conversation est confidentielle,
              l’accompagnement est gratuit.
            </p>
            <div className="relative mt-7 flex flex-wrap gap-4">
              <a href={TEL_HREF} className="bouton-appel !px-8 !py-4 text-lg">
                Appeler le {TEL_AFFICHE}
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
