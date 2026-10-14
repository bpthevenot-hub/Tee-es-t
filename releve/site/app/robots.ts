import type { MetadataRoute } from 'next'

// Démonstration : jamais indexée.
export default function robots(): MetadataRoute.Robots {
  return { rules: { userAgent: '*', disallow: '/' } }
}
