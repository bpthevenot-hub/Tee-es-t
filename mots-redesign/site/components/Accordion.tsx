/**
 * Accordéon accessible en HTML natif (details/summary) : clavier, lecteurs
 * d'écran et absence de JavaScript sont couverts d'office.
 */
export type AccordionItem = { question: string; reponse: string }

export default function Accordion({ items }: { items: AccordionItem[] }) {
  return (
    <div className="space-y-3">
      {items.map((item) => (
        <details
          key={item.question}
          className="group rounded-2xl border border-encre/8 bg-white shadow-carte open:shadow-carte-haute"
        >
          <summary className="flex cursor-pointer list-none items-center justify-between gap-4 rounded-2xl px-6 py-5 font-semibold text-marine focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sapin [&::-webkit-details-marker]:hidden">
            {item.question}
            <span
              aria-hidden="true"
              className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-ecume text-sapin transition group-open:rotate-45"
            >
              +
            </span>
          </summary>
          <p className="px-6 pb-6 text-encre/80">{item.reponse}</p>
        </details>
      ))}
    </div>
  )
}
