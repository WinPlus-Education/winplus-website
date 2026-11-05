// WinPlus site behaviour: header, menu, hero slideshow, marquee, reveal, filters,
// carousel, gallery lightbox, consultation form rules and cookie consent.
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- Header: transparent over hero, solid after scrolling ----------
  var header = $("[data-header]");
  var overlay = document.body.classList.contains("has-overlay");
  function onScroll() { if (header && overlay) header.classList.toggle("is-solid", window.scrollY > 40); }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // ---------- Mobile menu ----------
  var toggle = $(".nav-toggle"), nav = $("#site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      header.classList.toggle("menu-open", open);
      document.body.classList.toggle("menu-locked", open);
    });
  }
  $$(".sub-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var sub = btn.nextElementSibling, open = sub.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  // ---------- M1 Hero slideshow: 3s per campus, crossfade with zoom/pan ----------
  var hero = $("[data-slides]");
  if (hero) {
    var slides = $$(".slide", hero);
    var i = 0, timer = null;
    var eager = function (n) { var im = $("img", slides[n % slides.length]); if (im && im.loading === "lazy") im.loading = "eager"; };
    eager(1); eager(2);
    var show = function (n) {
      var prev = slides[i];
      prev.classList.replace("is-active", "was-active");
      setTimeout(function () { prev.classList.toggle("was-active", false); }, 1200);
      i = (n + slides.length) % slides.length;
      slides[i].classList.add("is-active");
      eager(i + 1); eager(i + 2);
    };
    var play = function () { if (!reduce && slides.length > 1) timer = setInterval(function () { show(i + 1); }, 3000); };
    document.addEventListener("visibilitychange", function () { clearInterval(timer); if (!document.hidden) play(); });
    play();
  }

  // ---------- M9 Logo marquee: duplicate the list for a seamless loop ----------
  $$(".marquee-track").forEach(function (track) {
    $$("li", track).forEach(function (li) { var c = li.cloneNode(true); c.setAttribute("aria-hidden", "true"); track.appendChild(c); });
  });

  // ---------- Reveal on scroll ----------
  var rev = $$(".reveal");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    rev.forEach(function (el) { io.observe(el); });
  } else { rev.forEach(function (el) { el.classList.add("is-in"); }); }

  // ---------- M16 Filters (programs, articles): AND across groups ----------
  $$("[data-filters]").forEach(function (box) {
    var target = $(box.getAttribute("data-filters"));
    if (!target) return;
    var items = $$("[data-filter-item]", target), empty = $("[data-filter-empty]");
    var state = {};
    var params = new URLSearchParams(location.search);
    var apply = function () {
      var shown = 0;
      items.forEach(function (it) {
        var ok = Object.keys(state).every(function (g) { return state[g] === "all" || it.getAttribute("data-" + g) === state[g]; });
        it.hidden = !ok; if (ok) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    };
    $$("[data-group]", box).forEach(function (group) {
      var g = group.getAttribute("data-group"), chips = $$(".chip", group);
      state[g] = "all";
      var select = function (chip) {
        chips.forEach(function (c) { var on = c === chip; c.classList.toggle("is-active", on); c.setAttribute("aria-pressed", on ? "true" : "false"); });
        state[g] = chip.getAttribute("data-value");
      };
      chips.forEach(function (chip) { chip.addEventListener("click", function () { select(chip); apply(); }); });
      var want = params.get(g);
      if (want) chips.forEach(function (c) { if (c.getAttribute("data-value") === want) select(c); });
    });
    $$("[data-filter-item]", target).forEach(function (it) { it.classList.add("is-in"); });
    apply();
  });

  // ---------- Testimonial carousel arrows ----------
  $$("[data-carousel]").forEach(function (nav) {
    var track = $(nav.getAttribute("data-carousel"));
    if (!track) return;
    $$("button", nav).forEach(function (b) {
      b.addEventListener("click", function () {
        var card = track.firstElementChild, step = card ? card.getBoundingClientRect().width + 32 : 320;
        track.scrollBy({ left: b.hasAttribute("data-next") ? step : -step, behavior: reduce ? "auto" : "smooth" });
      });
    });
  });

  // ---------- M15 Gallery lightbox ----------
  $$("[data-gallery]").forEach(function (gal) {
    var links = $$("a", gal), at = 0, box = null;
    var render = function () {
      $("img", box).src = links[at].getAttribute("href");
      $("img", box).alt = links[at].getAttribute("data-caption") || "";
      $(".lb-cap", box).textContent = links[at].getAttribute("data-caption") || "";
    };
    var close = function () { if (box) { box.remove(); box = null; document.removeEventListener("keydown", key); } };
    var key = function (e) { if (e.key === "Escape") close(); if (e.key === "ArrowRight") { at = (at + 1) % links.length; render(); } if (e.key === "ArrowLeft") { at = (at - 1 + links.length) % links.length; render(); } };
    links.forEach(function (a, n) {
      a.addEventListener("click", function (e) {
        e.preventDefault(); at = n;
        box = document.createElement("div"); box.className = "lightbox"; box.setAttribute("role", "dialog"); box.setAttribute("aria-modal", "true");
        box.innerHTML = '<img alt=""><p class="lb-cap"></p><button class="lb-close" aria-label="Close">×</button><button class="lb-prev" aria-label="Previous">‹</button><button class="lb-next" aria-label="Next">›</button>';
        document.body.appendChild(box); render();
        $(".lb-close", box).onclick = close;
        $(".lb-prev", box).onclick = function () { at = (at - 1 + links.length) % links.length; render(); };
        $(".lb-next", box).onclick = function () { at = (at + 1) % links.length; render(); };
        box.addEventListener("click", function (ev) { if (ev.target === box) close(); });
        document.addEventListener("keydown", key);
        $(".lb-close", box).focus();
      });
    });
  });

  // ---------- Consultation form: age screening + PRC consents (legal Part 6 §4, §9) ----------
  var form = $("[data-consult-form]");
  if (form) {
    var roleInputs = $$("input[name=role]", form);
    var dobWrap = $("[data-dob]", form), dob = $("input[name=student_dob]", form);
    var country = $("select[name=country]", form);
    var stop = $("[data-age-stop]", form), teen = $("[data-age-teen]", form);
    var rest = $("[data-form-rest]", form), prc = $("[data-prc]", form), prcChild = $("[data-prc-child]", form);
    var role = function () { var r = roleInputs.filter(function (x) { return x.checked; })[0]; return r ? r.value : ""; };
    var age = function () {
      if (!dob || !dob.value) return null;
      var b = new Date(dob.value), n = new Date(), a = n.getFullYear() - b.getFullYear();
      if (n.getMonth() < b.getMonth() || (n.getMonth() === b.getMonth() && n.getDate() < b.getDate())) a--;
      return a;
    };
    var update = function () {
      var r = role(), a = age(), c = country ? country.value : "";
      var strict = c === "CN" || c === "CA-QC";
      dobWrap.hidden = r !== "student";
      dob.required = r === "student";
      var blocked = r === "student" && a !== null && (a < 13 || (strict && a < 14));
      stop.hidden = !blocked;
      teen.hidden = !(r === "student" && a !== null && !blocked && a < 18);
      rest.hidden = blocked || !r;
      $$("input, select, textarea, button", rest).forEach(function (el) { el.disabled = blocked; });
      var isCN = c === "CN";
      prc.hidden = !isCN;
      var transfer = $("input[name=prc_transfer_consent]", form);
      if (transfer) transfer.required = isCN;
      if (prcChild) prcChild.hidden = !(isCN && r === "parent");
    };
    roleInputs.forEach(function (x) { x.addEventListener("change", update); });
    if (dob) dob.addEventListener("change", update);
    if (country) country.addEventListener("change", update);
    update();
    // Pre-fill interest and program from the link (e.g. contact.html?interest=...&program=...)
    var params = new URLSearchParams(location.search);
    var interest = $("select[name=interest]", form);
    if (interest && params.get("interest")) {
      var want = params.get("interest");
      $$("option", interest).forEach(function (o) { if (o.text === want || o.value === want) interest.value = o.value; });
    }
    var program = $("input[name=program]", form);
    if (program && params.get("program")) program.value = params.get("program");
  }

  // ---------- WeChat QR pop-up ----------
  var wbtn = $(".wechat-btn"), wpop = $("#wechat-pop");
  if (wbtn && wpop) wbtn.addEventListener("click", function () { wpop.hidden = !wpop.hidden; wbtn.setAttribute("aria-expanded", wpop.hidden ? "false" : "true"); });

  // ---------- Cookie consent (legal Part 6 §3): analytics load only after consent ----------
  var KEY = "wp_cookie_consent_v1";
  var banner = $("[data-cookie]"), prefs = $("[data-cookie-prefs]"), box = $("[data-cookie-analytics]");
  var read = function () { try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; } };
  var loadAnalytics = function () {
    var id = window.WINPLUS && window.WINPLUS.analytics;
    if (!id || window.__wpAnalytics) return;
    window.__wpAnalytics = true;
    var s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id);
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date()); window.gtag("config", id, { anonymize_ip: true });
  };
  var save = function (analytics) {
    try { localStorage.setItem(KEY, JSON.stringify({ analytics: !!analytics, at: new Date().toISOString() })); } catch (e) {}
    if (banner) banner.hidden = true;
    if (analytics) loadAnalytics();
  };
  var choice = read();
  if (choice && choice.analytics) loadAnalytics();
  if (banner && !choice) banner.hidden = false;
  var on = function (sel, fn) { $$(sel).forEach(function (b) { b.addEventListener("click", fn); }); };
  on("[data-cookie-accept]", function () { save(true); });
  on("[data-cookie-reject]", function () { save(false); });
  on("[data-cookie-open]", function () { prefs.hidden = !prefs.hidden; });
  on("[data-cookie-save]", function () { save(box && box.checked); });
  on("[data-cookie-settings]", function () { var c = read(); if (box) box.checked = !!(c && c.analytics); banner.hidden = false; prefs.hidden = false; });

  // ---------- Fallback: text labels on social buttons if the icon font fails ----------
  window.addEventListener("load", function () {
    var icon = $(".social-btn i");
    if (!icon) return;
    var c = getComputedStyle(icon, "::before").content;
    if (!c || c === "none" || c === "normal" || c === '""') document.documentElement.classList.add("no-icons");
  });
})();
