/** @type {import('next').NextConfig} */
const nextConfig = {
  // Отключаем ESLint во время сборки для Render
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Отключаем проверку типов во время сборки
  typescript: {
    ignoreBuildErrors: true,
  },
  // Дополнительные настройки для продакшена
  experimental: {
    optimizeCss: true,
  },
  // Настройки для Render
  output: 'standalone',
  poweredByHeader: false,
}

module.exports = nextConfig 