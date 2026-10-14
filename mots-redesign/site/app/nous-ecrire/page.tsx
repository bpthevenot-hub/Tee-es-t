import PageHero from '@/components/PageHero'
import Reveal from '@/components/Reveal'
import { ADRESSE, PROFESSIONS, SITE_OFFICIEL, TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

export const metadata = {
  title: 'Nous écrire',
  description:
    'Écrire à l’association MOTS : coordonnées du siège à Toulouse, lien vers le site officiel et rappel de la ligne d’écoute dédiée aux professionnels de santé, joignable 7 j/7.',
}

const CAS_COURRIER = [
  {
    titre: 'Candidature de médecin effecteur',
    texte:
      'Vous êtes médecin et souhaitez rejoindre le réseau de pairs qui reçoivent et accompagnent les soignants en difficulté.',
  },
  {
    titre: 'Proposition de coopération',
    texte:
      'Votre structure, institution ou organisation professionnelle souhaite construire un partenariat avec l’association.',
  },
  {
    titre: 'Demande presse',
    texte:
      'Vous êtes journaliste et préparez un sujet sur la santé des soignants ou sur le dispositif MOTS.',
  },
]

export default function NousEcrirePage() {
  return (
    <>
      <PageHero
        surtitre="Contact"
        titre="Nous écrire"
        intro="Une question sur l’association, une candidature, un projet de coopération ? Cette page réunit nos coordonnées. Et si vous traversez une période difficile, le téléphone reste le chemin le plus court."
      />

      {/* ---- Bandeau d'orientation ---- */}
      <section aria-label="En cas de difficulté" className="conteneur pt-10">
        <Reveal>
          <div className="carte flex flex-wrap items-center justify-between gap-6 border-l-4 !border-l-sapin">
            <div>
              <h2 className="font-bold text-marine">En cas de difficulté, le plus direct reste l’appel</h2>
              <p className="mt-1 max-w-xl text-encre/75">
                La ligne d’écoute répond 7 jours sur 7 : un répondant formé vous écoute, en toute
                confidentialité. N’attendez pas qu’un courrier fasse le trajet.
              </p>
            </div>
            <a href={TEL_HREF} className="bouton-appel">
              Appeler le {TEL_AFFICHE}
            </a>
          </div>
        </Reveal>
      </section>

      {/* ---- Formulaire (démonstration) et coordonnées ---- */}
      <section className="conteneur py-14">
        <div className="grid gap-10 lg:grid-cols-2">
          <Reveal>
            <h2 className="titre-section text-marine">Votre message</h2>
            <p className="mt-3 text-encre/75">
              Ce formulaire illustre le parcours de contact envisagé pour le futur site.
            </p>
            <form className="carte mt-6 space-y-5" aria-describedby="note-demo">
              <div>
                <label htmlFor="nom" className="block font-medium text-marine">
                  Votre nom
                </label>
                <input
                  type="text"
                  id="nom"
                  name="nom"
                  autoComplete="name"
                  placeholder="Prénom et nom"
                  className="mt-2 w-full rounded-xl border border-encre/15 bg-white px-4 py-3 text-encre placeholder:text-brume focus:border-sapin focus:outline-none"
                />
              </div>
              <div>
                <label htmlFor="profession" className="block font-medium text-marine">
                  Votre profession
                </label>
                <select
                  id="profession"
                  name="profession"
                  defaultValue=""
                  className="mt-2 w-full rounded-xl border border-encre/15 bg-white px-4 py-3 text-encre focus:border-sapin focus:outline-none"
                >
                  <option value="" disabled>
                    Sélectionnez votre profession
                  </option>
                  {PROFESSIONS.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                  <option value="autre">Autre</option>
                </select>
              </div>
              <div>
                <label htmlFor="email" className="block font-medium text-marine">
                  Votre adresse e-mail
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  autoComplete="email"
                  placeholder="vous@exemple.fr"
                  className="mt-2 w-full rounded-xl border border-encre/15 bg-white px-4 py-3 text-encre placeholder:text-brume focus:border-sapin focus:outline-none"
                />
              </div>
              <div>
                <label htmlFor="message" className="block font-medium text-marine">
                  Votre message
                </label>
                <textarea
                  id="message"
                  name="message"
                  rows={6}
                  placeholder="Écrivez votre message ici…"
                  className="mt-2 w-full rounded-xl border border-encre/15 bg-white px-4 py-3 text-encre placeholder:text-brume focus:border-sapin focus:outline-none"
                />
              </div>
              <button type="button" disabled className="bouton-appel w-full cursor-not-allowed opacity-50">
                Envoyer le message
              </button>
              <p id="note-demo" className="text-sm text-encre/60">
                Formulaire désactivé dans cette démonstration — aucune donnée n’est collectée.
              </p>
            </form>
          </Reveal>

          <Reveal delay={120}>
            <h2 className="titre-section text-marine">Nos coordonnées</h2>
            <p className="mt-3 text-encre/75">
              Le courrier reste le bon canal pour les démarches qui demandent un écrit.
            </p>
            <div className="carte mt-6">
              <h3 className="font-bold text-marine">Adresse du siège</h3>
              <address className="mt-2 not-italic text-encre/75">
                Association MOTS
                <br />
                {ADRESSE.ligne1}
                <br />
                {ADRESSE.ligne2}
                <br />
                {ADRESSE.ville}
              </address>
            </div>
            <div className="carte mt-5">
              <h3 className="font-bold text-marine">Site officiel</h3>
              <p className="mt-2 text-encre/75">
                Cette démonstration ne remplace pas le site de l’association. Pour toute
                information de référence, consultez&nbsp;:
              </p>
              <a
                href={SITE_OFFICIEL}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 inline-block font-medium text-sapin underline underline-offset-4 hover:text-accent-fonce"
              >
                association-mots.org (site officiel, nouvel onglet)
              </a>
            </div>
            <div className="carte mt-5">
              <h3 className="font-bold text-marine">Dans quels cas nous écrire ?</h3>
              <ul className="mt-3 space-y-4">
                {CAS_COURRIER.map((c) => (
                  <li key={c.titre}>
                    <p className="font-medium text-marine">{c.titre}</p>
                    <p className="mt-1 text-encre/75">{c.texte}</p>
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ---- Appel final ---- */}
      <section className="conteneur pb-4 pt-2">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-marine p-10 text-white sm:p-14">
            <div aria-hidden="true" className="orbe -right-20 -top-20 h-64 w-64 bg-accent/30" />
            <h2 className="titre-section relative max-w-xl">Un courrier peut attendre. Pas vous.</h2>
            <p className="relative mt-3 max-w-xl text-white/80">
              Si écrire est un détour et que la période est difficile, décrochez simplement votre
              téléphone : la conversation reste entre soignants, en toute confidentialité.
            </p>
            <div className="relative mt-7">
              <a href={TEL_HREF} className="bouton-appel !px-8 !py-4 text-lg">
                Appeler le {TEL_AFFICHE} — 7 j/7
              </a>
            </div>
          </div>
        </Reveal>
      </section>
    </>
  )
}
