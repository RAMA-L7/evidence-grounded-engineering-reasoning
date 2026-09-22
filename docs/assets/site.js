/* Shared page behaviour. Every page links this file; nothing here is page
   specific. Progressive enhancement: without JS the page is fully readable. */
(function () {
  'use strict';

  var root = document.documentElement;
  root.classList.add('js');

  /* ---- reveal on scroll -------------------------------------------------
     threshold 0 with a negative bottom margin so tall sections still fire,
     plus a sweep so nothing can stay hidden after a jump link or a restored
     scroll position. */
  var items = [].slice.call(document.querySelectorAll('.reveal'));
  function show(el) {
    el.classList.add('on');
  }
  if (!items.length) {
    /* nothing to do */
  } else if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          show(e.target);
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.14 });
    items.forEach(function (el) { io.observe(el); });

    /* Two guarantees the reference does not need on short pages but a long
       research page does. First, a settle pass at load and on hashchange so a
       restored scroll position or a jump link reveals what is on screen even
       though no intersection event will fire for it. Second, a final settle at
       the end of the document, because the last block of a dense page can be
       shorter than the 14 percent the observer asks for, and stranding real
       content is worse than skipping its entrance. Scrolling itself is left
       entirely to the observer, exactly as on the reference. */
    var settle = function () {
      items.forEach(function (el) {
        if (el.classList.contains('on')) return;
        var r = el.getBoundingClientRect();
        if (r.top < window.innerHeight && r.bottom > 0) show(el);
      });
    };
    var atEnd = function () {
      var doc = document.documentElement;
      var vh = window.innerHeight;
      if ((window.pageYOffset || 0) + vh >= (doc.scrollHeight || 0) - 2) {
        items.forEach(function (el) { if (!el.classList.contains('on')) show(el); });
      }
    };
    settle();
    window.addEventListener('hashchange', settle);
    window.addEventListener('scroll', function () { requestAnimationFrame(atEnd); }, { passive: true });
    atEnd();
  } else {
    items.forEach(show);
  }

  /* ---- opening loader ---------------------------------------------------
     Counts to 100 and lifts away. Removed outright when motion is reduced or
     when the URL carries ?preview, so a screenshot or a reader who asked for
     less motion never meets a curtain. */
  var loader = document.querySelector('.loader');
  if (loader) {
    var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (calm || /[?&]preview\b/.test(window.location.search)) {
      loader.parentNode.removeChild(loader);
    } else {
      (function () {
        var num = loader.querySelector('[data-loader-count]');
        var bar = loader.querySelector('[data-loader-line]');
        var start = performance.now();
        var span = 650;
        var step = function (now) {
          var p = Math.min(1, (now - start) / span);
          var value = Math.round((1 - Math.pow(1 - p, 3)) * 100);
          if (num) num.textContent = String(value);
          if (bar) bar.style.width = value + '%';
          if (p < 1) requestAnimationFrame(step);
          else setTimeout(function () { loader.classList.add('is-done'); }, 100);
        };
        requestAnimationFrame(step);
      })();
    }
  }

  /* ---- section dots ------------------------------------------------------
     A dot per top-level section on the right edge. The dot for the section
     covering the viewport centre lights up; clicking a dot scrolls there.
     Built from the document, so pages need no extra markup. */
  var dotsBox = document.querySelector('.dots');
  if (dotsBox) {
    var sections = [].slice.call(document.querySelectorAll('main > section'));
    var links = [];
    sections.forEach(function (sec, i) {
      if (!sec.id) sec.id = 'sec-' + (i + 1);
      var a = document.createElement('a');
      a.href = '#' + sec.id;
      a.setAttribute('aria-label', 'Section ' + (i + 1));
      dotsBox.appendChild(a);
      links.push(a);
    });
    var paint = function () {
      var mid = (window.innerHeight || 0) / 2;
      var active = 0;
      sections.forEach(function (sec, i) {
        var r = sec.getBoundingClientRect();
        if (r.top <= mid) active = i;
      });
      links.forEach(function (a, i) { a.classList.toggle('is-active', i === active); });
    };
    var queued = false;
    window.addEventListener('scroll', function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(function () { queued = false; paint(); });
    }, { passive: true });
    window.addEventListener('resize', function () { requestAnimationFrame(paint); }, { passive: true });
    paint();
  }

  /* ---- nav state, scroll progress, footer year -------------------------- */
  var nav = document.querySelector('.nav');
  var bar = document.querySelector('.progress');
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      var y = window.pageYOffset || document.documentElement.scrollTop || 0;
      if (nav) nav.classList.toggle('is-scrolled', y > 8);
      if (bar) {
        var max = (document.documentElement.scrollHeight - window.innerHeight) || 1;
        bar.style.width = Math.max(0, Math.min(1, y / max)) * 100 + '%';
      }
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());

  /* ---- overlays (figure viewer) ----------------------------------------- */
  var overlay = document.getElementById('overlay');
  if (overlay) {
    var img = overlay.querySelector('img');
    var cap = overlay.querySelector('[data-overlay-caption]');
    var title = overlay.querySelector('[data-overlay-title]');
    [].slice.call(document.querySelectorAll('[data-figure]')).forEach(function (btn) {
      btn.addEventListener('click', function (ev) {
        ev.preventDefault();
        var src = btn.getAttribute('data-figure');
        if (img) { img.src = src; img.alt = btn.getAttribute('data-figure-alt') || ''; }
        if (title) title.textContent = btn.getAttribute('data-figure-title') || '';
        if (cap) cap.textContent = btn.getAttribute('data-figure-caption') || '';
        overlay.classList.add('open');
      });
    });
    function close() { overlay.classList.remove('open'); }
    overlay.addEventListener('click', function (ev) {
      if (ev.target === overlay || ev.target.hasAttribute('data-overlay-close')) close();
    });
    document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') close(); });
  }

  /* ---- inline detail toggles -------------------------------------------- */
  [].slice.call(document.querySelectorAll('[data-toggle]')).forEach(function (row) {
    row.addEventListener('click', function () {
      var target = document.getElementById(row.getAttribute('data-toggle'));
      if (!target) return;
      var open = target.hasAttribute('hidden');
      if (open) target.removeAttribute('hidden'); else target.setAttribute('hidden', '');
      row.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
})();
