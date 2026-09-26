/* Narration player. One surface for two languages: the audio element's source
   is swapped rather than a second player being added, so only one set of
   controls is ever on screen and English is what it opens on.

   The visualiser is a ribbon of thin traces drawn from the low frequency part
   of the narration. It is animated only while sound is actually playing;
   paused and finished both rest on a single flat line in the same tint.

   Progressive enhancement: the script reveals the custom surface only when it
   can actually run it, so with scripting off the native audio element remains
   the player, and if Web Audio is unavailable the ribbon is driven by a free
   running wave so the player never looks broken. */
(function () {
  'use strict';

  var box = document.querySelector('[data-audio]');
  if (!box) return;

  var audio = box.querySelector('[data-audio-el]');
  var playBtn = box.querySelector('[data-audio-play]');
  var seek = box.querySelector('[data-audio-seek]');
  var fill = box.querySelector('[data-audio-fill]');
  var thumb = box.querySelector('[data-audio-thumb]');
  var curEl = box.querySelector('[data-audio-cur]');
  var durEl = box.querySelector('[data-audio-dur]');
  var langEl = box.querySelector('[data-audio-lang]');
  var viz = box.querySelector('[data-audio-viz]');
  var langBtns = [].slice.call(box.querySelectorAll('[data-lang]'));
  if (!audio || !playBtn || !seek) return;

  var LANGS = {
    en: {
      src: box.getAttribute('data-src-en'),
      label: 'English narration',
      spoken: 'English',
      duration: box.getAttribute('data-dur-en') || '0:00'
    },
    te: {
      src: box.getAttribute('data-src-te'),
      label: 'Telugu narration',
      spoken: 'Telugu',
      duration: box.getAttribute('data-dur-te') || '0:00'
    }
  };
  var lang = 'en';

  box.classList.add('is-ready');
  audio.removeAttribute('controls');

  function fmt(seconds) {
    if (!isFinite(seconds) || seconds < 0) seconds = 0;
    seconds = Math.floor(seconds);
    var m = Math.floor(seconds / 60);
    var s = seconds % 60;
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  function setPct(p) {
    p = Math.max(0, Math.min(1, p));
    var pct = (p * 100) + '%';
    if (fill) fill.style.width = pct;
    if (thumb) thumb.style.left = pct;
    seek.setAttribute('aria-valuenow', String(Math.round(p * 100)));
  }

  function syncTime() {
    var d = audio.duration;
    var t = audio.currentTime;
    if (curEl) curEl.textContent = fmt(t);
    if (isFinite(d) && d > 0) {
      if (durEl) durEl.textContent = fmt(d);
      setPct(t / d);
      seek.setAttribute('aria-valuetext', fmt(t) + ' of ' + fmt(d));
    } else {
      seek.setAttribute('aria-valuetext', fmt(t) + ' of ' + LANGS[lang].duration);
    }
  }

  function setPlaying(on) {
    playBtn.classList.toggle('is-playing', on);
    playBtn.setAttribute('aria-label',
      (on ? 'Pause ' : 'Play ') + LANGS[lang].spoken + ' narration');
  }

  /* ---- audio graph ------------------------------------------------------
     A media-element source can be created only once per element, and a page
     opened straight from disk is treated as an opaque origin, so the graph is
     built lazily on the first play and only over http(s). Any failure leaves
     the audio element untouched: it still plays, the ribbon runs free. */
  var ac = null;
  var analyser = null;
  var lf = null;
  var lfAnalyser = null;
  var lfTime = null;
  var raf = 0;
  var graphFailed = false;

  var g = viz ? viz.getContext('2d') : null;
  var dpr = 1;
  var cw = 0;
  var ch = 0;

  function buildGraph() {
    if (ac) return true;
    if (graphFailed) return false;
    if (location.protocol === 'file:' || !viz || !g) { graphFailed = true; return false; }
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) { graphFailed = true; return false; }
    try {
      ac = new AC();
      var node = ac.createMediaElementSource(audio);
      /* The audible path stays full band and untouched. */
      node.connect(ac.destination);
      /* Both analysers hang off that path as side branches: one full band, one
         behind a low pass. The trace is drawn from the low passed branch,
         which is what makes the ribbon flow instead of turning into a dense
         scribble at this width. */
      analyser = ac.createAnalyser();
      analyser.fftSize = 256;
      node.connect(analyser);
      lf = ac.createBiquadFilter();
      lf.type = 'lowpass';
      lf.frequency.value = 150;
      lf.Q.value = 0.7;
      lfAnalyser = ac.createAnalyser();
      lfAnalyser.fftSize = 2048;
      lfAnalyser.smoothingTimeConstant = 0.35;
      node.connect(lf);
      lf.connect(lfAnalyser);
      lfTime = new Uint8Array(lfAnalyser.fftSize);
      return true;
    } catch (e) {
      graphFailed = true;
      ac = null;
      analyser = null;
      lf = null;
      lfAnalyser = null;
      lfTime = null;
      return false;
    }
  }

  function sizeViz() {
    if (!viz || !g) return;
    var rect = viz.getBoundingClientRect();
    cw = Math.max(1, Math.round(rect.width));
    ch = Math.max(1, Math.round(rect.height));
    dpr = Math.min(2, window.devicePixelRatio || 1);
    viz.width = Math.round(cw * dpr);
    viz.height = Math.round(ch * dpr);
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    for (var i = 0; i < POINTS; i++) XS[i] = i * (cw / (POINTS - 1));
  }

  /* ---- the ribbon -------------------------------------------------------
     One smooth wave, drawn as a bundle of thin traces. Each trace in the
     bundle carries a slightly smaller amplitude, so the bundle opens widest
     where the wave is tall and closes into a single line where the wave
     flattens. A smooth taper at both ends takes the whole bundle to nothing,
     which is what keeps it from reading as a panel dropped on the page. */

  var LINES = 24;
  var POINTS = 140;
  /* How far the outermost strand is shifted along the wave, in sample points.
     The shift is what makes neighbouring strands cross near the centre line
     and weave, rather than merely nesting inside each other. */
  var WEAVE = 16;
  var wave = new Array(POINTS).fill(0);
  var waveTmp = new Array(POINTS).fill(0);
  var lastT = 0;
  var gain = 1;
  var ref = 0;
  var XS = new Array(POINTS).fill(0);
  var TAPER = new Array(POINTS);

  /* Full amplitude across the middle, easing to nothing over the outer tenth
     at each end, and keeping only the slow part of the signal so the bundle
     never turns into a dense scribble at small widths. */
  (function () {
    for (var i = 0; i < POINTS; i++) {
      var t = Math.min(i, POINTS - 1 - i) / (POINTS - 1);
      TAPER[i] = t >= 0.10 ? 1 : Math.pow(t / 0.10, 0.6);
    }
  })();

  /* Monochrome, as drawn: plain white strands whose crossings and fans build
     the density, on the site's black. White on the void is 21:1, far past the
     3:1 non-text requirement. */
  var STRAND = 'rgba(255,255,255,0.5)';
  var REST = 'rgba(255,255,255,0.35)';

  /* Read the low passed wave into a target shape, then ease the drawn shape
     toward it. The analyser hands back a fresh sample window every frame, and
     at 60fps that makes the pattern jump several cycles between frames: on a
     narrow phone strip that reads as fast jitter even though the motion is
     locked to the narration. Easing the drawn shape toward each new window
     keeps the lock while slowing what the eye sees to a calm pace, on any
     frame rate. The gain is eased on the same clock, so the bundle breathes
     instead of pumping. */
  function readWave(dt) {
    var len = lfTime.length;
    var per = Math.max(1, Math.floor(len / POINTS));
    var peak = 0;
    var i, k;
    for (i = 0; i < POINTS; i++) {
      var sum = 0;
      var base = i * per;
      for (k = 0; k < per; k++) sum += (lfTime[(base + k) % len] - 128) / 128;
      waveTmp[i] = sum / per;
    }
    var prev = waveTmp.slice();
    for (i = 1; i < POINTS - 1; i++) waveTmp[i] = (prev[i - 1] + prev[i] * 2 + prev[i + 1]) / 4;
    for (i = 0; i < POINTS; i++) {
      var a = Math.abs(waveTmp[i]);
      if (a > peak) peak = a;
    }
    /* The low band of speech is a small signal, so the ribbon is normalised
       against a slowly decaying reference peak rather than the frame's own
       peak. The bundle then fills the strip at any level, and falls back to
       the resting line within about a second of the narration going quiet. */
    ref = Math.max(peak, ref * Math.pow(0.97, dt * 60));
    var want = ref > 0.0008 ? Math.min(400, 0.9 / ref) : 1;
    gain += (want - gain) * Math.min(1, 0.12 * dt * 60);
    var ease = 1 - Math.pow(1 - 0.12, dt * 60);
    for (i = 0; i < POINTS; i++) wave[i] += (waveTmp[i] - wave[i]) * ease;
  }

  /* The same shape without any audio to read: a travelling wave, so a reader
     who opened the page from disk still sees the intended design. */
  function freeWave(now) {
    var s = now / 1000;
    for (var i = 0; i < POINTS; i++) {
      var x = i / (POINTS - 1);
      wave[i] = 0.6 * Math.sin(x * 6.2 - s * 1.4) * (0.5 + 0.5 * Math.sin(x * 3.8));
    }
    gain = 1;
  }

  function draw(live) {
    if (!g || !viz) return;
    g.clearRect(0, 0, cw, ch);
    var mid = Math.round(ch / 2) + 0.5;

    if (!live) {
      g.lineWidth = 1;
      g.strokeStyle = REST;
      g.beginPath();
      g.moveTo(0, mid);
      g.lineTo(cw, mid);
      g.stroke();
      return;
    }

    var amp = ch / 2 - 4;
    var i, L;
    g.lineWidth = 1;
    g.lineJoin = 'round';
    g.strokeStyle = STRAND;
    for (L = 0; L < LINES; L++) {
      var u = L / (LINES - 1);
      /* Deep amplitude spread and an alternating phase: the outer strands
         carry about half the height of the innermost one and cross it twice
         per cycle, which is what opens the weave into visible fans instead of
         a thin band. */
      var scale = 1 - 0.52 * u;
      var phase = u * Math.PI;
      var shift = Math.round(u * WEAVE);
      g.beginPath();
      for (i = 0; i < POINTS; i++) {
        var j = i + shift;
        if (j >= POINTS) j -= POINTS;
        var v = wave[j] * gain * TAPER[i] * scale;
        v += Math.sin(phase) * 0.5 * TAPER[i] * Math.cos(3.1 * (i / (POINTS - 1)) * Math.PI + phase);
        if (v > 1) v = 1; else if (v < -1) v = -1;
        var y = mid - v * amp;
        if (i) g.lineTo(XS[i], y); else g.moveTo(XS[i], y);
      }
      g.stroke();
    }
  }

  function loop(now) {
    raf = requestAnimationFrame(loop);
    var dt = lastT ? Math.min(0.1, (now - lastT) / 1000) : 0.016;
    lastT = now;
    if (lfAnalyser && lfTime) {
      lfAnalyser.getByteTimeDomainData(lfTime);
      readWave(dt);
    } else {
      freeWave(now || performance.now());
    }
    draw(true);
  }

  function startViz() {
    if (raf) return;
    lastT = 0;
    raf = requestAnimationFrame(loop);
  }

  function stopViz() {
    if (raf) { cancelAnimationFrame(raf); raf = 0; }
    lastT = 0;
    draw(false);
  }

  /* ---- transport --------------------------------------------------------- */
  playBtn.addEventListener('click', function () {
    if (audio.paused || audio.ended) {
      var p = audio.play();
      if (p && p.catch) p.catch(function () { setPlaying(false); stopViz(); });
    } else {
      audio.pause();
    }
  });

  function seekTo(clientX) {
    var rect = seek.getBoundingClientRect();
    var d = audio.duration;
    if (!rect.width || !isFinite(d) || d <= 0) return;
    var p = (clientX - rect.left) / rect.width;
    audio.currentTime = Math.max(0, Math.min(1, p)) * d;
    syncTime();
  }
  seek.addEventListener('click', function (ev) { seekTo(ev.clientX); });
  seek.addEventListener('keydown', function (ev) {
    var d = audio.duration;
    if (!isFinite(d) || d <= 0) return;
    var step = 5;
    if (ev.key === 'ArrowRight' || ev.key === 'ArrowUp') {
      audio.currentTime = Math.min(d, audio.currentTime + step);
      syncTime(); ev.preventDefault();
    } else if (ev.key === 'ArrowLeft' || ev.key === 'ArrowDown') {
      audio.currentTime = Math.max(0, audio.currentTime - step);
      syncTime(); ev.preventDefault();
    } else if (ev.key === 'Home') {
      audio.currentTime = 0; syncTime(); ev.preventDefault();
    } else if (ev.key === 'End') {
      audio.currentTime = d; syncTime(); ev.preventDefault();
    } else if (ev.key === ' ' || ev.key === 'Enter') {
      ev.preventDefault(); playBtn.click();
    }
  });

  audio.addEventListener('play', function () {
    if (buildGraph() && ac && ac.state === 'suspended') {
      var r = ac.resume();
      if (r && r.catch) r.catch(function () {});
    }
    setPlaying(true);
    startViz();
  });
  audio.addEventListener('pause', function () { setPlaying(false); stopViz(); });
  audio.addEventListener('ended', function () {
    setPlaying(false);
    stopViz();
    try { audio.currentTime = 0; } catch (e) {}
    if (curEl) curEl.textContent = fmt(0);
    setPct(0);
  });
  audio.addEventListener('timeupdate', syncTime);
  audio.addEventListener('loadedmetadata', syncTime);
  audio.addEventListener('durationchange', syncTime);

  /* ---- language ---------------------------------------------------------- */
  function setLang(next) {
    if (!LANGS[next] || next === lang) return;
    var wasPlaying = !audio.paused && !audio.ended;
    lang = next;
    audio.pause();
    audio.src = LANGS[next].src;
    audio.load();
    if (langEl) langEl.textContent = LANGS[next].label;
    if (durEl) durEl.textContent = LANGS[next].duration;
    if (curEl) curEl.textContent = fmt(0);
    setPct(0);
    seek.setAttribute('aria-valuetext', fmt(0) + ' of ' + LANGS[next].duration);
    langBtns.forEach(function (b) {
      var on = b.getAttribute('data-lang') === next;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    setPlaying(false);
    stopViz();
    if (wasPlaying) {
      var p = audio.play();
      if (p && p.catch) p.catch(function () {});
    }
  }
  langBtns.forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.getAttribute('data-lang')); });
  });

  /* ---- boot -------------------------------------------------------------- */
  if (!audio.getAttribute('src')) audio.src = LANGS[lang].src;
  if (durEl) durEl.textContent = LANGS[lang].duration;
  setPlaying(false);
  syncTime();
  if (viz) {
    sizeViz();
    draw(false);
    window.addEventListener('resize', function () {
      sizeViz();
      if (!raf) draw(false);
    }, { passive: true });
  }
})();
