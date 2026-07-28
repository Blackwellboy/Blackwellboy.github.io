#!/usr/bin/env python3
"""build.py - render index.html from index.template.html plus the live registry tree.

Why this exists
---------------
Every number on this page that describes the registry has been wrong at some
point, because it was typed by hand into HTML and the registry moved. The
count went 42, 81, 90, 97 inside about a day. Three separate hand corrections
were made and each was stale within hours.

The previous mechanism verified a stated count against a stated commit. That
stopped the page LYING, because "90 at 249ad34" stays true forever, but it did
not stop the page being OLD: an old page simply passed. The check was correct
and insufficient.

So the numbers are no longer written into the page. They are read out of a
checked-out registry at build time and substituted into a template. There is
one source of truth, it is the tree, and nobody has to remember anything.

Why a template render and not the alternatives
----------------------------------------------
- NOT a network fetch of a private repo at page load or build time. That is
  what broke an earlier attempt, and it also cannot work: the published page
  is static and the registry is a git tree, not an API.
- NOT client-side JavaScript against the GitHub API. It would break the
  no-JS property, rate-limit for real visitors, and show a spinner where a
  number should be.
- NOT a bot that rewrites numbers inside index.html with a regex. Editing
  generated values inside a hand-maintained file is how the two drift apart.

The template is the artifact a human edits. index.html is generated and should
never be edited directly; the workflow regenerates it and commits only when the
rendered bytes actually change, so history stays quiet when nothing moved.

What is generated versus what is not
------------------------------------
Generated: anything that describes the CURRENT STATE of a repository. Entry
counts, category counts, how many playbooks exist, how many stack pages, the
Core tier size, the doctor's check count, contributor counts, the tip.

Not generated, and deliberately hand-written: measurements from a fixed run.
"26.2 tok/s at K=7" is not a fact about the tree, it is a result from one
sweep at one revision, and it does not change when the registry grows. Those
carry their conditions instead, which is the same discipline applied by hand.

The rule: if a number would be different tomorrow without anyone intending it,
generate it. If it would only change because someone re-ran an experiment,
write it down with its conditions.

Fails loudly. A token that cannot be derived aborts the build rather than
rendering an empty span or a stale default, because a page that silently drops
a number is worse than one that does not build.

Usage:
    python3 build.py --registry /path/to/model-serving-minefield
    python3 build.py --registry ... --check    # verify index.html is current
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def git(repo, *args):
    r = subprocess.run(("git", "-C", repo) + args, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# --- extractors. each returns a string, or raises with a usable message. ----

def entries(reg):
    n = 0
    root = os.path.join(reg, "traps")
    for cat in os.listdir(root):
        d = os.path.join(root, cat)
        if os.path.isdir(d):
            n += len([f for f in os.listdir(d) if f.endswith(".md")])
    if n < 1:
        raise ValueError("counted %d trap entries" % n)
    return str(n)


def categories(reg):
    root = os.path.join(reg, "traps")
    return str(len([d for d in os.listdir(root)
                    if os.path.isdir(os.path.join(root, d))]))


def category_list(reg):
    root = os.path.join(reg, "traps")
    names = sorted(d for d in os.listdir(root)
                   if os.path.isdir(os.path.join(root, d)))
    return ", ".join(names)


def _md_count(reg, sub):
    d = os.path.join(reg, sub)
    if not os.path.isdir(d):
        raise ValueError("%s/ does not exist in the registry" % sub)
    return [f for f in sorted(os.listdir(d))
            if f.endswith(".md") and f.lower() != "readme.md"]


def playbooks(reg):
    return str(len(_md_count(reg, "playbooks")))


def stacks(reg):
    return str(len(_md_count(reg, "stacks")))


_STACK_PRETTY = {"llama-cpp": "llama.cpp", "mlx": "MLX", "ollama": "Ollama",
                 "vllm": "vLLM"}
MEASURED_HERE_RE = re.compile(r"^\*\*Measured here:\*\* (yes|no)\b", re.M)


def _prose_list(names):
    if len(names) > 1:
        return ", ".join(names[:-1]) + " and " + names[-1]
    return names[0]


def stack_names(reg):
    names = [_STACK_PRETTY.get(f[:-3], f[:-3]) for f in _md_count(reg, "stacks")]
    return _prose_list(names)


def _firsthand_stacks(reg):
    """Stack pages whose own marker says we measured on that stack.

    Read from an explicit marker, never inferred from prose. The first render
    of this page put the stack-PAGE count into a label reading "measured
    first-hand" and published 11, where the true number is 5: six of the pages
    are about stacks nobody here has touched. They said so in their own words,
    in two different phrasings, so no regex could separate the sets and the
    fix at the time was to weaken the label to "covered". The registry now
    declares it per page, and reference_integrity fails a stack page that does
    not carry the marker, so this raises rather than guessing.
    """
    out = []
    for fn in _md_count(reg, "stacks"):
        body = read(os.path.join(reg, "stacks", fn))
        m = MEASURED_HERE_RE.search(body)
        if m is None:
            raise ValueError(
                "stacks/%s has no '**Measured here:**' marker. Refusing to "
                "render a first-hand count that would be a guess." % fn)
        if m.group(1) == "yes":
            out.append(fn)
    return out


def stacks_firsthand(reg):
    return str(len(_firsthand_stacks(reg)))


def stack_firsthand_names(reg):
    return _prose_list([_STACK_PRETTY.get(f[:-3], f[:-3])
                        for f in _firsthand_stacks(reg)])


def core_count(reg):
    """The Core tier size, taken from CORE.md's own table rather than its title."""
    t = read(os.path.join(reg, "CORE.md"))
    rows = re.findall(r"^\|\s*\[", t, re.M)
    if not rows:
        raise ValueError("CORE.md has no table rows to count")
    return str(len(rows))


def doctor_checks(reg):
    """Counted from TRAP_PATHS in the tool itself, not from its README prose.

    This used to parse "Its N checks" out of doctor/README.md. That sentence
    said 18 while the same file said 19 further down and TRAP_PATHS held 19,
    so this page published 18: a stale sentence in one repo became a wrong
    number on a public site in another. The registry now also fails a mismatch
    between that sentence and the code, but the site no longer depends on the
    sentence at all.
    """
    t = read(os.path.join(reg, "doctor", "minefield_doctor.py"))
    m = re.search(r"TRAP_PATHS\s*=\s*\{(.*?)\n\}", t, re.S)
    if not m:
        raise ValueError("could not find TRAP_PATHS in minefield_doctor.py")
    return str(len(re.findall(r'"\d{2,}"\s*:', m.group(1))))


def _hof_tables(reg):
    t = read(os.path.join(reg, "HALL_OF_FAME.md"))
    main = t.split("## Upstream reports")[0]
    up = t.split("## Upstream reports")[1] if "## Upstream reports" in t else ""
    rows = lambda s: [l for l in s.splitlines() if l.startswith("|") and "**" in l]
    return rows(main), rows(up)


def contributors(reg):
    main, _ = _hof_tables(reg)
    owner = [l for l in main if "Blackwellboy" in l]
    return str(len(main) - len(owner))


def upstream_reporters(reg):
    _, up = _hof_tables(reg)
    names = set()
    for line in up:
        cell = line.strip("|").split("|")[0]
        cell = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)
        names |= set(re.findall(r"@?\b([A-Za-z0-9][A-Za-z0-9_-]{2,})\b", cell))
    if not names:
        raise ValueError("no upstream reporter names parsed")
    return str(len(names))


def open_questions(reg):
    """mining/ entries that record a question with its disposition."""
    d = os.path.join(reg, "mining")
    return str(len([f for f in os.listdir(d)
                    if f.endswith(".md") and f.lower() != "readme.md"]))


def tip(reg):
    s = git(reg, "rev-parse", "--short", "HEAD")
    if not s:
        raise ValueError("registry is not a git checkout")
    return s


def tip_full(reg):
    return git(reg, "rev-parse", "HEAD")


def tip_date(reg):
    return (git(reg, "log", "-1", "--format=%cs") or "")


TOKENS = {
    "REG_ENTRIES": entries,
    "REG_CATEGORIES": categories,
    "REG_CATEGORY_LIST": category_list,
    "REG_PLAYBOOKS": playbooks,
    "REG_STACKS": stacks,
    "REG_STACK_NAMES": stack_names,
    "REG_STACKS_FIRSTHAND": stacks_firsthand,
    "REG_STACK_FIRSTHAND_NAMES": stack_firsthand_names,
    "REG_CORE": core_count,
    "DOCTOR_CHECKS": doctor_checks,
    "CONTRIBUTORS": contributors,
    "UPSTREAM_REPORTERS": upstream_reporters,
    "OPEN_QUESTIONS": open_questions,
    "REG_TIP": tip,
    "REG_TIP_FULL": tip_full,
    "REG_TIP_DATE": tip_date,
}


def render(reg, template):
    values, problems = {}, []
    for name, fn in TOKENS.items():
        try:
            v = fn(reg)
            if v is None or v == "":
                raise ValueError("empty value")
            values[name] = v
        except Exception as exc:
            problems.append("  %-20s %s" % (name, exc))
    if problems:
        raise SystemExit("cannot derive these values from the registry:\n"
                         + "\n".join(problems))

    used, unknown = set(), set()

    def sub(m):
        key = m.group(1)
        if key not in values:
            unknown.add(key)
            return m.group(0)
        used.add(key)
        return values[key]

    out = re.sub(r"\{\{([A-Z_]+)\}\}", sub, template)
    if unknown:
        raise SystemExit("template uses tokens this script cannot supply: %s"
                         % ", ".join(sorted(unknown)))
    return out, values, sorted(set(values) - used)


# Superlatives about a repository are counts wearing a disguise. "its largest
# category" was true when the registry was smaller and silently became false
# when runtime overtook evaluation; nothing would have caught it, because it
# contains no digits. This warns rather than fails: some of these words are
# legitimate in prose about a measurement ("the highest median in that run").
SUPERLATIVE = re.compile(
    r"\b(its largest|the largest|the biggest|the most[- ]covered|the widest|"
    r"the deepest|the longest|our largest|the smallest|the fewest)\b", re.I)


def lint(template):
    warnings = []
    for i, line in enumerate(template.splitlines(), 1):
        if "<!--" in line:
            continue
        for m in SUPERLATIVE.finditer(line):
            warnings.append(
                "  line %d: %r is a claim about repo state that no build step "
                "can keep true" % (i, m.group(0)))
    return warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True)
    ap.add_argument("--template", default=os.path.join(HERE, "index.template.html"))
    ap.add_argument("--out", default=os.path.join(HERE, "index.html"))
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the rendered output differs from --out")
    args = ap.parse_args()

    template = read(args.template)
    warnings = lint(template)
    if warnings:
        print("lint, not fatal:")
        print("\n".join(warnings) + "\n")

    out, values, unused = render(args.registry, template)

    print("derived from %s at %s:" % (os.path.basename(os.path.abspath(args.registry)),
                                      values["REG_TIP"]))
    for k in sorted(values):
        if k.startswith("REG_TIP"):
            continue
        print("  %-20s %s" % (k, values[k]))
    if unused:
        print("  (derived but unused in the template: %s)" % ", ".join(unused))

    existing = read(args.out) if os.path.exists(args.out) else None

    if args.check:
        if existing == out:
            print("\nPASS: index.html is up to date with the registry.")
            return 0
        print("\nSTALE: index.html does not match a fresh render.")
        print("Run: python3 build.py --registry <path>")
        return 1

    if existing == out:
        print("\nunchanged: index.html already matches the registry.")
        return 0

    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    print("\nwrote %s (%d bytes)" % (args.out, len(out.encode())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
