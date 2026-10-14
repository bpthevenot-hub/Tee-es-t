import Link from 'next/link'
import PageHero from '@/components/PageHero'
import Reveal from '@/components/Reveal'
import { TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

export const metadata = {
  title: 'Actualités',
  description:
    'Les temps forts de l’association MOTS : journées nationales, formations interprofessionnelles et déploiement de l’outil d’autoévaluation OASIS.',
}

const EVENEMENTS = [
  {
    date: '26–28 septembre 2024',
    titre: 'Journées MOTS à Villeneuve-lez-Avignon',
    texte:
      'Les rencontres nationales de l’association ont réuni son réseau pendant trois jours à Villeneuve-lez-Avignon, autour des échanges entre pairs qui font la force du dispositif.',
  },
  {
    date: '2024',
    titre: 'MOTS lance OASIS, l’autoévaluation en ligne',
    texte:
      'L’association a lancé OASIS, un outil d’autoévaluation en ligne qui permet à chacun de faire le point sur sa situation, à son rythme — un premier pas discret avant, si besoin, de décrocher son téléphone.',
  },
  {
    date: 'Temps de formation',
    titre: 'Journées de formation interprofessionnelles',
    texte:
      'Des journées de formation ont rassemblé les différentes professions engagées dans le dispositif : un temps privilégié pour croiser les regards et consolider les pratiques d’accompagnement.',
  },
  {
    date: 'Temps du réseau',
    titre: 'Journée nationale',
    texte:
      'Le réseau s’est également retrouvé lors d’une journée nationale — un temps commun consacré à ce qui fonde l’association : la santé de celles et ceux qui soignent.',
  },
  {
    date: '2020',
    titre: 'MOTS fête ses 10 ans',
    texte:
      'Dix ans après sa création à Toulouse en 2010, l’association a célébré une décennie d’écoute et d’accompagnement confidentiel des professionnels de santé en difficulté.',
  },
]

export default function Actualites() {
  return (
    <>
      <PageHero
        surtitre="La vie de l’association"
        titre="Actualités & événements"
        intro="Journées nationales, formations, projets au long cours : retrouvez ici les temps forts qui font vivre MOTS et le soin des soignants."
      />

      {/* ---- Frise des temps forts ---- */}
      <section className="conteneur py-14" aria-label="Temps forts de l’association">
        <Reveal>
          <p className="etiquette">Archive des temps forts</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">
            Ce qui a marqué les dernières années
          </h2>
        </Reveal>
        <ol className="relative mt-10 space-y-8 border-l-2 border-sapin/20 pl-6 sm:pl-10">
          {EVENEMENTS.map((e, i) => (
            <li key={e.titre} className="relative">
              <span
                aria-hidden="true"
                className="absolute -left-[31px] top-8 h-3 w-3 rounded-full border-2 border-white bg-sapin sm:-left-[47px]"
              />
              <Reveal delay={i * 90}>
                <article className="carte">
                  <p className="text-sm font-semibold uppercase tracking-wide text-sapin">{e.date}</p>
                  <h3 className="mt-2 text-lg font-bold text-marine">{e.titre}</h3>
                  <p className="mt-2 text-encre/75">{e.texte}</p>
                </article>
              </Reveal>
            </li>
          ))}
        </ol>
      </section>

      {/* ---- En continu ---- */}
      <section className="bg-sable/60 py-14">
        <div className="conteneur">
          <Reveal>
            <p className="etiquette">Et en continu</p>
            <h2 className="titre-section mt-3 max-w-2xl text-marine">
              « On soigne mieux quand on va bien »
            </h2>
          </Reveal>
          <Reveal delay={100}>
            <div className="carte mt-8 border-t-4 !border-t-accent">
              <p className="text-encre/75">
                Au-delà des rendez-vous ponctuels, l’association anime des formations « On soigne
                mieux quand on va bien » avec des communautés professionnelles territoriales de
                santé — pour parler de la santé des soignants au plus près du terrain, là où ils
                exercent.
              </p>
            </div>
          </Reveal>
          <Reveal delay={180}>
            <p className="mt-8 rounded-2xl border border-dashed border-encre/15 bg-white/60 px-5 py-4 text-sm text-brume">
              Démonstration — cette rubrique sera synchronisée avec l’actualité réelle de
              l’association.
            </p>
          </Reveal>
        </div>
      </section>

      {/* ---- Bandeau final ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-marine p-10 text-white sm:p-14">
            <div aria-hidden="true" className="orbe -right-20 -top-20 h-64 w-64 bg-accent/30" />
            <h2 className="titre-section relative max-w-xl">L’actualité peut attendre. Pas vous.</h2>
            <p className="relative mt-3 max-w-xl text-white/80">
              Si vous traversez une période difficile, un répondant formé vous écoute 7 jours sur
              7, gratuitement et en toute confidentialité.
            </p>
            <div className="relative mt-7 flex flex-wrap gap-4">
              <a href={TEL_HREF} className="bouton-appel !px-8 !py-4 text-lg">
                Appeler le {TEL_AFFICHE}
              </a>
              <Link href="/aide-accompagnement" className="bouton-secondaire !border-white/30 !bg-white/10 !text-white hover:!bg-white/20">
                Comment ça se passe ?
              </Link>
            </div>
          </div>
        </Reveal>
      </section>
    </>
  )
}
