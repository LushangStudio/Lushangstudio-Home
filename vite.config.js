import { readFileSync } from "node:fs";
import { defineConfig } from "vite";
import { minify } from "html-minifier-terser";

// Keep apps.json as an independently editable file in the production bundle.
function applicationCatalog() {
  return {
    name: "application-catalog",
    generateBundle() {
      this.emitFile({
        type: "asset",
        fileName: "apps.json",
        source: JSON.stringify(
          JSON.parse(
            readFileSync(new URL("./apps.json", import.meta.url), "utf8"),
          ).filter(
            (application) =>
              !(process.env.HOME_EXCLUDE_APPS || "").split(",").includes(application.id),
          ),
        ),
      });
    },
  };
}

export default defineConfig({
  plugins: [
    applicationCatalog(),
    {
      name: "minify-html",
      apply: "build",
      transformIndexHtml: {
        order: "post",
        handler: (html) =>
          minify(html, {
            collapseWhitespace: true,
            removeComments: true,
            minifyCSS: true,
            minifyJS: true,
          }),
      },
    },
  ],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    minify: "esbuild",
    cssMinify: true,
    sourcemap: false,
  },
  server: {
    proxy: {
      "/leave": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/leave/, ""),
      },
      "/api": "http://127.0.0.1:8000",
      // The workspace launcher serves the original WordTxT build.
      "/wordtxt": "http://127.0.0.1:8080",
    },
  },
});
