import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV === "production") return [
      { source: "/api/:path*", destination: "/api/" },
    ];
    return [
      { source: "/api/:path*", destination: "http://localhost:8000/api/:path*" },
    ];
  },
  reactStrictMode: true,
};

export default nextConfig;
