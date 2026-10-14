import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import Link from 'next/link'
import { PRODUIT, MOTS_SITE, SNB_SITE, TEL_3114_AFFICHE, TEL_3114_HREF, TEL_MOTS_AFFICHE, TEL_MOTS_HREF, TEL_SAMU_AFFICHE, TEL_SAMU_HREF } from '@/lib/infos'

export const metadata: Metadata = {
  title: 'Mentions',
  description:
    'Mentions du site de démonstration Relève : nature du site, absence de données et de collecte, non-affiliation, noms et marques, sources, numéros d’urgence, hébergement, contact.',
}

/** Une rubrique : numéro, titre de niveau 2, contenu. */
function Rubrique({ numero, titre, id, children }: { numero: string; titre: string; id: string; children: ReactNode }) {
  return (
    <section id={id} aria-labelledby={`${id}-titre`} className="filet grid gap-x-10 gap-y-3 py-10 sm:grid-cols-[14rem_1fr] sm:py-12">
      <div>
        <p className="etiquette">{numero}</p>
        <h2 id={`${id}-titre`} className="titre titre-bloc mt-2">
          {titre}
        </h2>
      </div>
      <div className="texte flex flex-col gap-3 text-[1rem]">{children}</div>
    </section>
  )
}

/** Lien externe, toujours en nouvel onglet avec noopener. */
function Externe({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className="underline underline-offset-4 hover:text-[var(--mode-accent)]">
      {children} ↗
    </a>
  )
}

export default function Mentions() {
  return (
    <div className="conteneur">
      {/* En-tête */}
      <header className="py-16 sm:py-24">
        <p className="etiquette">Mentions</p>
        <h1 className="titre titre-hero mt-4">Mentions</h1>
        <p className="phrase mt-10 max-w-4xl">Un site de démonstration. Rien n’y est enregistré, rien n’en sort.</p>
        <p className="sourd texte mt-6 text-[1.02rem]">
          Ce que ce site est, ce qu’il ne fait pas, qui l’édite et où trouver les sources. Les numéros à appeler si ça ne va pas sont en rubrique 06.
        </p>
      </header>

      <div className="pb-16 sm:pb-24">
        <Rubrique numero="01" titre="Nature du site" id="nature">
          <p>
            Ce site est une démonstration de produit. Il présente « {PRODUIT} », une clinique digitale du soignant, telle que SNB Consulting propose de la construire. Il n’est pas un service de soin, pas une application en service, pas une offre commerciale ouverte.
          </p>
          <p>
            Éditeur : SNB Consulting, <Externe href={SNB_SITE}>snb.center</Externe>.
          </p>
        </Rubrique>

        <Rubrique numero="02" titre="Données" id="donnees">
          <p>
            Aucune donnée réelle. Les prénoms, dossiers, chiffres de recours et indicateurs affichés sur les écrans de démonstration sont fictifs et pseudonymes ; ils ne correspondent à aucune personne, aucun établissement, aucune association.
          </p>
          <p>
            Aucune collecte. Les écrans interactifs fonctionnent en mémoire, dans votre navigateur, le temps de la page. Ce que vous y saisissez n’est ni enregistré, ni transmis, ni conservé. Fermer l’onglet efface tout.
          </p>
          <p>Aucun cookie, aucun traceur, aucune mesure d’audience, aucune ressource chargée depuis un tiers.</p>
        </Rubrique>

        <Rubrique numero="03" titre="Non affiliation" id="affiliation">
          <p>
            Ce site n’est pas affilié à l’association MOTS (<Externe href={MOTS_SITE}>association-mots.org</Externe>), qui ne l’a ni demandé ni validé. Les chiffres cités sur MOTS sont ceux qu’elle publie elle-même. La page <Link href="/mots" className="underline underline-offset-4 hover:text-[var(--mode-accent)]">Pour MOTS</Link> est une proposition non sollicitée.
          </p>
          <p>
            Ce site n’est pas affilié à Eos Care, clinique digitale d’addictologie dont le modèle est cité comme inspiration. Ce qui en est dit relève d’éléments publics et déclarés, sans vérification indépendante.
          </p>
        </Rubrique>

        <Rubrique numero="04" titre="Noms et marques" id="marques">
          <p>
            « {PRODUIT} » est un nom de travail. Sa disponibilité comme marque n’a pas été vérifiée ; aucune recherche d’antériorité n’a été menée et aucun dépôt n’a été effectué.
          </p>
          <p>
            Les noms d’organisations, de dispositifs, de publications et de services cités sur ce site appartiennent à leurs titulaires et ne sont mentionnés qu’à titre de référence ou de source. C’est le cas, entre autres, de MOTS, Eos Care, NHS Practitioner Health, SPS, Schwartz Rounds, Clariane, Ramsay Santé, Inicea, Mon soutien psy, FHF, DREES, Cour des comptes, APICIL, JLO et Vercel.
          </p>
        </Rubrique>

        <Rubrique numero="05" titre="Sources" id="sources">
          <p>
            Chaque chiffre du site porte sa source. Elles sont réunies, avec leur nature (mesuré ou déclaré) et ce qui reste à mesurer, sur la page{' '}
            <Link href="/preuves" className="underline underline-offset-4 hover:text-[var(--mode-accent)]">
              Preuves
            </Link>
            .
          </p>
          <p>Aucun chiffre de ce site ne provient de Relève, qui n’existe pas encore. Les résultats du produit sont indiqués « à mesurer » partout où la preuve manque.</p>
        </Rubrique>

        <Rubrique numero="06" titre="Si ça ne va pas, maintenant" id="urgences">
          <p>Ce site ne remplace ni un médecin ni un service d’urgence. Deux numéros, gratuits, 24 h/24.</p>
          <ul className="flex flex-col gap-3" aria-label="Numéros d’urgence">
            <li>
              <a href={TEL_3114_HREF} className="bouton bouton-3114">
                {TEL_3114_AFFICHE} — prévention du suicide
              </a>
            </li>
            <li>
              <a href={TEL_SAMU_HREF} className="bouton bouton-second">
                {TEL_SAMU_AFFICHE} — SAMU, urgence médicale
              </a>
            </li>
          </ul>
          <p className="sourd text-[0.92rem]">
            Un médecin pair, 7 j/7, confidentiel :{' '}
            <a href={TEL_MOTS_HREF} className="donnee underline underline-offset-4 text-[var(--mode-texte)]">
              {TEL_MOTS_AFFICHE}
            </a>{' '}
            (association MOTS).
          </p>
        </Rubrique>

        <Rubrique numero="07" titre="Hébergement" id="hebergement">
          <p>
            Site hébergé pour la durée de la démonstration, sur Vercel. Aucun hébergement de données de santé n’est engagé : il n’y a aucune donnée à héberger.
          </p>
          <p>Le site n’est pas indexé par les moteurs de recherche.</p>
        </Rubrique>

        <Rubrique numero="08" titre="Contact" id="contact">
          <p>
            Pour une question, une correction ou une démonstration : <Externe href={SNB_SITE}>snb.center</Externe>.
          </p>
          <p className="sourd text-[0.92rem]">Aucun formulaire sur ce site. Aucune adresse n’y est collectée.</p>
        </Rubrique>
      </div>
    </div>
  )
}
