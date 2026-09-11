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
        destination: "https://paperloom-api.myftp.biz/api/v1/:path*",
      },
    ];
  },
};

export default nextConfig;