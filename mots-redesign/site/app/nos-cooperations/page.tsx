import Link from 'next/link'
import PageHero from '@/components/PageHero'
import Reveal from '@/components/Reveal'
import { TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

export const metadata = {
  title: 'Nos coopérations',
  description:
    'Ordres professionnels, universités, entraide confraternelle, institutions de la santé : découvrez les coopérations qui permettent à MOTS d’accompagner les professionnels de santé en difficulté.',
}

const FAMILLES = [
  {
    titre: 'Les ordres des professions de santé',
    texte:
      'MOTS travaille en lien étroit avec les conseils des ordres des professions de santé, relais naturels vers les soignants en difficulté. Ce lien est fondateur : le conseil départemental de l’Ordre des médecins de Haute-Garonne est à l’origine de la création de l’association.',
  },
  {
    titre: 'L’université',
    texte:
      'Avec les facultés de médecine de Toulouse et de Paris Diderot, l’association a co-créé en 2015 le diplôme inter-universitaire « Soigner les soignants ». Cette formation prépare les médecins à une clinique singulière : celle du soignant devenu patient.',
  },
  {
    titre: 'L’entraide confraternelle',
    texte:
      'MOTS s’inscrit dans un paysage plus large d’entraide entre soignants. L’association coopère avec les structures d’entraide confraternelle, pour que chaque professionnel en difficulté trouve la porte d’entrée qui lui convient, sans jamais rester seul.',
  },
  {
    titre: 'Les acteurs institutionnels de la santé',
    texte:
      'Caisses de retraite et de protection sociale des professions de santé, unions régionales, communautés professionnelles territoriales : l’association dialogue avec les acteurs institutionnels pour faire connaître le dispositif et faciliter l’orientation des soignants.',
  },
]

export default function NosCooperations() {
  return (
    <>
      <PageHero
        surtitre="Nos coopérations"
        titre="On accompagne mieux quand on coopère"
        intro="Aider un soignant en difficulté demande un maillage solide : ordres professionnels, universités, structures d’entraide, institutions de la santé. MOTS avance avec eux, au service d’un même objectif — qu’aucun professionnel de santé ne reste seul face à ses difficultés."
      />

      {/* ---- Les quatre familles de coopération ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <p className="etiquette">Un réseau au service des soignants</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">Quatre familles de coopération</h2>
          <p className="mt-4 max-w-2xl text-encre/75">
            Chacune de ces coopérations joue un rôle précis : orienter les soignants vers
            l’association, former celles et ceux qui les accompagnent, ou consolider le dispositif
            dans la durée.
          </p>
        </Reveal>
        <div className="mt-10 grid gap-5 sm:grid-cols-2">
          {FAMILLES.map((f, i) => (
            <Reveal key={f.titre} delay={i * 100}>
              <article className="carte h-full border-t-4 !border-t-sapin">
                <h3 className="font-bold text-marine">{f.titre}</h3>
                <p className="mt-2 text-encre/75">{f.texte}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---- Formations partagées ---- */}
      <section className="bg-sable/60 py-14">
        <div className="conteneur">
          <Reveal>
            <p className="etiquette">Se former ensemble</p>
            <h2 className="titre-section mt-3 max-w-2xl text-marine">Des formations partagées sur le terrain</h2>
          </Reveal>
          <div className="mt-8 grid gap-10 lg:grid-cols-2">
            <Reveal>
              <p className="text-encre/75">
                La coopération ne se limite pas aux conventions : elle se vit sur le terrain.
                L’association mène des formations partagées avec des communautés professionnelles
                territoriales de santé, comme «&nbsp;On soigne mieux quand on va bien&nbsp;».
              </p>
              <p className="mt-4 text-encre/75">
                L’idée est simple : un soignant qui prend soin de sa propre santé soigne mieux. Ces
                temps de formation sensibilisent les équipes de terrain, ouvrent la parole sur les
                difficultés du métier et font connaître les ressources d’aide existantes.
              </p>
            </Reveal>
            <Reveal delay={120}>
              <div className="carte h-full">
                <h3 className="font-bold text-marine">«&nbsp;On soigne mieux quand on va bien&nbsp;»</h3>
                <p className="mt-2 text-encre/75">
                  Une formation menée avec des communautés professionnelles territoriales de santé,
                  pour parler prévention, épuisement et santé des soignants — là où ils exercent,
                  entre pairs.
                </p>
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* ---- Coopérer avec MOTS ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <p className="etiquette">Construire ensemble</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">Coopérer avec MOTS</h2>
        </Reveal>
        <Reveal delay={100}>
          <div className="carte mt-8 max-w-3xl">
            <p className="text-encre/75">
              Vous représentez un ordre professionnel, une structure d’entraide, une communauté
              professionnelle territoriale, une institution de la santé ou une équipe de formation ?
              Chaque coopération renforce le filet de sécurité autour des soignants : orientation,
              sensibilisation, formation, soutien au dispositif.
            </p>
            <p className="mt-4 text-encre/75">
              Écrivez-nous pour présenter votre projet : nous étudierons ensemble la forme que peut
              prendre notre collaboration.
            </p>
            <div className="mt-6">
              <Link href="/nous-ecrire" className="bouton-secondaire">
                Nous écrire pour coopérer →
              </Link>
            </div>
          </div>
        </Reveal>
      </section>

      {/* ---- Bandeau final ---- */}
      <section className="conteneur pb-14 pt-2">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-marine p-10 text-white sm:p-14">
            <div aria-hidden="true" className="orbe -right-20 -top-20 h-64 w-64 bg-accent/30" />
            <h2 className="titre-section relative max-w-xl">Et si c’est vous qui avez besoin d’aide ?</h2>
            <p className="relative mt-3 max-w-xl text-white/80">
              Derrière chaque coopération, il y a une seule finalité : vous répondre. Un appel
              suffit — la conversation est confidentielle, l’accompagnement est gratuit.
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
