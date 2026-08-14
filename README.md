# blackwellboy.github.io

Public site for the Blackwellboy identity, served by GitHub Pages from `main`.
No framework and no client JavaScript.

Live: https://blackwellboy.github.io/

## Pages

- `index.html` — front page: wordmark, short positioning, generated registry stats, services, contact
- `about.html` — background, lab philosophy, measured stacks, independent uptake
- `work.html` — research studies and public deployment recipes
- `tools.html` — Minefield, Core, doctor, template preflight, playbooks and integrity
- `corrections.html` — retractions, narrowed claims and corrections

The source for each page is its matching `*.template.html`; generated `*.html`
files are committed because GitHub Pages serves directly from the branch.

## Design rules

The front-page visual identity is deliberate. `site.css` keeps the existing dark
palette, typography, sodium measurement accent, neon section headings and card chrome.

Do not casually:

- change the colour tokens or font stack;
- replace/restyle the front-page wordmark image;
- spend the sodium accent on decorative UI;
- turn the evidence pages into generic marketing cards.

The navigation is wider than the reading column on desktop and wraps on mobile so
external links such as GitHub remain visible instead of being hidden behind a
horizontal-scroll area.

## Content rules

- Lead with the result; keep methodology attached rather than burying it elsewhere.
- Dense work-card conditions live in native `<details>` blocks so the page is scannable
  without deleting the evidence.
- Fixed-run measurements stay hand-written with their build/hardware conditions.
- Facts about the current state of `model-serving-minefield` are generated from that
  repository at build time.
- Corrections stay public and are linked to the claim they changed.

## Build

Registry-derived tokens (`{{REG_*}}`, contributor counts, doctor checks, etc.) are
substituted from a checked-out copy of `model-serving-minefield`.

```bash
python3 build.py --registry /path/to/model-serving-minefield --all
python3 build.py --registry /path/to/model-serving-minefield --all --check
```

On pull requests, CI checks that every generated page matches a fresh render. On
`main`, the workflow renders all pages and commits only when the rendered bytes change.
Edit templates, not generated files.

## Front-page image

Keep these assets and the current `img.plate` / `srcset` / `sizes` arrangement intact:

- `blackwellboy-1400.jpg`
- `blackwellboy-900.jpg`
- `blackwellboy-600.jpg`
- `blackwellboy.jpg` (Open Graph / social image)

## Custom domain (optional)

To point a custom domain at the site:

1. add a `CNAME` file containing the bare domain;
2. configure DNS for GitHub Pages;
3. set the domain under repository Settings → Pages and enable HTTPS.

Internal asset/page links are relative so branch previews continue to work. Open Graph
image URLs are absolute to `https://blackwellboy.github.io/blackwellboy.jpg` and can be
changed later if a custom domain becomes canonical.
