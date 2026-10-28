# WinPlus Website

The WinPlus company website, built from the June 2026 mockup. Content is kept separate from design, so text and images can be changed without touching code, either through the online editor at `/admin` or by editing the files in `content/`.

## What's in this folder

| Folder / file | What it is |
|---|---|
| `content/site.yml` | Header, footer, contact info, menu, partner logos |
| `content/pages/*.yml` | The text for each page (one file per page) |
| `content/posts/*.md` | Insights articles (one file per article) |
| `static/images/uploads/` | Uploaded photos and logos |
| `static/admin/` | The online editor (Decap CMS) |
| `templates/` | Page layouts (HTML), only for design changes |
| `static/assets/css/style.css` | Colors, fonts, spacing |
| `build.py` | Turns content + templates into the finished site in `_site/` |
| `netlify.toml` | Tells Netlify how to build the site |

**Pages:** Home · Admissions Counseling · Research & Internships · Our Results · Insights (+ article pages) · For Schools · About WinPlus · How It Works · Book Consultation (form) · Thank-you page

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

## Not built yet
- **中文 (Chinese) version**: the EN | 中文 switch is in the header but inactive. Adding Chinese pages means a translated copy of each content file; the structure supports it.
- **Real photos, logos, results data, testimonials and bios**: all marked with `[ ]` placeholders.
