#!/usr/bin/env python3
"""check_counts.py - verify the registry figures quoted on this site.

The problem, stated exactly
---------------------------
The site quotes numbers that describe a DIFFERENT repository. That repository
moves: its entry count went 42 to 81 to 90 inside one day. A bare count on a
hand-written page is therefore not a fact, it is a decaying estimate, and this
page's closing promise is that every number on it checks out.

The registry's own integrity README settles the convention, and this script
implements it rather than inventing a second one:

    never write a bare count, always write the count and the tip it was
    counted at, so a reader can tell in one command whether it still holds.

So the page says "90 at 249ad34", not "90". That converts a perishable claim
into a dated measurement, which is the same thing every study card on the page
already does by naming its build and its box. "90 at 249ad34" stays true after
the tree grows to 200.

What this script checks, and what it deliberately does not
----------------------------------------------------------
FAILS when the stated count does not match the tree AT THE STATED SHA. That is
a real error: a transcription slip, or a number edited without recounting. It
is also permanent, so this check never goes stale and never needs tuning.

NOTES, without failing, when the live tip has moved past the stated one. That
is not an error. The page is still true; it is just describing an older commit,
and the reader was told which one. Failing here would paint the build red
because somebody else pushed to another repository, and a check that is
habitually red teaches people to click through it. The registry learned that
lesson explicitly when it narrowed an over-broad do-not-cite pattern rather
than letting it cry wolf, and the same reasoning applies here.

The note prints the refreshed numbers and the exact edit, so bringing the page
forward is a one-line change with the new SHA beside it.

Markers in the HTML:
    <div class="stats" data-counted-at="249ad34">
      <b data-check="minefield-entries">90</b>

Counting rules, which are the part worth getting right:
  entries      files under traps/<category>/, EXCLUDING the legacy flat
               redirect stubs at traps/NN-*.md, which are copies of earlier
               entries and not extra traps.
  categories   directories directly under traps/.
  contributors rows of the main credit table in HALL_OF_FAME.md, minus the
               owner's own row. The upstream-reports table below it credits
               original reporters of findings mined from public trackers,
               which is a different relationship and is counted separately
               in the page's prose rather than in this figure.

Usage:
    python3 check_counts.py --registry /path/to/model-serving-minefield
"""
import argparse
import os
import re
import subprocess
import sys


def git(repo, *args):
    return subprocess.run(("git", "-C", repo) + args,
                          capture_output=True, text=True)


def have_commit(repo, sha):
    r = git(repo, "cat-file", "-e", sha + "^{commit}")
    return r.returncode == 0


def ensure_commit(repo, sha):
    """CI checks out a shallow tree, so the stated SHA may be absent."""
    if have_commit(repo, sha):
        return True
    git(repo, "fetch", "--depth", "50", "origin", sha)
    if have_commit(repo, sha):
        return True
    git(repo, "fetch", "--unshallow")
    return have_commit(repo, sha)


def tree_paths(repo, sha):
    r = git(repo, "ls-tree", "-r", "--name-only", sha, "traps/")
    if r.returncode != 0:
        raise SystemExit("cannot read traps/ at %s: %s" % (sha, r.stderr.strip()))
    return [p for p in r.stdout.splitlines() if p.strip()]


def count_entries(repo, sha):
    # depth 2 under traps/ means traps/<category>/<file>.md, three components.
    return len([p for p in tree_paths(repo, sha)
                if p.endswith(".md") and len(p.split("/")) == 3])


def count_categories(repo, sha):
    return len({p.split("/")[1] for p in tree_paths(repo, sha)
                if len(p.split("/")) >= 3})


def count_contributors(repo, sha):
    r = git(repo, "show", "%s:HALL_OF_FAME.md" % sha)
    if r.returncode != 0:
        raise SystemExit("cannot read HALL_OF_FAME.md at %s" % sha)
    main = r.stdout.split("## Upstream reports")[0]
    rows = [l for l in main.splitlines() if l.startswith("|") and "**" in l]
    owner = [l for l in rows if "Blackwellboy" in l]
    return len(rows) - len(owner)


CHECKS = {
    "minefield-entries": count_entries,
    "minefield-categories": count_categories,
    "minefield-contributors": count_contributors,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True)
    ap.add_argument("--site", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "index.html"))
    args = ap.parse_args()

    with open(args.site, encoding="utf-8") as fh:
        html = fh.read()

    at = re.search(r'data-counted-at="([0-9a-f]{7,40})"', html)
    if not at:
        print("FAIL: no data-counted-at SHA on the stats block.")
        print("      A bare count is not checkable. State the tip it was counted at.")
        return 1
    sha = at.group(1)

    stated = dict(re.findall(r'data-check="([a-z-]+)"[^>]*>([0-9,]+)<', html))
    if not stated:
        print("FAIL: no data-check attributes found in", args.site)
        return 1

    if not ensure_commit(args.registry, sha):
        print("FAIL: commit %s is not reachable in the registry checkout." % sha)
        print("      Either the SHA on the page is wrong, or it was force-pushed away.")
        return 1

    print("Site states its registry figures were counted at %s\n" % sha)

    bad, unknown = [], sorted(set(stated) - set(CHECKS))
    for key, fn in CHECKS.items():
        if key not in stated:
            print("  note %-24s countable but not marked in the page" % key)
            continue
        said = int(stated[key].replace(",", ""))
        actual = fn(args.registry, sha)
        ok = said == actual
        if not ok:
            bad.append((key, said, actual))
        print("  %s %-24s page=%-6s tree@%s=%s"
              % ("ok " if ok else "FAIL", key, said, sha, actual))

    for key in unknown:
        print("  FAIL %-24s marked in the page but this script cannot count it" % key)

    if bad or unknown:
        print("\nThe page misstates a count for the commit it names.")
        for key, said, actual in bad:
            print("  %s: page says %s, tree at %s says %s" % (key, said, sha, actual))
        print("Fix index.html. Do not edit this script to agree.")
        return 1

    print("\nPASS: every stated count is correct for the commit the page names.")

    # Freshness note. Never fatal: the page is still true, just older.
    git(args.registry, "fetch", "-q", "origin", "main")
    tip = git(args.registry, "rev-parse", "--short", "FETCH_HEAD").stdout.strip()
    if tip and not tip.startswith(sha[:7]) and not sha.startswith(tip):
        if ensure_commit(args.registry, tip):
            print("\nNOTE: the registry has moved on. The page is not wrong, it is")
            print("      describing %s. Current tip is %s:" % (sha, tip))
            for key, fn in CHECKS.items():
                if key in stated:
                    print("        %-24s %s -> %s" % (key, stated[key], fn(args.registry, tip)))
            print("      To refresh, update the numbers and set")
            print("        data-counted-at=\"%s\"" % tip)
    return 0


if __name__ == "__main__":
    sys.exit(main())
