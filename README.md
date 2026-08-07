# Yang Photography Portfolio

攝影師作品集、服務方案與預約網站。使用 Astro、Tailwind CSS 與 Vercel 部署。

## Local development

```bash
npm install
npm run dev
npm run build
```

Portfolio pages are generated as static HTML and cached by Vercel. `api/booking.js` is a Vercel serverless function for booking requests.

## Booking storage

Booking requests are validated by `api/booking.js` and then written to the existing Google Apps Script / Google Sheet workflow. No email-service key is required.

## Photo publishing workflow

1. Place source images in `../Albums`.
2. Run `python photo_process.py` from this directory.
3. Review the generated `public/images/albums` assets and `src/data/*.json`.
4. Build and deploy.

`photo_process.py` creates WebP output sized for the website:

- Hero images: up to 2560px
- Portfolio images: up to 1600px
- Thumbnails: up to 800px

To deliberately regenerate every image after changing processing settings, run:

```powershell
$env:FORCE_REPROCESS='1'; python photo_process.py
```

## SEO

`@astrojs/sitemap` generates the sitemap at build time and `public/robots.txt` advertises it to search engines.
