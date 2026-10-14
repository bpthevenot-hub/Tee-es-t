import path from 'node:path'
import { fileURLToPath } from 'node:url'

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Le monorepo contient d'autres package.json : on fixe la racine de tracing.
  outputFileTracingRoot: path.dirname(fileURLToPath(import.meta.url)),
  // Démonstration : jamais indexée.
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Robots-Tag', value: 'noindex, nofollow' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'X-Frame-Options', value: 'DENY' },
        ],
      },
    ]
  },
}

export default nextConfig
