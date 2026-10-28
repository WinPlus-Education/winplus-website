#!/usr/bin/env python3
"""
WinPlus website builder.

Reads the editable content in /content (YAML + Markdown), fills in the
HTML templates in /templates, and writes the finished website to /_site.

  python build.py           # build the site into _site/
  python build.py --serve   # build, then preview at http://localhost:8000

Netlify runs `python build.py` automatically on every change (see netlify.toml).
"""
import datetime as dt
import http.server
import re
import shutil
import socketserver
import sys
from functools import partial
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT / "_site"

# page template -> (content file, output file)
PAGES = {
    "home.html": ("home", "index.html"),
    "admissions.html": ("admissions", "admissions.html"),
    "programs.html": ("programs", "programs.html"),
    "results.html": ("results", "results.html"),
    "insights.html": ("insights", "insights.html"),
    "schools.html": ("schools", "schools.html"),
    "about.html": ("about", "about.html"),
    "how-it-works.html": ("how-it-works", "how-it-works.html"),
    "contact.html": ("contact", "contact.html"),
    "thanks.html": ("contact", "thanks.html"),
}


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_posts():
    posts = []
    for path in sorted((CONTENT / "posts").glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
        meta, body = (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, raw)
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
        date = meta.get("date")
        if isinstance(date, str):
            date = dt.date.fromisoformat(date[:10])
        if isinstance(date, dt.datetime):
            date = date.date()
        posts.append({
            **meta,
            "slug": slug,
            "date": date,
            "url": f"insights/{slug}.html",
            "body": markdown.markdown(body, extensions=["extra"]),
        })
    posts.sort(key=lambda p: p.get("date") or dt.date.min, reverse=True)
    return posts


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def build():
    site = load_yaml(CONTENT / "site.yml")
    posts = load_posts()

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["num"] = num
    env.filters["date_fmt"] = lambda d: d.strftime("%B %-d, %Y") if d else ""
    env.filters["slugify"] = lambda s: re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)

    common = {"site": site, "posts": posts, "year": dt.date.today().year}

    def link(url, root):
        """Make site links relative so the site works from any folder."""
        if not url or re.match(r"^(https?:|mailto:|tel:|#|/)", url):
            return url
        return root + url

    for tpl, (content_name, out_name) in PAGES.items():
        page = load_yaml(CONTENT / "pages" / f"{content_name}.yml")
        root = ""
        env.globals["u"] = partial(link, root=root)
        html = env.get_template(tpl).render(**common, page=page, root=root, current=out_name)
        (OUT / out_name).write_text(html, encoding="utf-8")

    (OUT / "insights").mkdir(exist_ok=True)
    for post in posts:
        root = "../"
        env.globals["u"] = partial(link, root=root)
        html = env.get_template("post.html").render(**common, page={}, post=post, root=root, current="insights.html")
        (OUT / post["url"]).write_text(html, encoding="utf-8")

    print(f"Built {len(PAGES)} pages and {len(posts)} articles into {OUT.relative_to(ROOT)}/")


def serve(port=8000):
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Preview at http://localhost:{port}  (Ctrl+C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve()
