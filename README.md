# Eleni Karagianni: portfolio

Architectural engineer and computational designer in London.

Live site: https://www.eleni-karagianni.com

## Structure

- `index.html`, `about/`, and one folder per project (`nine-acts/`, `night-walk/`, …) are plain static pages.
- `assets/site.css` and `assets/site.js` are the only stylesheet and script. The script is small (video play/pause, lightbox, YouTube on click) and every page works without it.
- `media/` holds images (WebP) and short clips (H.264 MP4), one folder per project.
- `nightwalk/` is the Night Walk prototype, a separate app.
- `_build/build.py` generates the pages from the content defined in it: `python3 _build/build.py`.

Deployed on Vercel from `main`. The previous one-page version is kept on the `archive-v1` branch.
