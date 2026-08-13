# blackwellboy.github.io

Single-page site for the Blackwellboy identity, served by GitHub Pages from
the `main` branch of this repo. No framework, no external JS.

Live at: https://blackwellboy.github.io/

## Editing

Edit `index.template.html` only. `index.html` is generated.

- `build.py` renders `index.html` from the template by substituting
  `{{REG_*}}` tokens derived from a checked‑out copy of
  `Blackwellboy/model-serving-minefield`.
- On pull requests, CI runs `python3 build.py --check` against a fresh
  registry checkout and fails if `index.html` was hand‑edited.
- On push and on a schedule, `.github/workflows/build.yml` regenerates
  `index.html` and commits only when the rendered bytes actually change.
  A human edit to `index.html` will be reverted by the next scheduled build.

Optional local render:

- `python3 build.py --registry /path/to/model-serving-minefield`
- `python3 build.py --registry /path/to/model-serving-minefield --check`

Two conventions worth keeping:

- **Colour tokens carry their measured contrast ratio in a comment.** If you
  change a colour, recompute the ratio against `--ground` and update the
  comment. Nothing a reader parses as a sentence sits below **12:1**.
- **The accent is used for three things only:** measured values, link
  underlines, and the bar beside a conditions line. Spending it anywhere else
  costs it its meaning.

Figures on the page are re‑derived from the raw data published in the linked
repos. Generated counts come from the registry at build time; fixed‑run
measurements carry their conditions.

## Custom domain later

To point a custom domain (for example blackwellboy.ai) at this site without
changing the page:

1. Add a file named `CNAME` to the repo root containing exactly one line:
   the bare domain (for example `blackwellboy.ai`).
2. At the DNS provider, add either a CNAME record pointing `www` (or the
   apex via ALIAS/ANAME) at `blackwellboy.github.io`, or A records for the
   apex at GitHub Pages IPs (185.199.108.153, 185.199.109.153,
   185.199.110.153, 185.199.111.153).
3. In repo Settings, Pages, set the custom domain and enable Enforce HTTPS
   once the certificate is issued.

The page uses relative URLs for its own assets, so it works unchanged on
either domain. The Open Graph and Twitter image URLs are absolute
(`https://blackwellboy.github.io/blackwellboy.jpg`) and keep working after a
domain move; update them to the new domain only if you want unfurls to show
the custom domain.
