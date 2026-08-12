# Yang Photography Website

Astro + Tailwind portfolio website, deployed on Vercel. Booking requests are
handled by the Vercel function in `api/booking.js`.

## Project layout

- `src/` — pages, layout, and the JSON data that defines albums and home-page images.
- `public/images/` — published, web-optimised WebP assets used by the live site.
- `Website_Queue/` — local intake area for photos waiting to be added to the site.
  Images in this folder are deliberately ignored by Git.
- `scripts/` — project utilities. Old Gemini-era photo scripts are kept under
  `scripts/legacy-photo-tools/` for reference only.
- `docs/` — operating notes, including the Website Queue workflow.
- `workspace/` — a bounded area for experiments, notes, test media, and their
  generated output.

## Local development

```bash
npm install
npm run dev
npm run build
```

## Publishing photos

1. Put selected photos into the matching folder in `Website_Queue/`.
2. Read [docs/WEBSITE_QUEUE.md](docs/WEBSITE_QUEUE.md) for the folder roles.
3. Ask Codex to sync the Queue. Codex will create WebP files and thumbnails,
   update `src/data/albums.json` / home-page data, test the build, and deploy.

Do not put unprocessed source photos directly in `public/images/`; that
directory is the generated, published asset library.

## Booking storage

Booking requests are validated by `api/booking.js`, verified by Cloudflare
Turnstile, then written to the existing Google Apps Script / Google Sheet
workflow. The related environment variables are configured in Vercel.

## SEO

`@astrojs/sitemap` generates the sitemap at build time, and `public/robots.txt`
advertises it to search engines.
