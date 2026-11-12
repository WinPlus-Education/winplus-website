# WinPlus Website

The WinPlus company website, built from the June 2026 mockup. Content is kept separate from design, so text and images can be changed without touching code, either through the online editor at `/admin` or by editing the files in `content/`.

## What's in this folder

| Folder / file | What it is |
|---|---|
| `content/site.yml` | Menu, footer, contact, offices, social, logo strip, cookie banner and form consent text |
| `content/pages/*.yml` | Text for each main page (one file per page) |
| `content/pages/team.yml` | Every person on the site (founders, advisors, mentors). Other pages pick people by `id` |
| `content/admissions/*.yml` | The six admissions programs (US College, US Graduate, US High School, UK, Canada, Australia) |
| `content/programs/*.yml` | Research & internship programs. `status`: open / closed / past; `type`: research / internship; `industry`: field id |
| `content/experiences/*.yml` | Campus Immersion and Global Leadership Conferences |
| `content/events/*.yml` | Events. Past/upcoming is automatic from the date (`end_date` optional); past events can have a `gallery` and `testimonials` |
| `content/posts/*.md` | Insights articles |
| `content/legal/*.md` | Privacy, Terms of Use, Terms of Service, Cookie Policy, Disclaimer, Accessibility (drafts under legal review) |
| `content/zh/` | The Chinese site, same structure |
| `static/images/uploads/` | Photos and logos (`campus/` = home hero slides, `photos/` = WinPlus program photos) |
| `templates/macros.html` | The shared design modules every page is built from |
| `static/assets/css/style.css` | Design tokens (colors, type, spacing) in `:root` |
| `build.py` | Builds the site + sitemap.xml, robots.txt and llms.txt |

**Site map:** Home · Admissions Counseling (+ 6 programs) · Research & Internships (+ programs) · Global Experiences (Campus Immersion, Global Leadership Conferences) · Events (+ event pages) · Our Results · Insights · About Us (Our Story, How We Work, Our Team, For Schools) · FAQ · Contact · Legal pages · Site Map

**Home hero photos:** the slideshow shows every file listed under `hero.slides` in `content/pages/home.yml` that exists. Add landscape photos (2400px+ wide, licensed for web use) as `static/images/uploads/campus/harvard.webp`, `princeton.webp`, `stanford.webp`, `wharton.webp`, `brown.webp` and they appear automatically.

**Forms (Netlify Forms):** `consultation` (contact page: age screening, PRC consents and the consent version are saved with each submission), `newsletter` (footer), `event-registration` (event pages).

**Cookie banner & analytics:** analytics only load after a visitor clicks "Accept Analytics". Add a Google Analytics 4 ID in Site Settings → `analytics_ga4_id`.

**SEO / AI search:** unique titles and descriptions, canonical and hreflang links, structured data (organization with both offices, services, courses, events, people, FAQs, breadcrumbs), `sitemap.xml`, `robots.txt` and `llms.txt`. Old addresses redirect to new ones (see `netlify.toml`).

---

## One-time setup: put the site on Netlify (about 20 minutes)

### 1. Put the code on GitHub
1. Create a free account at github.com (or use your company's).
2. Click **New repository**, name it `winplus-website`, and set it to **Private**.
3. Click **uploading an existing file**, then drag in **everything inside this folder** (not the folder itself). Commit.
   *(Or with git: `git init && git add . && git commit -m "Initial site" && git branch -M main && git remote add origin <repo-url> && git push -u origin main`)*

### 2. Connect Netlify
1. Create a free account at netlify.com and choose **Add new site → Import an existing project → GitHub**.
2. Pick the `winplus-website` repository. Netlify reads the build settings from `netlify.toml`, so leave them as they are.
3. Click **Deploy**. In 1–2 minutes you get a live address like `winplus-abc123.netlify.app`.

### 3. Turn on the online editor
1. In Netlify, open your site → **Project configuration → Identity** → **Enable Identity**.
2. Under **Registration**, choose **Invite only** so no one else can sign up.
3. Under **Services → Git Gateway**, click **Enable Git Gateway**.
4. Go to the **Identity** tab → **Invite users** and invite your own email (and any teammates who will edit).
5. Open the invite email and accept it, then set a password.
6. Go to `https://<your-site>.netlify.app/admin/` and log in.

### 4. Turn on form emails
The "Book Free Consultation" form and the newsletter sign-up use **Netlify Forms**. Submissions appear under **Forms** in Netlify. To get an email for each one: **Project configuration → Notifications → Emails and webhooks → Form submission notifications → Add notification**.

### 5. Connect your domain
**Domain management → Add a domain** → enter `winplus.com` and follow the DNS steps. Netlify adds a free HTTPS certificate automatically.

---

## Editing the site day to day

1. Go to `yourdomain.com/admin/` and log in.
2. Pick **Pages**, **Insights Articles**, or **Site Settings**.
3. Edit text, upload photos, add or reorder list items.
4. Click **Publish**. The live site updates in about a minute.

Every change is saved in GitHub history, so any edit can be undone.

**Tips**
- Images: anywhere you see a grey `[Photo]` box, upload an image in the editor and it replaces the placeholder.
- Partner logos: leave the logo empty to show the name as text, or upload a logo file (SVG or PNG with a transparent background looks best).
- Results chart: type numbers only (e.g. `3.6`). Bars resize automatically. Leave blank to show `[X%]`.
- New article: **Insights Articles → New Article**. Tick "Feature at top" to make it the large card.

## Previewing on your own computer (optional, for developers)

```bash
pip install -r requirements.txt
python build.py --serve      # then open http://localhost:8000
```

To use the editor locally without logging in, uncomment `local_backend: true` in `static/admin/config.yml`, then run `npx decap-server` in a second terminal and open `http://localhost:8000/admin/`.


## Chinese version (中文网站)

- English pages are built from `content/`, Chinese pages from `content/zh/` (same structure). The Chinese site is published under `/zh/` (for example `/zh/results.html`).
- The EN | 中文 switch in the top bar jumps to the same page in the other language.
- In `/admin`, collections starting with **中文** edit the Chinese site.
- Built-in labels (buttons, form fields such as "Learn more" / "了解更多") are translated in `content/i18n/zh.yml`. If a label is missing, the build prints a note listing it.
- Search engines are told which page is which language (hreflang tags in each page and in `sitemap.xml`).

## For developers

- `python tools/build_cms_config.py` regenerates `static/admin/config.yml` from the content files (run it after adding or renaming fields).
- `python tools/check_cms_fields.py` checks that every field in the content files is editable in `/admin` (the editor deletes unknown fields when saving).

## Still to provide
Anything in `[square brackets]` is a placeholder: results data (acceptance rates, % to Ivy/Top 30), testimonials with written consent, remaining campus hero photos, SpaceX and Northwestern logos, mentor photos, office street addresses, contact email, final legal text and the Terms of Service.
