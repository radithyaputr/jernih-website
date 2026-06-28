import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  experimental: {
    // Improve performance for production builds
  },
};

export default nextConfig;
