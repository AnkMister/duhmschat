/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // PWA configuration
  experimental: {
    // Enable server actions for form handling
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },

  // Headers for PWA and security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },

  // Rewrites for API proxy to Python backend
  async rewrites() {
    return [
      {
        source: '/api/portfolio/:path*',
        destination: `${process.env.BACKEND_URL || 'http://localhost:8000'}/api/portfolio/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
