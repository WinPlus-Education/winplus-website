#!/usr/bin/env python3
"""
WinPlus website builder (English + Chinese).

Reads the editable content in /content (English) and /content/zh (Chinese),
fills in the HTML templates in /templates, and writes the finished website to /_site
(English at the root, Chinese under /zh/). Also generates sitemap.xml, robots.txt
and llms.txt for SEO and AI search.

  python build.py           # build the site into _site/
  python build.py --serve   # build, then preview at http://localhost:8000

Netlify runs `python build.py` automatically on every change (see netlify.toml).
Interface labels (buttons, form fields, "Learn more"...) are translated in
content/i18n/zh.yml.
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

LANGS = [
    {"code": "en", "html": "en", "locale": "en_US", "prefix": "", "dir": CONTENT},
    {"code": "zh", "html": "zh-CN", "locale": "zh_CN", "prefix": "zh/", "dir": CONTENT / "zh"},
]

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

DATE_FORMATS = {
    "en": {"long": "%B %-d, %Y", "mon": "%b", "day": "%-d", "year": "%Y", "weekday": "%A, %B %-d, %Y"},
    "zh": {"long": "%Y年%-m月%-d日", "mon": "%-m月", "day": "%-d", "year": "%Y", "weekday": "%Y年%-m月%-d日 {wd}"},
}
ZH_WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


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


def load_posts(base):
    posts = []
    for path in sorted((base / "posts").glob("*.md")):
        meta, body = read_front_matter(path)
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
        posts.append({**meta, "slug": slug, "date": as_date(meta.get("date")),
                      "url": f"insights/{slug}.html", "body": md(body)})
    posts.sort(key=lambda p: p.get("date") or dt.datetime.min, reverse=True)
    return posts


def load_collection(base, name, out_dir):
    items = []
    for path in sorted((base / name).glob("*.yml")):
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


def load_language(lang):
    base = lang["dir"]
    data = {"site": load_yaml(base / "site.yml"), "posts": load_posts(base)}
    for name, (_, out) in COLLECTIONS.items():
        data[name] = load_collection(base, name, out)
    data["legal"] = []
    for path in sorted((base / "legal").glob("*.md")):
        meta, body = read_front_matter(path)
        meta["body"] = md(body)
        data["legal"].append((path.stem, meta))
    data["results"] = load_yaml(base / "pages" / "results.yml")
    return data


def build():
    langs = [l for l in LANGS if (l["dir"] / "site.yml").exists()]
    site_url = load_yaml(CONTENT / "site.yml").get("site_url", "").rstrip("/")
    zh_strings = load_yaml(CONTENT / "i18n" / "zh.yml")
    missing = set()
    now = dt.datetime.now()
    version = now.strftime("%Y%m%d%H%M%S")

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)

    # Pass 1: load content and list every output page per language
    data, outputs = {}, {}
    for lang in langs:
        d = load_language(lang)
        data[lang["code"]] = d
        names = [out for tpl, (_, out, _) in PAGES.items()]
        names += [i["url"] for name in COLLECTIONS for i in d[name]]
        names += [p["url"] for p in d["posts"]]
        names += [f"{stem}.html" for stem, _ in d["legal"]]
        outputs[lang["code"]] = set(names)

    sitemap = []  # (lang, out_name, priority)

    # Pass 2: render
    for lang in langs:
        code, d = lang["code"], data[lang["code"]]
        env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]),
                          trim_blocks=True, lstrip_blocks=True)

        def translate(text, code=code):
            if code == "en" or not text:
                return text
            if text in zh_strings:
                return zh_strings[text]
            missing.add(text)
            return text

        def date_fmt(d_, kind="long", code=code):
            if not d_:
                return ""
            fmt = DATE_FORMATS[code].get(kind, kind)
            return d_.strftime(fmt.replace("{wd}", ZH_WEEKDAYS[d_.weekday()]))

        env.filters.update(num=num, md=md, date_fmt=date_fmt,
                           slugify=lambda s: re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "x",
                           jsonld=lambda obj: json.dumps(obj, ensure_ascii=False, indent=1).replace("</", "<\\/"))
        env.globals["_"] = translate

        events = d["events"]
        upcoming = [e for e in events if e.get("date") and e["date"] >= now - dt.timedelta(days=1)]
        common = {
            "lang": lang, "site": d["site"], "site_url": site_url, "posts": d["posts"],
            "programs": d["programs"], "services": d["admissions"], "enrichments": d["enrichment"],
            "events": events, "upcoming": upcoming, "past_events": [e for e in events if e not in upcoming][::-1],
            "results_data": d["results"], "today": TODAY, "year": TODAY.year, "version": version,
        }

        def render(template, out_name, page=None, priority=None, **extra):
            full = lang["prefix"] + out_name
            asset_root = "../" * full.count("/")
            lang_root = "../" * out_name.count("/")

            def link(url):
                if not url or re.match(r"^(https?:|mailto:|tel:|#|/)", url):
                    return url
                return lang_root + url

            def url_for(code_, name):
                pre = next(l["prefix"] for l in langs if l["code"] == code_)
                return f"{site_url}/{pre}" + ("" if name == "index.html" else name)

            alternates = {}
            for l in langs:
                if out_name in outputs[l["code"]]:
                    alternates[l["html"]] = url_for(l["code"], out_name)
            if len(alternates) > 1:
                alternates["x-default"] = url_for("en", out_name)
            switch = {}
            for l in langs:
                target = out_name if out_name in outputs[l["code"]] else "index.html"
                switch[l["code"]] = asset_root + l["prefix"] + target
            env.globals["u"] = link
            env.globals["img"] = lambda src, w=1200: img_url(src, w, asset_root)
            html = env.get_template(template).render(
                **common, page=page or {}, root=asset_root, current=out_name,
                canonical=url_for(code, out_name), alternates=alternates if len(alternates) > 1 else {},
                switch=switch, **extra)
            target = OUT / full
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8")
            if priority:
                sitemap.append((code, out_name, priority))

        for tpl, (content_name, out_name, prio) in PAGES.items():
            page = load_yaml(lang["dir"] / "pages" / f"{content_name}.yml") if content_name else {}
            render(tpl, out_name, page, prio)
        for name, (tpl, _) in COLLECTIONS.items():
            for item in d[name]:
                render(tpl, item["url"], item, "0.5" if name == "events" else "0.7", item=item, siblings=d[name])
        for post in d["posts"]:
            render("post.html", post["url"], {}, "0.6", post=post)
        for stem, meta in d["legal"]:
            render("legal.html", f"{stem}.html", meta, "0.2")

        # llms.txt — a plain-language summary for AI assistants (English site only)
        if code == "en":
            env.globals["u"] = lambda url: url
            (OUT / "llms.txt").write_text(env.get_template("llms.txt").render(**common), encoding="utf-8")

    # sitemap.xml with language alternates
    by_name = {}
    for code, name, prio in sitemap:
        by_name.setdefault(name, {})[code] = prio
    rows = []
    for code, name, prio in sitemap:
        pre = next(l["prefix"] for l in langs if l["code"] == code)
        loc = f"{site_url}/{pre}" + ("" if name == "index.html" else name)
        alts = ""
        if len(by_name[name]) > 1:
            for l in langs:
                if l["code"] in by_name[name]:
                    href = f"{site_url}/{l['prefix']}" + ("" if name == "index.html" else name)
                    alts += f'<xhtml:link rel="alternate" hreflang="{l["html"]}" href="{href}"/>'
        rows.append(f"  <url><loc>{loc}</loc><lastmod>{TODAY.isoformat()}</lastmod><priority>{prio}</priority>{alts}</url>")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")

    # robots.txt — welcome search engines and AI assistants (helps GEO), keep the editor private
    bots = ["Googlebot", "Bingbot", "Baiduspider", "Sogou web spider", "360Spider", "Bytespider", "GPTBot",
            "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Google-Extended",
            "Applebot-Extended"]
    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /thanks.html\nDisallow: /zh/thanks.html\n\n"
        + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)
        + f"Sitemap: {site_url}/sitemap.xml\n", encoding="utf-8")

    counts = ", ".join(f"{l['code'].upper()}: {sum(1 for c, *_ in sitemap if c == l['code'])}" for l in langs)
    print(f"Built pages ({counts}) into {OUT.relative_to(ROOT)}/ (+ sitemap.xml, robots.txt, llms.txt)")
    if missing:
        print(f"Note: {len(missing)} interface label(s) have no Chinese translation in content/i18n/zh.yml:")
        for m in sorted(missing):
            print("  -", m)


def serve(port=8000):
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Preview at http://localhost:{port}  (Ctrl+C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve()
