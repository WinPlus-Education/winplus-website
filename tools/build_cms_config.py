#!/usr/bin/env python3
"""
Generates static/admin/config.yml (the /admin editor setup) for English and Chinese.
Run after changing the content structure:  python tools/build_cms_config.py
"""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


def s(name, label, req=True, **kw):
    d = {"name": name, "label": label, "widget": "string", **kw}
    if not req: d["required"] = False
    return d
def t(name, label, req=True):
    d = {"name": name, "label": label, "widget": "text"}
    if not req: d["required"] = False
    return d
def m(name, label, req=True):
    d = {"name": name, "label": label, "widget": "markdown"}
    if not req: d["required"] = False
    return d
def img(name, label):
    return {"name": name, "label": label, "widget": "image", "choose_url": True, "required": False}
def n(name, label):
    return {"name": name, "label": label, "widget": "number", "value_type": "int"}
def b(name, label):
    return {"name": name, "label": label, "widget": "boolean", "default": False, "required": False}
def o(name, label, fields):
    return {"name": name, "label": label, "widget": "object", "collapsed": True, "fields": fields}
def L(name, label, fields, summary=None, req=True):
    d = {"name": name, "label": label, "widget": "list", "collapsed": True, "fields": fields}
    if summary: d["summary"] = summary
    if not req: d["required"] = False
    return d
def SL(name, label, req=True):
    d = {"name": name, "label": label, "widget": "list", "field": {"name": "item", "label": "Item", "widget": "string"}}
    if not req: d["required"] = False
    return d
def date(name, label, fmt="YYYY-MM-DD", time=False):
    d = {"name": name, "label": label, "widget": "datetime", "format": fmt}
    if not time: d.update(date_format="YYYY-MM-DD", time_format=False)
    return d

SEO = [s("seo_title", "SEO: browser tab & Google title"), t("meta_description", "SEO: Google description (about 150 characters)")]
PHOTO = [img("image", "Photo (upload, or paste an image link)"), s("image_alt", "Photo description (accessibility & SEO)", False)]
FAQ = L("faq", "FAQ (also shown in Google results)", [s("q", "Question"), t("a", "Answer")], "{{fields.q}}", False)
TT = [s("title", "Title"), t("text", "Text")]
STAT = lambda name="stats", label="Statistics": L(name, label, [s("number", "Number (e.g. 87)"), s("label", "Label")], "{{fields.number}} {{fields.label}}")
FACTS = L("facts", "Key facts", [s("label", "Label"), s("value", "Value")], "{{fields.label}}: {{fields.value}}")
HEAD3 = [s("eyebrow", "Small label"), s("title", "Title"), t("intro", "Intro")]


def collections(base, prefix, zh=False):
    c = f"{base}/"
    tag = f"{prefix} " if prefix else ""
    site = {"name": "site", "label": "Header, Footer, Contact & Social", "file": f"{c}site.yml", "fields": [
        s("name", "Logo text"), s("name_sub", "Logo subtitle"), s("name_local", "Chinese brand name", False),
        s("company_legal", "Legal company name"), s("tagline", "Tagline (top bar)"),
        *([] if zh else [s("site_url", "Website address (e.g. https://www.winplus.org), used for SEO")]),
        img("default_image", "Default image when sharing links"), t("meta_description", "Default search description"),
        s("founded", "Year founded", False), s("address", "Address", False), SL("area_served", "Countries served (SEO)", False),
        s("email", "Email"), s("phone", "Phone", False), s("wechat_id", "WeChat ID", False), img("wechat_qr", "WeChat QR code"),
        s("cta_text", "Header button text"), s("cta_link", "Header button link"),
        L("nav", "Main menu", [s("label", "Label"), s("link", "Link (e.g. results.html)"),
                               L("children", "Dropdown items", [s("label", "Label"), s("link", "Link")], "{{fields.label}}", False)], "{{fields.label}}"),
        L("utility_links", "Top bar links", [s("label", "Label"), s("link", "Link")], "{{fields.label}}"),
        s("partners_label", "Logo strip label"), t("partners_note", "Logo strip disclaimer", False),
        L("partners", "Logo strip (rolling)", [s("name", "Organization name"), img("logo", "Logo file (PNG/SVG, transparent background)")], "{{fields.name}}"),
        L("social", "Social media", [{"name": "platform", "label": "Platform", "widget": "select",
                                      "options": ["wechat", "xiaohongshu", "linkedin", "instagram", "youtube", "bilibili", "tiktok", "facebook", "x", "weibo"]},
                                     s("label", "Label"), s("url", "Profile link", False)], "{{fields.label}}"),
        o("newsletter", "Newsletter sign-up", [s("title", "Title"), t("text", "Text"), s("button", "Button")]),
        t("footer_blurb", "Footer description"), t("footer_disclaimer", "Footer disclaimer"),
    ]}

    home = {"name": "home", "label": "Home", "file": f"{c}pages/home.yml", "fields": SEO + [
        o("hero", "Hero (top of page)", [s("eyebrow", "Small label"), s("title_line1", "Headline line 1"), s("title_line2", "Headline line 2 (gold)"),
                                        t("subtitle", "Subtitle")] + PHOTO + [s("primary_cta", "Gold button"), s("primary_link", "Gold button link"),
                                        s("secondary_cta", "Outline button"), s("secondary_link", "Outline button link"), s("proof", "Badge on photo", False)]),
        o("results", "Results showcase", [s("eyebrow", "Small label"), s("title", "Title"), t("text", "Text"),
            L("photos", "Photos (3)", [img("image", "Photo"), s("alt", "Photo description"), s("caption", "Caption", False)], "{{fields.caption}}"),
            L("key_stats", "Key numbers (2)", [s("number", "Number"), s("label", "Label"), s("note", "Small note", False)], "{{fields.number}} {{fields.label}}"),
            s("chart_title", "Chart title"), t("chart_note", "Chart note"),
            L("chart", "Chart: offers by university (numbers only)", [s("name", "University"), s("value", "Number of offers", False)], "{{fields.name}}: {{fields.value}}"),
            s("offers_label", "Offers label"),
            L("offer_groups", "Offer groups", [s("label", "Group name (e.g. Ivy League)"), SL("schools", "Universities")], "{{fields.label}}"),
            t("footnote", "Footnote"), s("link_text", "Link text"), s("link", "Link")]),
        o("mission", "Mission", [s("eyebrow", "Small label"), s("title", "Title"),
                                 {"name": "paragraphs", "label": "Paragraphs", "widget": "list", "field": {"name": "p", "label": "Paragraph", "widget": "text"}}] + PHOTO),
        o("offer", "What we offer (3 segments)", [s("eyebrow", "Small label"), s("title", "Title"), t("intro", "Intro"),
            L("segments", "Segments", [s("title", "Title"), t("text", "Text"), SL("points", "Bullet points")] + PHOTO + [s("link", "Link"), s("link_text", "Link text")], "{{fields.title}}")]),
        o("why", "Why WinPlus", [s("eyebrow", "Small label"), s("title", "Title"), L("points", "Points", TT, "{{fields.title}}")]),
        o("events", "Upcoming events section", [s("eyebrow", "Small label"), s("title", "Title"), t("text", "Text"), s("link_text", "Link text"), s("link", "Link")]),
        o("testimonials", "Testimonials section (quotes come from Our Results → In their words)", [s("eyebrow", "Small label"), s("title", "Title"), s("link_text", "Link text"), s("link", "Link")]),
        o("faq", "FAQ", [s("title", "Title"), L("items", "Questions", [s("q", "Question"), t("a", "Answer")], "{{fields.q}}")]),
        o("cta", "Bottom call to action", [s("title", "Title"), t("text", "Text"), s("button", "Button"), s("link", "Link")]),
    ]}

    admissions = {"name": "admissions", "label": "Admissions Counseling (overview)", "file": f"{c}pages/admissions.yml", "fields": SEO + HEAD3 + PHOTO + [
        s("services_title", "Services heading"), t("services_intro", "Services intro"),
        s("diff_title", "Differentiation heading"), t("diff_intro", "Differentiation intro"), L("differentiators", "Differentiators", TT, "{{fields.title}}"),
        s("process_title", "How we work heading"), t("process_intro", "How we work intro"),
        L("process", "How we work steps", [s("title", "Title"), t("text", "Text"), s("deliverable", "You receive"), s("when", "When")], "{{fields.title}}"),
        s("timeline_title", "Timeline heading"), L("timeline", "Timeline by grade", [s("grade", "Grade"), t("focus", "Focus")], "{{fields.grade}}"),
        FAQ, s("cta", "Button text"), s("cta_link", "Button link")]}

    research = {"name": "research", "label": "Research & Internships (overview)", "file": f"{c}pages/research.yml", "fields": SEO + HEAD3 + PHOTO + [
        s("why_title", "Why research heading"), L("why", "Why research matters", TT, "{{fields.title}}"),
        s("method_title", "Method title", False), t("method_text", "Method text", False),
        s("deliverables_title", "Deliverables heading"), t("deliverables_intro", "Deliverables intro"), L("deliverables", "Key deliverables", TT, "{{fields.title}}"),
        s("format_title", "Format heading"), L("format", "Program format", [s("label", "Label"), s("value", "Value")], "{{fields.label}}"),
        L("categories", "Program categories", [s("id", "ID (don't change)"), s("title", "Title")], "{{fields.title}}"),
        FAQ, s("cta_title", "Bottom heading"), t("cta_text", "Bottom text"), s("cta", "Button"), s("cta_link", "Button link")]}

    enrichment = {"name": "enrichment", "label": "Experience Enrichment (overview)", "file": f"{c}pages/enrichment.yml", "fields": SEO + HEAD3 + PHOTO + [
        s("benefits_title", "Benefits heading"), L("benefits", "Benefits", TT, "{{fields.title}}"),
        o("highlight", "Highlight", [s("label", "Label"), s("title", "Title"), t("text", "Text")] + PHOTO),
        s("cta_title", "Bottom heading"), t("cta_text", "Bottom text"), s("cta", "Button"), s("cta_link", "Button link")]}

    results = {"name": "results", "label": "Our Results", "file": f"{c}pages/results.yml", "fields": SEO + HEAD3 + PHOTO + [
        STAT(), t("stats_note", "Statistics note", False), s("chart_title", "Chart title"),
        L("schools", "Acceptance rates (numbers only, e.g. 3.6)", [s("name", "University"), s("general_rate", "General admit rate %", False),
                                                                   s("winplus_rate", "WinPlus rate %", False)], "{{fields.name}}: {{fields.general_rate}}% vs {{fields.winplus_rate}}%"),
        t("footnote", "Footnote"), s("offers_title", "Offers heading"), SL("offers", "Universities admitted to"), t("offers_note", "Offers note", False),
        s("highlights_title", "Student stories heading"),
        L("highlights", "Student stories (with photos)", [s("title", "Title"), s("tag", "Tag"), t("text", "Story")] + PHOTO + [s("link", "Link", False)], "{{fields.title}}"),
        s("stories_title", "Quotes heading"),
        L("stories", "Student quotes (also on home page)", [s("initials", "Initials"), s("admitted_to", "Admitted to"), s("program", "Program"), t("quote", "Quote")], "{{fields.initials}} → {{fields.admitted_to}}"),
        s("testimonials_title", "Testimonials heading"),
        L("testimonials", "Parent & alumni testimonials", [t("quote", "Quote"), s("name", "Name"), s("role", "Role (e.g. Parent, Alumni)")], "{{fields.name}}"),
        s("cta", "Button"), s("cta_link", "Button link")]}

    person = [s("name", "Name"), s("role", "Role"), img("photo", "Photo"), t("bio", "Bio", False)]
    team = {"name": "team", "label": "Our Team", "file": f"{c}pages/team.yml", "fields": SEO + HEAD3 + PHOTO + [
        s("what_title", "What we do heading"), L("what", "What we do", [s("title", "Title"), t("text", "Text"), s("link", "Link")], "{{fields.title}}"),
        s("compare_title", "Comparison heading"),
        o("without", "Without WinPlus", [s("label", "Label"), s("heading", "Heading"), s("center", "Center box"), SL("vendors", "Vendors"), s("note", "Note")]),
        o("with", "With WinPlus", [s("label", "Label"), s("heading", "Heading"), s("center", "Center box"), SL("stages", "Stages")]),
        L("benefits", "Benefits", TT, "{{fields.title}}"),
        s("leaders_title", "Founders heading"), L("leaders", "Founders", person + [s("linkedin", "LinkedIn URL", False)], "{{fields.name}}"),
        s("consultants_title", "Consultants heading"), t("consultants_intro", "Consultants intro"), L("consultants", "Consultants & coaches", person, "{{fields.name}}"),
        s("featured_title", "Featured mentors heading"), t("featured_intro", "Featured mentors intro"),
        L("featured", "Featured mentors", [s("name", "Name"), img("photo", "Photo"), s("background", "Background (organizations)"), s("field", "Field")], "{{fields.name}}"),
        s("network_title", "Mentor network heading"),
        L("network", "Mentor network groups", [s("title", "Title"), t("text", "Text"), s("count", "Count (e.g. 30+)")], "{{fields.title}}"),
        o("team_stat", "Team size", [s("number", "Number"), s("label", "Label")]),
        s("mentors_title", "Program mentors heading"), t("mentors_intro", "Program mentors intro"),
        L("mentors", "Program mentors", [s("role", "Role"), s("org", "Organization"), s("program", "Program"), img("photo", "Photo"), s("link", "Program page link", False)], "{{fields.org}} — {{fields.role}}"),
        s("join_title", "Join heading"), t("join_text", "Join text"), s("join_cta", "Join button"), s("join_link", "Join link")]}

    schools = {"name": "schools", "label": "For Schools (partnerships)", "file": f"{c}pages/schools.yml", "fields": SEO + HEAD3 + PHOTO + [
        s("challenges_title", "Why now heading"), L("challenges", "Why now", [s("letter", "Number/letter"), s("title", "Title"), t("text", "Text")], "{{fields.title}}"),
        s("benefits_title", "Benefits heading"), L("benefits", "Benefits", TT, "{{fields.title}}"),
        s("models_title", "Models heading"), L("models", "Partnership models", TT, "{{fields.title}}"),
        s("roles_title", "Roles heading"), o("roles", "Who does what", [SL("partner", "Partner"), SL("winplus", "WinPlus")]), t("models_note", "Models note"),
        s("services_title", "Services heading"), t("services_intro", "Services intro"),
        L("services_table", "Services table", [s("service", "Service"), s("ages", "For"), t("outcomes", "Key outcomes"), t("edge", "Why it's hard to copy"), s("models", "Models")], "{{fields.service}}"),
        t("services_note", "Services note"),
        s("track_title", "Track record heading"), STAT("track", "Track record numbers"), t("track_note", "Track record note", False),
        s("steps_title", "Steps heading"), L("steps", "Getting started steps", TT, "{{fields.title}}"),
        t("ideal_partners", "Ideal partners"),
        s("contact_title", "Contact heading"), s("contact_name", "Contact name"), s("contact_role", "Contact role"), s("contact_email", "Contact email"),
        s("trusted_label", "Partner logos label"), L("school_logos", "Partner logos", [s("name", "Name"), img("logo", "Logo")], "{{fields.name}}"),
        s("primary_cta", "Button"), s("primary_link", "Button link"), s("secondary_cta", "Download button text"),
        {"name": "secondary_file", "label": "Overview PDF", "widget": "file", "required": False}]}

    simple = [
        {"name": "insights", "label": "Insights (page text)", "file": f"{c}pages/insights.yml", "fields": SEO + HEAD3 + [SL("categories", "Topic filters")]},
        {"name": "events-page", "label": "Events (page text)", "file": f"{c}pages/events.yml", "fields": SEO + HEAD3 + [s("past_title", "Past events heading"), t("empty_text", "Message when no events")]},
        {"name": "how-it-works", "label": "How We Work", "file": f"{c}pages/how-it-works.yml", "fields": SEO + HEAD3 + [
            L("steps", "Steps", TT, "{{fields.title}}"), o("testimonial", "Testimonial", [t("quote", "Quote"), s("name", "Name")]),
            s("primary_cta", "Gold button"), s("primary_link", "Gold link"), s("secondary_cta", "Outline button"), s("secondary_link", "Outline link")]},
        {"name": "contact", "label": "Book Consultation (form page)", "file": f"{c}pages/contact.yml", "fields": SEO + HEAD3 + [
            SL("interests", "'Interested in' options"), t("success_message", "Thank-you message")]},
    ]
    legal = {"name": f"{prefix}legal".replace(" ", "-").lower() or "legal", "label": f"{tag}Legal pages", "files": [
        {"name": n_, "label": l_, "file": f"{c}legal/{n_}.md", "fields": [s("title", "Title"), s("seo_title", "SEO title"), t("meta_description", "SEO description"),
                                                                           date("updated", "Last updated"), m("body", "Text")]}
        for n_, l_ in [("privacy", "Privacy Policy"), ("terms", "Terms & Disclaimer")]]}

    def folder(name, label, singular, sub, fields, summary="{{title}}", sort=None, slug="{{slug}}"):
        d = {"name": name, "label": f"{tag}{label}", "label_singular": singular, "folder": f"{c}{sub}", "create": True,
             "format": "yml", "extension": "yml", "slug": slug, "summary": summary, "fields": fields}
        if sort: d["sortable_fields"] = sort
        return d

    cats = [{"label": "AI & Technology", "value": "ai-technology"}, {"label": "Finance & Business", "value": "finance-business"},
            {"label": "Science & Space", "value": "science-space"}, {"label": "Arts & Media", "value": "arts-media"}]
    services = folder(f"{prefix}admissions-services".lower().replace(" ", "-"), "Admissions Services", "Admissions Service", "admissions", [
        n("order", "Order in lists"), s("title", "Title"), s("short_title", "Short title (menus & breadcrumbs)"),
        s("interest", "Contact form option to pre-select (must match an option on the contact page)", False)] + SEO + [t("summary", "Summary")] + PHOTO + [
        t("who", "Who it's for"), SL("included", "What's included"), L("approach", "Our approach", TT, "{{fields.title}}"),
        s("deadlines_title", "Dates heading"), L("deadlines", "Key dates", [s("label", "Label"), s("date", "Date")], "{{fields.label}}"), FAQ], sort=["order", "title"])
    programs = folder(f"{prefix}programs".lower().replace(" ", "-"), "Research & Internship Programs", "Program", "programs", [
        n("order", "Order in lists"), s("title", "Program title"), {"name": "category", "label": "Category", "widget": "select", "options": cats},
        s("org", "Mentor organization"), s("format", "Format (e.g. Online Internship)")] + SEO + [t("summary", "Summary")] + PHOTO + [
        FACTS, m("overview", "Program overview"), SL("activities", "What students do"), s("mentor", "Mentor title"), t("mentor_bio", "Mentor bio"),
        img("mentor_photo", "Mentor photo"), SL("deliverables", "What students receive"), t("prerequisites", "Who should apply", False), FAQ,
        t("internal_note", "Internal note (not shown on website)", False)], summary="{{org}} — {{title}}", sort=["order", "title", "category"])
    enrich = folder(f"{prefix}enrichment-programs".lower().replace(" ", "-"), "Enrichment Programs", "Enrichment Program", "enrichment", [
        n("order", "Order in lists"), s("title", "Title"), s("short_title", "Short title")] + SEO + [t("summary", "Summary")] + PHOTO + [
        FACTS, m("overview", "Overview"), SL("activities", "What students do"), SL("deliverables", "What students receive"),
        t("highlight", "Highlight story", False), FAQ], sort=["order", "title"])
    events = folder(f"{prefix}events".lower().replace(" ", "-"), "Upcoming Events", "Event", "events", [
        s("title", "Event title"), date("date", "Date & start time", "YYYY-MM-DDTHH:mm:ss", time=True),
        s("time_label", "Time as shown (e.g. 7:00–8:00 PM ET)"), s("type", "Type (e.g. Webinar, Info Session)"),
        s("location", "Location (include 'Online' or '线上' for virtual events)")] + PHOTO + [
        t("summary", "Short summary"), m("details", "Full details", False),
        s("register_url", "External registration link (optional, leave empty to use the built-in form)", False)],
        summary="{{date}} — {{title}}", sort=["date", "title"], slug="{{year}}-{{month}}-{{day}}-{{slug}}")
    posts = {"name": f"{prefix}posts".lower().replace(" ", "-"), "label": f"{tag}Insights Articles", "label_singular": "Article", "folder": f"{c}posts",
             "create": True, "slug": "{{year}}-{{month}}-{{day}}-{{slug}}", "sortable_fields": ["date", "title", "category"], "summary": "{{title}} ({{category}})",
             "fields": [s("title", "Title"), s("seo_title", "SEO title (optional)", False), date("date", "Publish date"),
                        s("category", "Topic (must match a topic filter on the Insights page)"), t("summary", "Short summary (also used for Google)"),
                        img("image", "Cover image"), s("image_alt", "Cover image description", False),
                        s("source", "Originally published on (e.g. WeChat, Xiaohongshu)", False), b("featured", "Feature at top of Insights page"), m("body", "Article")]}

    pages = {"name": f"{prefix}pages".lower().replace(" ", "-"), "label": f"{tag}Pages",
             "files": [home, admissions, research, enrichment, results, team, schools] + simple}
    settings = {"name": f"{prefix}settings".lower().replace(" ", "-"), "label": f"{tag}Site Settings", "files": [site]}
    return [settings, pages, services, programs, enrich, events, posts, legal]


def main():
    site_url = yaml.safe_load(open(ROOT / "content" / "site.yml"))["site_url"]
    cols = collections("content", "") + collections("content/zh", "中文", zh=True)
    # unique, ASCII collection names
    for col in cols:
        col["name"] = col["name"].replace("中文", "zh-")
        if col["name"] == "legal" and col["label"].startswith("中文"):
            col["name"] = "zh-legal"
    config = {"backend": {"name": "git-gateway", "branch": "main"}, "media_folder": "static/images/uploads", "public_folder": "/images/uploads",
              "site_url": site_url, "display_url": site_url, "collections": cols}
    header = ("# Decap CMS configuration: what can be edited at yoursite.com/admin\n"
              "# Generated by tools/build_cms_config.py; edit that script and re-run it rather than editing this file by hand.\n"
              "# Collections starting with 中文 edit the Chinese site (content/zh).\n"
              "# local_backend: true   # uncomment to edit locally (run `npx decap-server` + `python build.py --serve`)\n")
    (ROOT / "static" / "admin" / "config.yml").write_text(header + yaml.safe_dump(config, sort_keys=False, allow_unicode=True, width=200), encoding="utf-8")
    print(f"Wrote static/admin/config.yml with {len(cols)} collections")


if __name__ == "__main__":
    main()
