import { defineConfig } from "vite";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  root: ".",
  base: "/", // Use '/' for custom domain, or '/bishop-forge/' for github.io/bishop-forge

  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url))
    }
  },

  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: true
  },

  test: {
    globals: true,
    environment: "happy-dom",
    setupFiles: "tests/setup.js",
    include: ["src/**/*.test.js", "tests/**/*.test.js"]
  }
});
