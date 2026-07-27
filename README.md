# blackwellboy.github.io

Single-page site for the Blackwellboy identity, served by GitHub Pages from
the `main` branch of this repo. No build step, no framework, no external JS:
one `index.html` with inline CSS plus one image.

Live at: https://blackwellboy.github.io/

## Editing

Everything is in `index.html`: the CSS lives in one `<style>` block at the top,
the content below it. There is no build step, so an edit pushed to `main` is
live within a minute or two.

Two conventions worth keeping:

- **Colour tokens carry their measured contrast ratio in a comment.** If you
  change a colour, recompute the ratio against `--ground` and update the
  comment. Nothing a reader sees as a sentence should sit below about 9:1.
- **The accent is used for three things only:** measured values, link
  underlines, and the bar beside a conditions line. Spending it anywhere else
  costs it its meaning.

Every figure on the page is re-derived from the raw data published in the two
linked repos. If a study is updated upstream, re-check the matching line here.

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
