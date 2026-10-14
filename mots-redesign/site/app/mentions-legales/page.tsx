import Link from 'next/link'
import PageHero from '@/components/PageHero'
import Reveal from '@/components/Reveal'
import { SITE_OFFICIEL } from '@/lib/infos'

export const metadata = {
  title: 'Mentions légales',
  description:
    'Mentions légales de cette démonstration de refonte : nature du site, propriété des contenus, données personnelles et référencement.',
}

export default function MentionsLegalesPage() {
  return (
    <>
      <PageHero
        surtitre="Transparence"
        titre="Mentions légales"
        intro="Cette page précise le statut exact de ce site, l’origine de ses contenus et les choix techniques retenus en matière de données personnelles et de référencement."
      />

      {/* ---- Nature du site ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <h2 className="titre-section text-marine">Nature du site</h2>
          <div className="carte mt-6 border-l-4 !border-l-accent">
            <p className="text-encre/80">
              Ce site est une <strong>démonstration de refonte</strong> : une proposition
              graphique et éditoriale réalisée à titre d’exercice. Il ne s’agit
              <strong> ni d’un site officiel, ni d’un site affilié</strong> à l’Association MOTS
              (Médecin-Organisation-Travail-Santé), et son contenu n’a été ni commandé ni validé
              par elle.
            </p>
            <p className="mt-3 text-encre/80">
              Aucune information publiée ici ne saurait engager l’association. Pour toute
              démarche réelle, reportez-vous à son site officiel :{' '}
              <a
                href={SITE_OFFICIEL}
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold text-sapin underline underline-offset-4 hover:text-accent-fonce"
              >
                association-mots.org
              </a>
              .
            </p>
          </div>
        </Reveal>
      </section>

      {/* ---- Contenus et propriété intellectuelle ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <h2 className="titre-section text-marine">Contenus et propriété intellectuelle</h2>
        </Reveal>
        <div className="mt-6 grid gap-5 md:grid-cols-2">
          <Reveal>
            <article className="carte h-full">
              <h3 className="font-bold text-marine">Des textes originaux</h3>
              <p className="mt-2 text-encre/75">
                Les textes de cette démonstration ont été rédigés à partir d’informations
                publiquement disponibles, sans reproduction du site officiel de l’association.
              </p>
            </article>
          </Reveal>
          <Reveal delay={110}>
            <article className="carte h-full">
              <h3 className="font-bold text-marine">Ce qui appartient à l’association</h3>
              <p className="mt-2 text-encre/75">
                Le nom, l’identité et les contenus officiels de l’Association MOTS appartiennent à
                l’Association MOTS. Toute référence les concernant renvoie à{' '}
                <a
                  href={SITE_OFFICIEL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-semibold text-sapin underline underline-offset-4 hover:text-accent-fonce"
                >
                  son site officiel
                </a>
                .
              </p>
            </article>
          </Reveal>
        </div>
      </section>

      {/* ---- Vidéo intégrée ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <h2 className="titre-section text-marine">Vidéo intégrée</h2>
          <div className="carte mt-6">
            <p className="text-encre/80">
              La vidéo présentée sur ce site provient de la chaîne YouTube officielle de
              l’association. Elle est intégrée via une façade sans cookie (« youtube-nocookie ») :
              aucun contenu n’est chargé depuis YouTube tant que vous ne cliquez pas explicitement
              sur le lecteur.
            </p>
          </div>
        </Reveal>
      </section>

      {/* ---- Données personnelles ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <h2 className="titre-section text-marine">Données personnelles</h2>
        </Reveal>
        <div className="mt-6 grid gap-5 md:grid-cols-3">
          {[
            {
              titre: 'Aucune collecte',
              texte:
                'Ce site ne collecte aucune donnée personnelle : pas de compte, pas de mesure d’audience, pas de profilage.',
            },
            {
              titre: 'Ni cookie, ni traceur',
              texte:
                'Aucun cookie n’est déposé et aucun traceur tiers n’est embarqué lors de votre navigation.',
            },
            {
              titre: 'Formulaire désactivé',
              texte:
                'Le formulaire de contact est volontairement désactivé : rien de ce que vous pourriez y saisir n’est transmis ni conservé.',
            },
          ].map((d, i) => (
            <Reveal key={d.titre} delay={i * 110}>
              <article className="carte h-full border-t-4 !border-t-sapin">
                <h3 className="font-bold text-marine">{d.titre}</h3>
                <p className="mt-2 text-encre/75">{d.texte}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---- Référencement et hébergement ---- */}
      <section className="conteneur py-14">
        <Reveal>
          <h2 className="titre-section text-marine">Référencement et hébergement</h2>
        </Reveal>
        <div className="mt-6 grid gap-5 md:grid-cols-2">
          <Reveal>
            <article className="carte h-full">
              <h3 className="font-bold text-marine">Référencement</h3>
              <p className="mt-2 text-encre/75">
                Ce site est volontairement exclu de l’indexation par les moteurs de recherche
                (directive « noindex »), afin d’éviter toute confusion avec le site officiel de
                l’association.
              </p>
            </article>
          </Reveal>
          <Reveal delay={110}>
            <article className="carte h-full">
              <h3 className="font-bold text-marine">Hébergement</h3>
              <p className="mt-2 text-encre/75">
                Les informations relatives à l’hébergeur (raison sociale, adresse, contact) seront
                complétées au moment du déploiement de cette démonstration.
              </p>
            </article>
          </Reveal>
        </div>
      </section>

      {/* ---- Retour ---- */}
      <section className="conteneur pb-16 pt-4">
        <Reveal>
          <Link href="/" className="bouton-secondaire">
            <span aria-hidden="true">← </span>
            Retour à l’accueil
          </Link>
        </Reveal>
      </section>
    </>
  )
}
