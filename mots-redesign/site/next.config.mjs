import path from 'node:path'
import { fileURLToPath } from 'node:url'

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Le repo parent (Tee-es-t) contient d'autres package.json : on fixe la racine
  // de tracing pour eviter que Next remonte au monorepo.
  outputFileTracingRoot: path.dirname(fileURLToPath(import.meta.url)),
  // Demo privee : on renforce le noindex au niveau HTTP en plus du robots.ts.
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
