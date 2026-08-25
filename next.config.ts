import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output used by container-oriented builds.
  output: 'standalone',
  distDir: 'dist',

  typescript: {
    ignoreBuildErrors: false,
  },

  // ESLint is not configured in this repo; do not pretend the build lints.
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Experimental features for hydration
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },

  // Enable styled-components transform (better classnames and SSR)
  compiler: {
    styledComponents: true,
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
