import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Vercel optimization
  output: 'standalone',

  // Disable TypeScript checking for build
  typescript: {
    ignoreBuildErrors: true,
  },

  // Disable ESLint checking for build
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8082',
  },

  // API rewrites for development (only if API_URL is set)
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!apiUrl || apiUrl === 'http://localhost:8082') {
      return [];
    }

    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
