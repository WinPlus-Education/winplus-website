// WinPlus site behaviour: menu, dropdowns, logo marquee, article filters, events, forms.
(function () {
  // Mobile menu
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Dropdown toggles (mobile)
  document.querySelectorAll(".sub-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var sub = btn.nextElementSibling;
      var open = sub.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });


  // Rolling logo strip: duplicate the list so it loops seamlessly
  document.querySelectorAll(".marquee-track").forEach(function (track) {
    var items = Array.prototype.slice.call(track.children);
    items.forEach(function (li) {
      var copy = li.cloneNode(true);
      copy.setAttribute("aria-hidden", "true");
      track.appendChild(copy);
    });
  });

  // Insights topic filter
  var chips = document.querySelectorAll(".chip-btn[data-filter]");
  var cards = document.querySelectorAll("[data-cat]");
  var emptyMsg = document.querySelector("[data-filter-empty]");
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var f = chip.getAttribute("data-filter");
      chips.forEach(function (c) {
        var on = c === chip;
        c.classList.toggle("is-active", on);
        c.setAttribute("aria-pressed", on ? "true" : "false");
      });
      var shown = 0;
      cards.forEach(function (card) {
        var match = f === "all" || card.getAttribute("data-cat") === f;
        card.hidden = !match;
        if (match) shown++;
      });
      if (emptyMsg) emptyMsg.hidden = shown > 0;
    });
  });

  // Hide events whose date has passed (the site may not have been rebuilt yet)
  var now = new Date();
  now.setHours(0, 0, 0, 0);
  var cardsLeft = 0, eventCards = document.querySelectorAll(".event-card[data-date]");
  eventCards.forEach(function (card) {
    var d = new Date(card.getAttribute("data-date"));
    if (!isNaN(d) && d < now) card.hidden = true; else cardsLeft++;
  });
  var evEmpty = document.querySelector("[data-events-empty]");
  if (evEmpty && eventCards.length && !cardsLeft) evEmpty.hidden = false;
  var evPage = document.querySelector("[data-event-date]");
  if (evPage) {
    var ed = new Date(evPage.getAttribute("data-event-date"));
    if (!isNaN(ed) && ed < now) {
      var note = evPage.querySelector(".event-past-note");
      var form = evPage.querySelector("form, #register .btn");
      if (note) note.hidden = false;
      if (form) form.hidden = true;
    }
  }

  // Contact form: pre-fill "interest" and "program" from the link (e.g. contact.html?program=...)
  var params = new URLSearchParams(location.search);
  var interest = document.getElementById("f-interest");
  if (interest && params.get("interest")) {
    var want = params.get("interest");
    Array.prototype.forEach.call(interest.options, function (o) { if (o.text === want) interest.value = o.value || o.text; });
  }
  var program = document.getElementById("f-program");
  if (program && params.get("program")) program.value = params.get("program");

  // WeChat QR pop-up in the footer
  var wbtn = document.querySelector(".wechat-btn");
  var wpop = document.getElementById("wechat-pop");
  if (wbtn && wpop) {
    wbtn.addEventListener("click", function () {
      wpop.hidden = !wpop.hidden;
      wbtn.setAttribute("aria-expanded", wpop.hidden ? "false" : "true");
    });
  }

  // If the icon stylesheet can't load, show text labels on social buttons instead
  window.addEventListener("load", function () {
    var icon = document.querySelector(".social-btn i");
    if (!icon) return;
    var c = getComputedStyle(icon, "::before").content;
    if (!c || c === "none" || c === "normal" || c === '""') document.documentElement.classList.add("no-icons");
  });
})();
