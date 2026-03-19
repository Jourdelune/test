export default defineNuxtConfig({
  future: {
    compatibilityVersion: 4,
  },
  devtools: { enabled: true },
  alias: {
    '@': '/volatile/home/er284977/Bureau/dev/JUNCO/junco-frontend/app',
  },
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:2024',
    },
  },
})
