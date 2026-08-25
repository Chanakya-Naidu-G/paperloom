import type { NextConfig } from "next";

const allowedOrigins = process.env.ALLOWED_DEV_ORIGINS?.split(",").map((s) => s.trim()).filter(Boolean) ?? [];

const nextConfig: NextConfig = {
  ...(allowedOrigins.length ? { allowedDevOrigins: allowedOrigins } : {}),
};

export default nextConfig;