import Link from 'next/link'
import PageHero from '@/components/PageHero'
import Reveal from '@/components/Reveal'
import { HELLOASSO_URL, TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

export const metadata = {
  title: 'Je deviens adhérent',
  description:
    'Adhérer à l’association MOTS, c’est faire vivre une ligne d’écoute 7 j/7 pour les professionnels de santé en difficulté et soutenir la prévention de l’épuisement des soignants.',
}

const RAISONS = [
  {
    titre: 'Faire vivre la ligne d’écoute',
    texte:
      'Votre adhésion contribue directement au fonctionnement d’une ligne dédiée aux soignants, joignable 7 jours sur 7 par celles et ceux qui traversent une période difficile.',
  },
  {
    titre: 'Renforcer le réseau d’effecteurs',
    texte:
      'Derrière chaque appel, il y a des médecins effecteurs formés au soin des soignants. Adhérer, c’est aider ce réseau de pairs à grandir et à rester disponible.',
  },
  {
    titre: 'Porter la prévention',
    texte:
      'L’association agit aussi en amont : sensibiliser, prévenir l’épuisement professionnel et rappeler que la santé des soignants est l’affaire de tous.',
  },
]

const USAGES = [
  {
    titre: 'Le fonctionnement de la ligne',
    texte: 'Maintenir une écoute disponible 7 j/7, confidentielle et sans condition.',
  },
  {
    titre: 'La formation des effecteurs',
    texte: 'Former les médecins qui reçoivent et accompagnent leurs pairs en difficulté.',
  },
  {
    titre: 'Les outils du dispositif',
    texte: 'Développer les outils qui soutiennent l’accompagnement, comme OASIS.',
  },
  {
    titre: 'Les journées de rencontre',
    texte: 'Réunir le réseau pour partager les pratiques et faire avancer la cause.',
  },
]

const PUBLICS = [
  {
    titre: 'Aux professionnels de santé',
    texte:
      'Soignants en exercice ou retraités, sensibles à la santé de leurs pairs — que vous ayez ou non déjà fait appel au dispositif.',
  },
  {
    titre: 'Aux institutions',
    texte:
      'Structures, établissements et organisations professionnelles qui souhaitent s’engager aux côtés des soignants.',
  },
  {
    titre: 'À toute personne',
    texte:
      'Chacun peut adhérer ou donner, tout simplement parce que la cause lui tient à cœur : sans soignants en bonne santé, pas de soin.',
  },
]

export default function JeDeviensAdherent() {
  return (
    <>
      <PageHero
        surtitre="Adhésion & soutien"
        titre="Rejoignez celles et ceux qui prennent soin des soignants"
        intro="Adhérer à MOTS, c’est donner à un professionnel de santé en difficulté la certitude qu’une voix répondra, aujourd’hui comme demain. Chaque adhésion compte, chaque don aussi."
      >
        <div className="flex flex-wrap items-center gap-4">
          <a
            href={HELLOASSO_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="bouton-appel !px-8 !py-4 text-lg"
          >
            Adhérer ou faire un don en ligne
          </a>
          <Link href="/nous-ecrire" className="bouton-secondaire">
            Nous écrire
          </Link>
        </div>
        <p className="mt-4 text-sm text-encre/60">
          L’adhésion et le don se font sur HelloAsso (site externe, ouverture dans un nouvel onglet).
        </p>
      </PageHero>

      {/* ---- Pourquoi adhérer ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <p className="etiquette">Pourquoi adhérer</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">Une adhésion, trois effets concrets</h2>
        </Reveal>
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {RAISONS.map((r, i) => (
            <Reveal key={r.titre} delay={i * 110}>
              <article className="carte h-full border-t-4 !border-t-sapin">
                <h3 className="font-bold text-marine">{r.titre}</h3>
                <p className="mt-2 text-encre/75">{r.texte}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---- Qui peut adhérer ---- */}
      <section className="bg-sable/60 py-16">
        <div className="conteneur">
          <Reveal>
            <p className="etiquette">Qui peut adhérer</p>
            <h2 className="titre-section mt-3 max-w-2xl text-marine">
              L’association est ouverte à toutes les bonnes volontés
            </h2>
            <p className="mt-4 max-w-2xl text-encre/75">
              Nul besoin d’être médecin pour soutenir MOTS. L’adhésion est ouverte :
            </p>
          </Reveal>
          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {PUBLICS.map((p, i) => (
              <Reveal key={p.titre} delay={i * 110}>
                <article className="carte h-full">
                  <h3 className="font-bold text-marine">{p.titre}</h3>
                  <p className="mt-2 text-encre/75">{p.texte}</p>
                </article>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ---- À quoi sert l'adhésion ---- */}
      <section className="conteneur py-16">
        <Reveal>
          <p className="etiquette">À quoi sert votre adhésion</p>
          <h2 className="titre-section mt-3 max-w-2xl text-marine">Votre soutien se traduit en actions</h2>
        </Reveal>
        <div className="mt-10 grid gap-5 sm:grid-cols-2">
          {USAGES.map((u, i) => (
            <Reveal key={u.titre} delay={i * 90}>
              <article className="carte h-full">
                <h3 className="font-bold text-marine">{u.titre}</h3>
                <p className="mt-2 text-encre/75">{u.texte}</p>
              </article>
            </Reveal>
          ))}
        </div>
        <Reveal className="mt-10">
          <div className="carte flex flex-wrap items-center justify-between gap-6">
            <div>
              <h3 className="font-bold text-marine">Prêt·e à franchir le pas ?</h3>
              <p className="mt-1 max-w-xl text-encre/75">
                L’adhésion comme le don se font en quelques minutes en ligne. Une question avant de
                vous décider ? Écrivez-nous, nous vous répondrons.
              </p>
            </div>
            <div className="flex flex-wrap gap-4">
              <a href={HELLOASSO_URL} target="_blank" rel="noopener noreferrer" className="bouton-appel">
                Adhérer sur HelloAsso
              </a>
              <Link href="/nous-ecrire" className="bouton-secondaire">
                Nous écrire
              </Link>
            </div>
          </div>
        </Reveal>
      </section>

      {/* ---- Bandeau final ---- */}
      <section className="conteneur pb-4 pt-2">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-marine p-10 text-white sm:p-14">
            <div aria-hidden="true" className="orbe -right-20 -top-20 h-64 w-64 bg-accent/30" />
            <h2 className="titre-section relative max-w-xl">Besoin d’aide ? N’attendez pas d’adhérer.</h2>
            <p className="relative mt-3 max-w-xl text-white/80">
              L’accompagnement de MOTS ne dépend d’aucune adhésion : si vous traversez une période
              difficile, appelez. La ligne répond 7 jours sur 7, en toute confidentialité.
            </p>
            <div className="relative mt-7">
              <a href={TEL_HREF} className="bouton-appel !px-8 !py-4 text-lg">
                Appeler le {TEL_AFFICHE}
              </a>
            </div>
          </div>
        </Reveal>
      </section>
    </>
  )
}
