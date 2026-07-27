/* ------------------------------------------------------------------
   stacked-sheet navigation.

   every page is a .sheet, all present at once. the one matching the
   url hash comes to the top; the rest are dealt back into the stack
   in cyclic order, so the shuffle always runs the same direction.
   ------------------------------------------------------------------ */

(function () {
  "use strict";

  document.documentElement.classList.remove("no-js");

  /* ---- language ---------------------------------------------------- */

  var btn = document.getElementById("lang");

  function applyLang(lang) {
    document.documentElement.setAttribute("lang", lang);
    if (btn) btn.textContent = lang === "en" ? "日本語" : "EN";
    try { localStorage.setItem("lang", lang); } catch (e) {}
  }

  applyLang(document.documentElement.getAttribute("lang") === "ja" ? "ja" : "en");

  if (btn) {
    btn.addEventListener("click", function () {
      applyLang(document.documentElement.getAttribute("lang") === "en" ? "ja" : "en");
    });
  }

  /* ---- the deck ---------------------------------------------------- */

  var sheets = [].slice.call(document.querySelectorAll(".sheet"));
  var links = [].slice.call(document.querySelectorAll("nav a[href^='#']"));
  /* routed by data-page, not by id — an id matching the hash would make
     the browser jump-scroll to the section and shove the masthead off screen */
  var names = sheets.map(function (s) { return s.dataset.page; });
  var current = null;

  function show(name, animate) {
    var i = names.indexOf(name);
    if (i < 0) i = 0;
    if (names[i] === current) return;

    var previous = current;
    current = names[i];

    sheets.forEach(function (sheet, j) {
      /* how far back in the stack this sheet sits, counting round */
      var depth = (j - i + sheets.length) % sheets.length;
      var active = depth === 0;

      sheet.classList.toggle("is-active", active);
      sheet.setAttribute("aria-hidden", active ? "false" : "true");
      if (active) sheet.removeAttribute("data-depth");
      else sheet.setAttribute("data-depth", String(depth));

      /* the sheet we just left rides above the other buried one */
      sheet.classList.toggle("is-leaving", animate && sheet.dataset.page === previous);
    });

    links.forEach(function (a) {
      if (a.getAttribute("href") === "#" + current) {
        a.setAttribute("aria-current", "page");
      } else {
        a.removeAttribute("aria-current");
      }
    });

    document.title = sheets[i].dataset.title || "acc8f1";
    document.documentElement.setAttribute("data-page", current);

    if (animate) {
      window.setTimeout(function () {
        sheets.forEach(function (s) { s.classList.remove("is-leaving"); });
      }, 460);
    }
  }

  function fromHash(animate) {
    show((location.hash || "").replace(/^#/, "") || names[0], animate);
  }

  window.addEventListener("hashchange", function () { fromHash(true); });
  fromHash(false);

  /* clicking the sheet that is already on top should do nothing jarring */
  links.forEach(function (a) {
    a.addEventListener("click", function (e) {
      if (a.getAttribute("href") === "#" + current) e.preventDefault();
    });
  });

  /* ---- days -------------------------------------------------------- */

  var grid = document.getElementById("days-grid");
  if (!grid || typeof DAYS === "undefined") return;

  if (!DAYS.length) {
    grid.innerHTML =
      '<p class="empty"><span class="en">Nothing here yet.</span>' +
      '<span class="ja">まだ何もありません。</span></p>';
    return;
  }

  grid.innerHTML = DAYS.map(function (d) {
    var src = "images/days/" + d.file;
    return (
      "<figure>" +
        '<a href="' + src + '">' +
          '<img src="' + src + '" alt="' + d.date + '" loading="lazy">' +
        "</a>" +
        "<figcaption>" +
          (d.en ? '<span class="note en">' + d.en + "</span>" : "") +
          (d.ja ? '<span class="note ja">' + d.ja + "</span>" : "") +
          d.date +
        "</figcaption>" +
      "</figure>"
    );
  }).join("");
})();
