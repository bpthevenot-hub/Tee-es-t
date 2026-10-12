import type { MetadataRoute } from 'next'

// Démo privée non affiliée : interdite d'indexation tant que l'association
// n'a pas validé le projet.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: '*', disallow: '/' },
  }
}
