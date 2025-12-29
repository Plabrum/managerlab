import withBundleAnalyzer from '@next/bundle-analyzer';
import type { NextConfig } from 'next';

/**
 * Base Next.js configuration.
 * Add your rewrites, images, and other settings here.
 */
const baseConfig: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV === 'production') {
      return [
        {
          source: '/api/:path*',
          destination: '/api/', // proxy to same origin in production
        },
      ];
    }

    // In development, proxy API requests to the backend
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },

  reactStrictMode: true,

  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/local-download/**',
      },
      // Uncomment and customize for production S3 bucket
      // {
      //   protocol: 'https',
      //   hostname: 'your-bucket.s3.amazonaws.com',
      //   pathname: '/media/**',
      // },
    ],
  },
};

/**
 * Wrap with bundle analyzer when ANALYZE=true
 */
const withAnalyzer = withBundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

export default withAnalyzer(baseConfig);
