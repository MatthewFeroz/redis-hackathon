# Plumbly dashboard

SvelteKit (static adapter) UI for the Plumbly operator console: review pipeline, jobs, analytics, and live updates. The production build is compiled in the root `Dockerfile` and served by FastAPI from `dashboard-app/build/`.

## Develop

```sh
cd dashboard-app
npm install
npm run dev
```

API requests use same-origin paths (e.g. `/api/...`) against the running FastAPI app.

## Reference

See the repository root [README.md](../README.md) and [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).
