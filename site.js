/* ------------------------------------------------------------------
   language toggle + days index. no dependencies.
   ------------------------------------------------------------------ */

(function () {
  "use strict";

  /* ---- language ---------------------------------------------------- */

  var btn = document.getElementById("lang");

  function apply(lang) {
    document.documentElement.setAttribute("lang", lang);
    if (btn) btn.textContent = lang === "en" ? "日本語" : "EN";
    try { localStorage.setItem("lang", lang); } catch (e) {}
  }

  apply(document.documentElement.getAttribute("lang") === "ja" ? "ja" : "en");

  if (btn) {
    btn.addEventListener("click", function () {
      apply(document.documentElement.getAttribute("lang") === "en" ? "ja" : "en");
    });
  }

  /* ---- days -------------------------------------------------------- */

  var grid = document.getElementById("days");
  if (!grid || typeof DAYS === "undefined") return;

  if (!DAYS.length) {
    grid.innerHTML =
      '<p class="empty"><span class="en">Nothing here yet.</span>' +
      '<span class="ja">まだ何もありません。</span></p>';
    return;
  }

  var html = DAYS.map(function (d) {
    var src = "images/days/" + d.file;
    return (
      '<figure>' +
        '<a href="' + src + '">' +
          '<img src="' + src + '" alt="' + d.date + '" loading="lazy">' +
        '</a>' +
        '<figcaption>' +
          (d.en ? '<span class="note en">' + d.en + "</span>" : "") +
          (d.ja ? '<span class="note ja">' + d.ja + "</span>" : "") +
          d.date +
        "</figcaption>" +
      "</figure>"
    );
  }).join("");

  grid.innerHTML = html;
})();
