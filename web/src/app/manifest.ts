import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Options Portfolio Monitor',
    short_name: 'Options Monitor',
    description: 'Track your options portfolio and get alerts when positions go in-the-money',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#1f2937',
    orientation: 'portrait-primary',
    icons: [
      {
        src: '/icons/icon-192.png',
        sizes: '192x192',
        type: 'image/png',
        purpose: 'maskable',
      },
      {
        src: '/icons/icon-512.png',
        sizes: '512x512',
        type: 'image/png',
        purpose: 'any',
      },
    ],
    categories: ['finance', 'productivity'],
    screenshots: [
      {
        src: '/screenshots/dashboard.png',
        sizes: '1280x720',
        type: 'image/png',
        form_factor: 'wide',
        label: 'Portfolio Dashboard',
      },
      {
        src: '/screenshots/mobile.png',
        sizes: '750x1334',
        type: 'image/png',
        form_factor: 'narrow',
        label: 'Mobile View',
      },
    ],
  };
}
