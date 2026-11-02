#!/usr/bin/env python3
"""Read-only integrity checks for the static site (stdlib only).

Checks: CNAME preserved, local asset references exist with exact case
(Pages runs on case-sensitive Linux), no private secret URLs, image alt text,
sitemap namespace. Exit code 1 on any error.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_CNAME = "puranenjenny.dev"
errors, warnings = [], []


class Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.imgs = [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("src", "href", "poster"):
            if a.get(key):
                self.refs.append((tag, a[key]))
        if tag == "img":
            self.imgs.append(a)


def exact_case_exists(path: Path) -> bool:
    cur = ROOT
    for part in path.relative_to(ROOT).parts:
        if part not in [p.name for p in cur.iterdir()]:
            return False
        cur = cur / part
    return True


def check_cname():
    f = ROOT / "CNAME"
    if not f.exists() or f.read_text().strip() != EXPECTED_CNAME:
        errors.append(f"CNAME must contain {EXPECTED_CNAME}")


def check_html(html: Path):
    rel = html.relative_to(ROOT)
    text = html.read_text(encoding="utf-8", errors="replace")
    if re.search(r"[?&]secret=", text):
        warnings.append(f"{rel}: private ?secret= URL (pending owner decision)")
    p = Refs()
    p.feed(text)
    for tag, ref in p.refs:
        u = urlparse(ref)
        if u.scheme or not u.path or ref.startswith("//"):
            continue
        base = ROOT if u.path.startswith("/") else html.parent
        target = (base / unquote(u.path).lstrip("/")).resolve()
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            errors.append(f"{rel}: missing <{tag}> {ref}")
        elif not exact_case_exists(target):
            errors.append(f"{rel}: case mismatch {ref}")
    for a in p.imgs:
        alt = (a.get("alt") or "").strip()
        if "alt" not in a:
            warnings.append(f"{rel}: img without alt {a.get('src')}")
        elif re.fullmatch(r"[A-Za-z]{1,3}\d{0,2}", alt):
            warnings.append(f"{rel}: weak alt '{alt}'")


def check_sitemap():
    f = ROOT / "sitemap.xml"
    if f.exists() and "https://www.sitemaps.org/schemas" in f.read_text():
        warnings.append("sitemap.xml: namespace should be http://www.sitemaps.org/...")


def main():
    check_cname()
    check_sitemap()
    for html in sorted(ROOT.glob("*.html")):
        check_html(html)
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
