# blackwellboy.github.io

Public site for the Blackwellboy identity, served by GitHub Pages from the
`main` branch of this repo. No framework, no client JavaScript.

Live: https://blackwellboy.github.io/

## Pages

- `index.html` — front page (photo, lede, generated registry stats, Available for, Contact)
- `about.html` — background, fleet and serving‑stacks copy (first‑person)
- `work.html` — selected studies plus public recipe cards (with conditions)
- `corrections.html` — “What I got wrong”
- `tools.html` — registry, playbooks, doctor, preflight, integrity, operators guide

The shared CSS lives in `site.css`. The look is deliberate:

- Do not restyle the theme: keep the existing colour tokens, fonts, neon‑on‑h2,
  card chrome and sodium rules exactly as they are.
- Do not remove, replace or restyle the wordmark photo on the front page. Keep
  `blackwellboy-1400.jpg` / `-900` / `-600` exactly as in the template: same
  `img.plate`, same `srcset`, same `sizes`, same `alt`.
- The accent is used for three things only: measured values, link underlines,
  and the bar beside a conditions line.

## Templates and build

Humans edit templates, not generated HTML.

- Source templates: `*.template.html` (one per page)
- Generated files: `*.html`
- Registry‑derived tokens (`{{REG_*}}`) are substituted at build time from a
  checked‑out copy of `model-serving-minefield`.

Local build/check:

```bash
python3 build.py --registry /path/to/model-serving-minefield --all
python3 build.py --registry /path/to/model-serving-minefield --all --check
```

CI:

- Pull requests run a check that all generated `*.html` files match a fresh
  render. If you edit a generated file directly, CI fails with a message to
  edit the corresponding `*.template.html` instead.
- On `main` (push or schedule), CI renders all pages and commits only when the
  rendered bytes change.

## Content discipline

- The registry stats are generated on build so they cannot silently go stale.
- Study figures are hand‑written with their conditions and links to raw data.
- The `work.html` recipe cards copy their numbers and conditions from public
  READMEs; do not invent a figure that is not stated there.

## Custom domain (optional)

To point a custom domain (for example `blackwellboy.ai`) at this site:

1. Add `CNAME` at the repo root with the bare domain (e.g. `blackwellboy.ai`).
2. Configure DNS (CNAME `www` to `blackwellboy.github.io`, or A records for the apex).
3. In repo Settings → Pages, set the custom domain and enable Enforce HTTPS.

Asset URLs are relative so the site works unmodified on either domain. Open‑Graph
image URLs are absolute (`https://blackwellboy.github.io/blackwellboy.jpg`);
change them only if you want unfurls to show the custom domain.
