// Mobile menu toggle
(function () {
  var btn = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Chinese version placeholder
  var zh = document.querySelector(".lang-zh");
  if (zh) zh.addEventListener("click", function (e) { e.preventDefault(); });

  // Insights topic filter
  var chips = document.querySelectorAll(".chip[data-filter]");
  var cards = document.querySelectorAll("[data-cat]");
  var empty = document.querySelector(".empty");
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
      if (empty) empty.hidden = shown > 0;
    });
  });
})();
