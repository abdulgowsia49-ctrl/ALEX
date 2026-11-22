// OPTIONAL Cloudflare Pages "advanced mode" worker (NOT tested in the authoring environment).
// Serves the built SPA and proxies the API paths to the host that runs backend/main.py
// (for example a Hugging Face Space). Set API_ORIGIN in Pages > Settings > Variables,
// e.g. https://YOUR-USER-arkagni.hf.space  (no trailing slash).
const API = /^\/(results|config|version|health|ingestion|observations|harmonize|live-analysis|audit|docs|openapi\.json)(\/|$)/;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (API.test(url.pathname)) {
      if (!env.API_ORIGIN) return new Response('API_ORIGIN is not configured', { status: 503 });
      const target = new URL(url.pathname + url.search, env.API_ORIGIN);
      return fetch(new Request(target, request));
    }
    return env.ASSETS.fetch(request);
  },
};
