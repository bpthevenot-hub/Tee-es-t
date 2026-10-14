import Link from 'next/link'
import PageHero from '@/components/PageHero'
import Reveal from '@/components/Reveal'
import Accordion, { type AccordionItem } from '@/components/Accordion'
import { TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

export const metadata = {
  title: 'FAQ',
  description:
    'Les réponses aux questions les plus fréquentes sur l’association MOTS : qui peut appeler, coût, confidentialité, déroulé de l’accompagnement, OASIS et façons de soutenir.',
}

const FAQ_ITEMS: AccordionItem[] = [
  {
    question: 'Qui peut appeler MOTS ?',
    reponse:
      'Depuis 2018, le dispositif est ouvert aux neuf professions de santé à ordre : médecins, infirmiers, chirurgiens-dentistes, masseurs-kinésithérapeutes, pharmaciens, pédicures-podologues, sages-femmes, orthoptistes et biologistes. Quel que soit votre mode d’exercice ou votre spécialité, la ligne vous est ouverte. Un seul appel suffit pour être écouté·e.',
  },
  {
    question: 'Combien cela coûte-t-il ?',
    reponse:
      'Rien : l’accompagnement est entièrement gratuit pour le soignant qui appelle. Le dispositif repose sur un esprit d’entraide confraternelle — des pairs qui prennent soin de leurs pairs. Aucune facture, aucune avance de frais, aucune contrepartie ne vous sera demandée.',
  },
  {
    question: 'Mon appel restera-t-il vraiment confidentiel ?',
    reponse:
      'Oui, la confidentialité est stricte et constitue le socle du dispositif. Ce qui se dit lors de l’entretien confraternel reste entre vous et le médecin qui vous reçoit. Vous pouvez parler librement de votre santé, de votre travail ou de vos difficultés, sans crainte que cela circule.',
  },
  {
    question: 'Que se passe-t-il concrètement après mon appel ?',
    reponse:
      'Votre appel est d’abord pris par un répondant formé, qui vous écoute et recueille votre situation. Il vous met ensuite en relation avec un médecin effecteur, qui vous propose un entretien confraternel. C’est ce médecin qui construit avec vous la suite de l’accompagnement, à votre rythme.',
  },
  {
    question: 'Qui sont les médecins effecteurs ?',
    reponse:
      'Ce sont des pairs : des médecins qui connaissent la réalité du soin et qui se sont spécifiquement formés à l’accompagnement des soignants. Beaucoup sont notamment passés par le diplôme inter-universitaire « Soigner les soignants ». Vous parlez donc à quelqu’un qui comprend votre quotidien professionnel.',
  },
  {
    question: 'Puis-je appeler pour un confrère ou une consœur qui m’inquiète ?',
    reponse:
      'Oui, et c’est même un réflexe précieux. Si le comportement ou l’état d’un confrère ou d’une consœur vous préoccupe, vous pouvez contacter MOTS pour en parler et être conseillé·e sur la manière de l’aider. S’inquiéter pour un pair fait aussi partie de l’entraide confraternelle.',
  },
  {
    question: 'Qu’est-ce qu’OASIS ?',
    reponse:
      'OASIS est un outil numérique d’autoévaluation lancé en 2024. Il permet à un professionnel de santé de faire le point sur sa situation, en quelques minutes et en toute autonomie. C’est une première étape utile pour prendre conscience d’une difficulté, avant — ou en complément — d’un appel.',
  },
  {
    question: 'MOTS intervient-elle partout en France ?',
    reponse:
      'Oui, le dispositif est national : où que vous exerciez, vous pouvez appeler. Le siège de l’association se trouve à Toulouse, mais l’accompagnement n’est pas limité à une région. La distance n’est donc jamais un obstacle pour être aidé·e.',
  },
  {
    question: 'Comment puis-je soutenir l’association ?',
    reponse:
      'La façon la plus simple est d’adhérer à l’association via la plateforme HelloAsso — toutes les modalités sont détaillées sur la page « Devenir adhérent » de ce site. Chaque adhésion renforce la capacité de MOTS à écouter et accompagner des soignants en difficulté. En parler autour de vous est aussi une aide précieuse.',
  },
  {
    question: 'Et si ma situation n’est pas « assez grave » ?',
    reponse:
      'Il n’existe pas de seuil de gravité pour appeler : toute difficulté mérite une écoute. Fatigue qui s’installe, doutes, tensions au travail, question de santé — mieux vaut en parler tôt que d’attendre que la situation s’aggrave. Appeler n’engage à rien d’autre qu’une conversation.',
  },
]

// Données structurées FAQPage (schema.org) : mêmes questions que l'accordéon.
const FAQ_JSON_LD = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: FAQ_ITEMS.map((item) => ({
    '@type': 'Question',
    name: item.question,
    acceptedAnswer: { '@type': 'Answer', text: item.reponse },
  })),
}

export default function Faq() {
  return (
    <>
      <PageHero
        surtitre="FAQ"
        titre="Vos questions, nos réponses"
        intro="Avant d’appeler, il est normal de vouloir savoir à quoi s’attendre. Voici, en toute transparence, les réponses aux questions que l’on nous pose le plus souvent."
      />

      <section className="conteneur py-14">
        <Reveal>
          <h2 className="titre-section text-marine">Dix questions pour tout comprendre</h2>
          <p className="mt-4 max-w-2xl text-encre/75">
            Cliquez sur une question pour dérouler la réponse. Et si la vôtre n’y figure pas, le
            plus simple reste d’appeler — ou de{' '}
            <Link
              href="/nous-ecrire"
              className="font-semibold text-sapin underline underline-offset-4 hover:text-accent-fonce"
            >
              nous écrire
            </Link>
            .
          </p>
        </Reveal>
        <Reveal className="mt-8" delay={120}>
          <Accordion items={FAQ_ITEMS} />
        </Reveal>
      </section>

      {/* ---- Bandeau final ---- */}
      <section className="conteneur pb-16 pt-2">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-marine p-10 text-white sm:p-14">
            <div aria-hidden="true" className="orbe -right-20 -top-20 h-64 w-64 bg-accent/30" />
            <h2 className="titre-section relative max-w-xl">
              Une question à laquelle seule une voix peut répondre ?
            </h2>
            <p className="relative mt-3 max-w-xl text-white/80">
              Un répondant formé vous écoute, gratuitement et en toute confidentialité. Le premier
              pas, c’est un appel.
            </p>
            <div className="relative mt-7 flex flex-wrap gap-4">
              <a href={TEL_HREF} className="bouton-appel !px-8 !py-4 text-lg">
                Appeler le {TEL_AFFICHE}
              </a>
              <Link href="/je-deviens-adherent" className="bouton-secondaire !border-white/30 !bg-white/10 !text-white hover:!bg-white/20">
                Soutenir l’association
              </Link>
            </div>
          </div>
        </Reveal>
      </section>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(FAQ_JSON_LD) }}
      />
    </>
  )
}
