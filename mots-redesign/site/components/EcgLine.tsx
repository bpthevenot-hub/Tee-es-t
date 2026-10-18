/**
 * Ligne d'électrocardiogramme animée — motif visuel du site.
 * Purement décorative (aria-hidden), tracée une fois au chargement.
 */
export default function EcgLine({ className = '' }: { className?: string }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 600 80"
      fill="none"
      className={`ligne-ecg ${className}`}
      preserveAspectRatio="none"
    >
      <path
        d="M0 40 H150 L170 40 L185 12 L200 68 L215 40 H320 L340 40 L352 24 L364 54 L376 40 H600"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
