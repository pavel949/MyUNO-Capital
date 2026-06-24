/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Ensure the Founder Console always has a backend URL baked in at build time.
  // Vercel's project env (or vercel.json build.env) overrides this; the fallback
  // is the deployed FastAPI backend so production never points at localhost.
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "https://my-uno-capital-backend.vercel.app",
  },
};

module.exports = nextConfig;
