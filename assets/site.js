// Small enhancements only. Every page works without this file.
(function () {
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Looping clips: play when on screen, pause when not.
  var vids = document.querySelectorAll("video[data-loop]");
  if (reduce) {
    vids.forEach(function (v) { v.removeAttribute("autoplay"); v.pause(); v.controls = true; });
  } else if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
        else v.pause();
      });
    }, { threshold: 0.25 });
    vids.forEach(function (v) { io.observe(v); });
  }

  // YouTube: load the player only when asked.
  document.querySelectorAll("button.yt").forEach(function (b) {
    b.addEventListener("click", function () {
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + b.dataset.id + "?autoplay=1&rel=0";
      f.title = b.dataset.title || "Video";
      f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      f.allowFullscreen = true;
      var box = document.createElement("div");
      box.className = "yt";
      box.appendChild(f);
      b.replaceWith(box);
    });
  });

  // Lightbox for images.
  var dlg = null, big = null;
  function open(src, alt) {
    if (!dlg) {
      dlg = document.createElement("dialog");
      dlg.className = "lb";
      dlg.innerHTML = '<button type="button" aria-label="Close">Close</button><img alt="">';
      document.body.appendChild(dlg);
      big = dlg.querySelector("img");
      dlg.addEventListener("click", function () { dlg.close(); });
    }
    big.src = src; big.alt = alt || "";
    if (dlg.showModal) dlg.showModal(); else window.open(src);
  }
  document.querySelectorAll("img.zoom").forEach(function (im) {
    im.addEventListener("click", function () { open(im.currentSrc || im.src, im.alt); });
  });

  // Old one-page links (/#nine-acts) now live at /nine-acts/.
  var h = location.hash.replace("#", "");
  var moved = { "nine-acts":1, "night-walk":1, "turin-machine":1, "unseen-city":1, "under-common-care":1, "mind-the-gap":1, "the-bus":1, "interview-dimitris":1, "about":1 };
  if (location.pathname === "/" && moved[h]) location.replace("/" + h + "/");
  if (location.pathname === "/" && (h === "contact")) location.replace("/about/");
})();
