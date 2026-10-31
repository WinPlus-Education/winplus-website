#!/usr/bin/env python3
"""
WinPlus website builder.

Reads the editable content in /content (YAML + Markdown), fills in the
HTML templates in /templates, and writes the finished website to /_site.
Also generates sitemap.xml, robots.txt and llms.txt for SEO / AI search.

  python build.py           # build the site into _site/
  python build.py --serve   # build, then preview at http://localhost:8000

Netlify runs `python build.py` automatically on every change (see netlify.toml).
"""
import datetime as dt
import http.server
import json
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
TODAY = dt.date.today()

# template -> (content file in content/pages, output file, sitemap priority)
PAGES = {
    "home.html": ("home", "index.html", "1.0"),
    "admissions.html": ("admissions", "admissions.html", "0.9"),
    "research.html": ("research", "research.html", "0.9"),
    "enrichment.html": ("enrichment", "enrichment.html", "0.9"),
    "events.html": ("events", "events.html", "0.7"),
    "results.html": ("results", "results.html", "0.9"),
    "insights.html": ("insights", "insights.html", "0.8"),
    "team.html": ("team", "team.html", "0.8"),
    "schools.html": ("schools", "schools.html", "0.6"),
    "how-it-works.html": ("how-it-works", "how-it-works.html", "0.7"),
    "contact.html": ("contact", "contact.html", "0.8"),
    "sitemap.html": (None, "sitemap.html", "0.3"),
    "thanks.html": ("contact", "thanks.html", None),
    "404.html": (None, "404.html", None),
}

# folder of YAML files -> (detail template, output folder)
COLLECTIONS = {
    "admissions": ("service.html", "admissions"),
    "programs": ("program.html", "research"),
    "enrichment": ("enrichment-detail.html", "enrichment"),
    "events": ("event.html", "events"),
}


def load_yaml(path):
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def as_date(value):
    if isinstance(value, dt.datetime):
        return value
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time())
    if isinstance(value, str) and value.strip():
        try:
            return dt.datetime.fromisoformat(value.strip()[:19])
        except ValueError:
            return None
    return None


def read_front_matter(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
    return (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, raw)


def md(text):
    return markdown.markdown(text or "", extensions=["extra"])


def load_posts():
    posts = []
    for path in sorted((CONTENT / "posts").glob("*.md")):
        meta, body = read_front_matter(path)
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
        date = as_date(meta.get("date"))
        posts.append({**meta, "slug": slug, "date": date, "url": f"insights/{slug}.html", "body": md(body)})
    posts.sort(key=lambda p: p.get("date") or dt.datetime.min, reverse=True)
    return posts


def load_collection(name, out_dir):
    items = []
    for path in sorted((CONTENT / name).glob("*.yml")):
        data = load_yaml(path)
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
        data.update(slug=slug, url=f"{out_dir}/{slug}.html")
        if "date" in data:
            data["date"] = as_date(data["date"])
        items.append(data)
    if name == "events":
        items.sort(key=lambda e: e.get("date") or dt.datetime.max)
    else:
        items.sort(key=lambda e: (e.get("order", 99), e.get("title", "")))
    return items


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def img_url(src, width=1200, root=""):
    """Unsplash links get size/format parameters; uploaded files get the right relative path."""
    if not src:
        return ""
    if src.startswith("http"):
        if "images.unsplash.com" in src and "?" not in src:
            return f"{src}?auto=format&fit=crop&w={width}&q=70"
        return src
    return root + src.lstrip("/")


def build():
    site = load_yaml(CONTENT / "site.yml")
    site_url = site.get("site_url", "").rstrip("/")
    posts = load_posts()
    collections = {name: load_collection(name, out) for name, (_, out) in COLLECTIONS.items()}
    now = dt.datetime.now()
    events = collections["events"]
    upcoming = [e for e in events if e.get("date") and e["date"] >= now - dt.timedelta(days=1)]
    past = [e for e in events if e not in upcoming][::-1]

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["num"] = num
    env.filters["md"] = md
    env.filters["date_fmt"] = lambda d, f="%B %-d, %Y": d.strftime(f) if d else ""
    env.filters["slugify"] = lambda s: re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
    env.filters["jsonld"] = lambda obj: json.dumps(obj, ensure_ascii=False, indent=1).replace("</", "<\\/")

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)

    common = {
        "site": site,
        "site_url": site_url,
        "posts": posts,
        "programs": collections["programs"],
        "services": collections["admissions"],
        "enrichments": collections["enrichment"],
        "events": events,
        "upcoming": upcoming,
        "past_events": past,
        "results_data": load_yaml(CONTENT / "pages" / "results.yml"),
        "today": TODAY,
        "year": TODAY.year,
        # changes on every build so browsers always load the newest CSS/JS
        "version": now.strftime("%Y%m%d%H%M%S"),
    }
    sitemap = []

    def render(template, out_name, page=None, priority=None, **extra):
        depth = out_name.count("/")
        root = "../" * depth

        def link(url):
            if not url or re.match(r"^(https?:|mailto:|tel:|#)", url):
                return url
            return root + url.lstrip("/")

        env.globals["u"] = link
        env.globals["img"] = lambda src, w=1200: img_url(src, w, root)
        canonical = f"{site_url}/" + ("" if out_name == "index.html" else out_name)
        html = env.get_template(template).render(
            **common, page=page or {}, root=root, current=out_name, canonical=canonical, **extra
        )
        target = OUT / out_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        if priority:
            sitemap.append((canonical, priority))

    for tpl, (content_name, out_name, prio) in PAGES.items():
        page = load_yaml(CONTENT / "pages" / f"{content_name}.yml") if content_name else {}
        render(tpl, out_name, page, prio)

    for name, (tpl, out_dir) in COLLECTIONS.items():
        items = collections[name]
        for item in items:
            render(tpl, item["url"], item, "0.7" if name != "events" else "0.5", item=item, siblings=items)

    for post in posts:
        render("post.html", post["url"], {}, "0.6", post=post)

    for path in sorted((CONTENT / "legal").glob("*.md")):
        meta, body = read_front_matter(path)
        meta["body"] = md(body)
        render("legal.html", f"{path.stem}.html", meta, "0.2")

    # sitemap.xml
    urls = "\n".join(
        f"  <url><loc>{loc}</loc><lastmod>{TODAY.isoformat()}</lastmod><priority>{p}</priority></url>"
        for loc, p in sitemap
    )
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8",
    )

    # robots.txt — welcome search engines and AI assistants (helps GEO), keep the editor private
    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /thanks.html\n\n"
        + "".join(f"User-agent: {bot}\nAllow: /\n\n" for bot in
                  ["Googlebot", "Bingbot", "Baiduspider", "GPTBot", "OAI-SearchBot", "ChatGPT-User",
                   "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Applebot-Extended"])
        + f"Sitemap: {site_url}/sitemap.xml\n",
        encoding="utf-8",
    )

    # llms.txt — a plain-language summary of the site for AI assistants (GEO)
    env.globals["u"] = lambda url: url
    llms = env.get_template("llms.txt").render(**common)
    (OUT / "llms.txt").write_text(llms, encoding="utf-8")

    print(f"Built {len(sitemap)} pages into {OUT.relative_to(ROOT)}/ (+ sitemap.xml, robots.txt, llms.txt)")


def serve(port=8000):
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Preview at http://localhost:{port}  (Ctrl+C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve()
