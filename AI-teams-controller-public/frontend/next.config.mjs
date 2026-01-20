/** @type {import('next').NextConfig} */
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:17063'

// Build version: timestamp at build time for cache debugging
const buildVersion = new Date().toISOString().replace('T', ' ').substring(0, 19)

const nextConfig = {
  experimental: {
    // Skip problematic page data collection phase
    workerThreads: false,
    cpus: 1,
  },
  env: {
    NEXT_PUBLIC_BUILD_VERSION: buildVersion,
  },
  // Disable Turbopack - use webpack for more reliable builds
  // turbopack: { root: process.cwd() },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  devIndicators: false,
  // Allow external origins (Cloudflare tunnel) in development
  allowedDevOrigins: [
    'https://voice-ui.hungson175.com',
    'http://voice-ui.hungson175.com',
  ],
  async rewrites() {
    return {
      // beforeFiles rewrites run before pages/public files are checked
      // but after API routes, so our local API routes take precedence
      beforeFiles: [
        {
          source: '/health',
          destination: `${backendUrl}/health`,
        },
      ],
      // fallback rewrites run after pages/public files
      fallback: [
        {
          source: '/api/:path*',
          destination: `${backendUrl}/api/:path*`,
        },
      ],
    }
  },
}

export default nextConfig
