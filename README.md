# blackwellboy.github.io

Public site for the Blackwellboy identity, served by GitHub Pages from `main`.
No framework and no client JavaScript.

Live: https://blackwellboy.github.io/

## Information architecture

The site is deliberately a curated public layer over the GitHub repos rather than a copy of them.

- `index.html` — Home: wordmark, positioning, live Minefield stats, services, contact
- `work.html` — strongest deployments, failure files, selected research, reproduction links
- `models.html` — model wall, with evidence-depth labels: deployment, campaign, targeted test, control
- `tools.html` — diagnosis workflow, Minefield tools, playbooks, deployment references and integrity
- `about.html` — rack-to-runtime background, test taxonomy, hardware/runtimes, external uptake
- `corrections.html` — retractions, narrowed claims and correction propagation

The source for each page is its matching `*.template.html`; generated `*.html` files are committed because GitHub Pages serves directly from the branch.

## Editorial rules

The website tells the story; GitHub holds the receipts.

- Lead with the result or the failure mechanism, not a wall of methodology.
- Keep exact conditions attached to fixed-run measurements.
- Do not turn a lane-specific speed result into a universal model-speed claim.
- Do not turn upstream, contributor or registry evidence into a first-hand claim.
- The Models page must preserve evidence depth. A targeted test is not a full campaign.
- Negative results and corrections are first-class work, not footnotes.
- Dense methodology belongs in `<details>` blocks or the linked repository, not in the first paragraph a visitor sees.
- Facts about the current state of `model-serving-minefield` should be generated from that repository rather than typed by hand.

## Design rules

The front-page visual identity is deliberate. `site.css` keeps the existing dark palette, typography, sodium measurement accent, neon section headings, card chrome and wordmark treatment.

Do not casually:

- change the colour tokens or font stack;
- replace/restyle the front-page wordmark image;
- spend the sodium accent on decorative UI;
- hide primary navigation behind an invisible horizontal scroller;
- turn the site into generic marketing cards or a GitHub README mirror.

Keep these front-page assets and the current `img.plate` / `srcset` / `sizes` arrangement intact:

- `blackwellboy-1400.jpg`
- `blackwellboy-900.jpg`
- `blackwellboy-600.jpg`
- `blackwellboy.jpg` (Open Graph / social image)

## Build

Registry-derived tokens (`{{REG_*}}`, contributor counts, doctor checks, etc.) are substituted from a checked-out copy of `model-serving-minefield`.

```bash
python3 build.py --registry /path/to/model-serving-minefield --all
python3 build.py --registry /path/to/model-serving-minefield --all --check
```

On pull requests, CI checks that every generated page matches a fresh render. On `main`, the workflow renders all pages and commits only when the rendered bytes change. Edit templates, not generated files.

`build.py --all` discovers every `*.template.html`, so adding a page means adding both its template and its generated neighbour to the branch; no hard-coded page list is required.

## Public evidence sources used by the site

The site should prefer stable public surfaces:

- `Blackwellboy/model-serving-minefield` — registry, model/stack maps, playbooks, doctor, integrity
- `Blackwellboy/model-serving-minefield-evidence` — scrubbed public study bundles
- `Blackwellboy/laguna-s21-lab` — detailed single-model research programme
- `Blackwellboy/kimi-k3-neuron-tp3-dgxspark-recipe` — public Kimi K3 SparkInfer recipe snapshot
- `Blackwellboy/Hy3-295B-NVFP4-MTP-Dual-DGX-Spark` — Hy3 deployment recipe and measurements
- `Blackwellboy/MiniMax-M3-2x-DGX-Spark-stock-driver` — MiniMax stock-driver lane and failure analysis

Private repos can inform future work, but unpublished private campaign state must not leak onto the public site.

## Custom domain (optional)

To point a custom domain at the site:

1. add a `CNAME` file containing the bare domain;
2. configure DNS for GitHub Pages;
3. set the domain under repository Settings → Pages and enable HTTPS.

Internal asset/page links are relative so branch previews continue to work. Open Graph image URLs are absolute to `https://blackwellboy.github.io/blackwellboy.jpg` and can be changed later if a custom domain becomes canonical.
