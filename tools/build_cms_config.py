#!/usr/bin/env python3
"""
Generates static/admin/config.yml (the /admin editor) for English and Chinese.

The editor fields are inferred from the content files themselves, so every field in
content/ is always editable (Decap deletes unknown fields when saving). Run this after
adding or renaming fields:   python tools/build_cms_config.py
Then check:                   python tools/check_cms_fields.py
"""
import glob
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# Friendly labels for common field names (anything else is turned into "Title case")
LABELS = {
    "seo_title": "SEO: browser tab & Google title", "meta_description": "SEO: Google description (about 150 characters)",
    "eyebrow": "Small label above the title", "intro": "Intro text", "image": "Photo (upload, or paste an image link)",
    "image_alt": "Photo description (accessibility & SEO)", "cta": "Button text", "cta_link": "Button link",
    "faq": "FAQ (questions & answers)", "q": "Question", "a": "Answer", "link": "Link (e.g. results.html)",
    "status": "Status (open / closed / past)", "type": "Type", "industry": "Field (id)", "mentor_id": "Mentor (person id from Our Team)",
    "mentor_note": "Mentor line shown on cards", "order": "Order in lists", "slides": "Hero photos (rotating)",
    "results_notice": "Results disclaimer (legal)", "consent": "Form notices & consents (legal)", "cookie": "Cookie banner (legal)",
    "partners": "Logo strip (mentor network)", "logo": "Logo file (PNG/SVG, transparent background)", "photo": "Photo",
    "bio": "Full bio", "body": "Text", "date": "Date & start time", "end_date": "End date (optional)",
    "featured": "Featured people (ids from Our Team)", "gallery": "Photo gallery", "testimonials": "Testimonials",
    "dek": "Standfirst (one or two sentences under the title)", "image_caption": "Cover photo caption", "key_facts": "Key facts strip (2–4 numbers)",
    "faq_title": "Q&A heading", "logo_text": "Text beside the crest logo (empty = brand name)", "company_cn": "China entity name", "tax_id_cn": "Unified social credit code",
    "postal_code": "ZIP / postal code",
}
IMAGE_KEYS = {"image", "photo", "logo", "wechat_qr", "default_image", "mission_image", "case_image", "secondary_file"}
TEXT_KEYS = {"intro", "text", "summary", "bio", "a", "quote", "overview", "details", "meta_description", "footer_blurb",
             "footer_disclaimer", "statement_text", "summary_text", "story_text", "mission_text", "case_text", "start",
             "strategy", "change", "outcome", "who", "selection_text", "card_text", "subtitle", "dek"}
MARKDOWN_KEYS = {"overview", "details", "bio", "body", "a", "summary_text", "story_text", "mission_text"}
DATE_KEYS = {"date", "end_date", "updated"}
NUMBER_KEYS = {"order", "rates_count"}
BOOL_KEYS = {"lead", "highlight", "featured_post"}


def label(key):
    return LABELS.get(key, key.replace("_", " ").capitalize())


def merge(a, b):
    """Merge two inferred field specs (used to combine several files of a folder collection)."""
    if a is None:
        return b
    if b is None:
        return a
    if a[0] == "object" and b[0] == "object":
        keys = list(a[1].keys()) + [k for k in b[1] if k not in a[1]]
        return ("object", {k: merge(a[1].get(k), b[1].get(k)) for k in keys})
    if a[0] == "list" and b[0] == "list":
        return ("list", merge(a[1], b[1]))
    rank = ["string", "text", "markdown"]
    if a[0] in rank and b[0] in rank:
        return (rank[max(rank.index(a[0]), rank.index(b[0]))], None)
    return a


def infer(key, value):
    if isinstance(value, dict):
        spec = None
        for k, v in value.items():
            spec = merge(spec, ("object", {k: infer(k, v)}))
        return spec or ("object", {})
    if isinstance(value, list):
        item = None
        for v in value:
            item = merge(item, infer(key, v))
        return ("list", item or ("string", None))
    if isinstance(value, bool) or key in BOOL_KEYS:
        return ("boolean", None)
    if key in NUMBER_KEYS and isinstance(value, int):
        return ("number", None)
    if key in DATE_KEYS:
        return ("datetime", None)
    if key in IMAGE_KEYS:
        return ("image", None)
    if key in MARKDOWN_KEYS:
        return ("markdown", None)
    if key in TEXT_KEYS or (isinstance(value, str) and (len(value) > 110 or "\n" in value)):
        return ("text", None)
    return ("string", None)


def to_fields(spec):
    fields = []
    for k, sub in spec[1].items():
        fields.append(to_field(k, sub))
    return fields


def to_field(k, sub):
    kind = sub[0]
    f = {"name": k, "label": label(k), "required": False}
    if kind == "object":
        f.update(widget="object", collapsed=True, fields=to_fields(sub))
    elif kind == "list":
        item = sub[1]
        if item[0] == "object":
            f.update(widget="list", collapsed=True, fields=to_fields(item))
            first = next(iter(item[1]), None)
            for cand in ("title", "name", "q", "label", "city", "phase", "number", "image"):
                if cand in item[1]:
                    first = cand
                    break
            if first:
                f["summary"] = "{{fields.%s}}" % first
        else:
            f.update(widget="list", field={"name": "item", "label": "Item", "widget": "image" if item[0] == "image" else "string"})
    elif kind == "datetime":
        f.update(widget="datetime", format="YYYY-MM-DDTHH:mm:ss" if k == "date" else "YYYY-MM-DD")
    elif kind == "image":
        f.update(widget="file" if k == "secondary_file" else "image", choose_url=True)
    else:
        f["widget"] = kind
    return f


def load(path):
    raw = Path(path).read_text(encoding="utf-8")
    if path.endswith(".md"):
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
        data = yaml.safe_load(m.group(1)) or {}
        data["body"] = m.group(2)
        return data
    return yaml.safe_load(raw) or {}


def spec_for(paths):
    spec = None
    for p in paths:
        spec = merge(spec, infer("", load(p)))
    return spec or ("object", {})


PAGE_LABELS = {"home": "Home", "admissions": "Admissions Counseling (overview)", "research": "Research & Internships (overview)",
               "experiences": "Global Experiences (overview)", "events": "Events (page text)", "results": "Our Results",
               "about": "About Us", "team": "Our Team (all people)", "schools": "For Schools", "faq": "FAQ", "contact": "Book Consultation (form)",
               "insights": "Insights (page text)", "credits": "Photo credits"}
FOLDERS = [("admissions", "Admissions Programs", "Admissions Program", "yml"), ("programs", "Research & Internship Programs", "Program", "yml"),
           ("experiences", "Global Experiences", "Experience", "yml"), ("events", "Events", "Event", "yml"), ("posts", "Insights Articles", "Article", "md")]


def collections(base, zh=False):
    tag = "中文 · " if zh else ""
    pre = "zh-" if zh else ""
    c = ROOT / base
    cols = [{"name": f"{pre}settings", "label": f"{tag}Site Settings", "files": [
        {"name": "site", "label": "Header, Footer, Contact, Social & Legal text", "file": f"{base}/site.yml", "fields": to_fields(spec_for([str(c / "site.yml")]))}]}]
    pages = []
    for f in sorted((c / "pages").glob("*.yml")):
        pages.append({"name": f.stem, "label": PAGE_LABELS.get(f.stem, f.stem.title()), "file": f"{base}/pages/{f.name}", "fields": to_fields(spec_for([str(f)]))})
    cols.append({"name": f"{pre}pages", "label": f"{tag}Pages", "files": pages})
    for folder, lab, singular, ext in FOLDERS:
        paths = sorted(glob.glob(str(c / folder / f"*.{ext}")))
        if not paths:
            continue
        col = {"name": f"{pre}{folder}", "label": f"{tag}{lab}", "label_singular": singular, "folder": f"{base}/{folder}", "create": True,
               "extension": ext, "fields": to_fields(spec_for(paths)), "summary": "{{title}}"}
        if ext == "md":
            col["format"] = "frontmatter"
            col["slug"] = "{{year}}-{{month}}-{{day}}-{{slug}}"
        else:
            col["format"] = "yml"
            col["slug"] = "{{year}}-{{month}}-{{day}}-{{slug}}" if folder == "events" else "{{slug}}"
        # body must be last and markdown for articles
        cols.append(col)
    legal = sorted((c / "legal").glob("*.md"))
    cols.append({"name": f"{pre}legal", "label": f"{tag}Legal pages", "files": [
        {"name": f.stem, "label": f.stem.replace("-", " ").title(), "file": f"{base}/legal/{f.name}", "fields": to_fields(spec_for([str(f)]))} for f in legal]})
    return cols


def main():
    site_url = yaml.safe_load(open(ROOT / "content" / "site.yml"))["site_url"]
    cols = collections("content") + collections("content/zh", zh=True)
    config = {"backend": {"name": "git-gateway", "branch": "main"}, "media_folder": "static/images/uploads", "public_folder": "/images/uploads",
              "site_url": site_url, "display_url": site_url, "collections": cols}
    header = ("# Decap CMS configuration: what can be edited at yoursite.com/admin\n"
              "# Generated by tools/build_cms_config.py from the content files; re-run it rather than editing this file by hand.\n"
              "# Collections starting with 中文 edit the Chinese site (content/zh).\n"
              "# local_backend: true   # uncomment to edit locally (run `npx decap-server` + `python build.py --serve`)\n")
    (ROOT / "static" / "admin" / "config.yml").write_text(header + yaml.safe_dump(config, sort_keys=False, allow_unicode=True, width=200), encoding="utf-8")
    print(f"Wrote static/admin/config.yml with {len(cols)} collections")


if __name__ == "__main__":
    main()
