import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV === 'production')
      return [{ source: '/api/:path*', destination: '/api/' }];
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
      // Add your S3 bucket for production
      // {
      //   protocol: 'https',
      //   hostname: 'your-bucket.s3.amazonaws.com',
      //   pathname: '/media/**',
      // },
    ],
  },
};

export default nextConfig;
