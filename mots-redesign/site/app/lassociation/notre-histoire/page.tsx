import Link from 'next/link'
import PageHero from '@/components/PageHero'
import Reveal from '@/components/Reveal'
import { TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

export const metadata = {
  title: 'Notre histoire',
  description:
    'De la création de MOTS à Toulouse en 2010 à plus de 1 700 soignants accompagnés : les grandes étapes d’une association dédiée à la santé des professionnels de santé.',
}

const ETAPES = [
  {
    annee: '2010',
    titre: 'Naissance à Toulouse',
    texte:
      'L’association MOTS voit le jour à Toulouse, à l’initiative du conseil départemental de l’Ordre des médecins de Haute-Garonne. L’intuition fondatrice : un soignant en difficulté doit pouvoir se confier à un pair qui comprend la réalité de son métier.',
  },
  {
    annee: '2015',
    titre: 'Le DIU « Soigner les soignants »',
    texte:
      'MOTS co-crée le diplôme inter-universitaire « Soigner les soignants » avec les facultés de médecine de Toulouse et Paris Diderot. Prendre soin d’un confrère ou d’une consœur devient une compétence qui s’apprend et se transmet.',
  },
  {
    annee: '2018',
    titre: 'Un accompagnement ouvert à tous les soignants à ordre',
    texte:
      'D’abord pensé pour les médecins, le dispositif s’ouvre à l’ensemble des professions de santé à ordre. La conviction reste la même : personne ne devrait affronter seul une période difficile.',
  },
  {
    annee: '2020',
    titre: 'Dix ans d’écoute',
    texte:
      'L’association fête ses dix ans. Une décennie d’appels reçus, d’entretiens confraternels et de parcours d’accompagnement, portée par des médecins spécifiquement formés au soin des soignants.',
  },
  {
    annee: '2024',
    titre: 'OASIS et les Journées MOTS',
    texte:
      'MOTS lance OASIS, un outil numérique d’autoévaluation pour les soignants, et réunit son réseau lors des Journées MOTS à Villeneuve-lez-Avignon. Le dispositif continue de s’outiller et de fédérer.',
  },
]

export default function NotreHistoirePage() {
  return (
    <>
      <PageHero
        surtitre="L’association"
        titre="Notre histoire"
        intro="Depuis 2010, MOTS avance avec une boussole simple : offrir aux professionnels de santé une écoute confraternelle, confidentielle et gratuite. Retour sur les étapes qui ont construit le dispositif."
      />

      <nav aria-label="Fil d’Ariane" className="conteneur pt-8">
        <ol className="flex flex-wrap items-center gap-2 text-sm text-brume">
          <li>
            <Link href="/lassociation" className="font-medium text-sapin hover:underline">
              L’association
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li aria-current="page">Notre histoire</li>
        </ol>
      </nav>

      {/* ---- Frise chronologique ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <p className="etiquette">De 2010 à aujourd’hui</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">Les grandes étapes du dispositif</h2>
          <p className="mt-4 max-w-2xl text-encre/75">
            Chaque jalon raconte la même progression : élargir l’accompagnement, professionnaliser
            l’écoute et rester fidèle au principe fondateur — des soignants qui prennent soin des
            soignants.
          </p>
        </Reveal>
        <ol className="relative mt-12 space-y-8 border-l-2 border-sapin/20 pl-8">
          {ETAPES.map((e, i) => (
            <li key={e.annee} className="relative">
              <span
                aria-hidden="true"
                className="absolute -left-[39px] top-7 h-3.5 w-3.5 rounded-full bg-sapin ring-4 ring-sapin/15"
              />
              <Reveal delay={i * 90}>
                <article className="carte">
                  <p className="text-sm font-bold tracking-wide text-sapin">{e.annee}</p>
                  <h3 className="mt-1 font-bold text-marine">{e.titre}</h3>
                  <p className="mt-2 text-encre/75">{e.texte}</p>
                </article>
              </Reveal>
            </li>
          ))}
          <li className="relative">
            <span
              aria-hidden="true"
              className="point-vif absolute -left-[39px] top-7 h-3.5 w-3.5 rounded-full bg-accent"
            />
            <Reveal delay={ETAPES.length * 90}>
              <article className="carte border-t-4 !border-t-accent">
                <p className="text-sm font-bold tracking-wide text-accent-fonce">Aujourd’hui</p>
                <h3 className="mt-1 font-bold text-marine">Plus de 1 700 soignants accompagnés</h3>
                <p className="mt-2 text-encre/75">
                  L’histoire continue de s’écrire, un appel à la fois. Derrière ce chiffre, il y a des
                  parcours singuliers — et, à chaque fois, une même porte d’entrée : une conversation
                  entre pairs.
                </p>
              </article>
            </Reveal>
          </li>
        </ol>
      </section>

      {/* ---- Bandeau final ---- */}
      <section className="conteneur pb-16 pt-2">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-marine p-10 text-white sm:p-14">
            <div aria-hidden="true" className="orbe -right-20 -top-20 h-64 w-64 bg-accent/30" />
            <h2 className="titre-section relative max-w-xl">Et si le prochain chapitre était le vôtre ?</h2>
            <p className="relative mt-3 max-w-xl text-white/80">
              Vous traversez une période difficile, ou vous vous inquiétez pour un confrère ou une
              consœur ? Un appel suffit : l’échange reste confidentiel, entre soignants.
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
