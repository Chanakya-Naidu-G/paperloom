import type { NextConfig } from "next";

const allowedOrigins =
  process.env.ALLOWED_DEV_ORIGINS
    ?.split(",")
    .map((s) => s.trim())
    .filter(Boolean) ?? [];

const nextConfig: NextConfig = {
  ...(allowedOrigins.length ? { allowedDevOrigins: allowedOrigins } : {}),

  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://13.204.45.15:8000/api/v1/:path*",
      },
    ];
  },
};

export default nextConfig;