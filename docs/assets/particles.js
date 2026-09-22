/* Constellation engine.
 *
 * This is the reference engine, integrated verbatim: the same render loop, the
 * same shape calculations, the same morph mechanics (shapeMix with a cubic
 * ease), the same per-object screen positions and the same cursor rotation.
 * The only structural adaptation is scene discovery: sections are found from
 * the document itself, and each page shuffles the five objects into its own
 * stable order so no two pages read identically.
 *
 * Decoration only: nothing here carries information, and with reduced motion
 * the field is drawn once and left alone.
 */
(function () {
  'use strict';

  var canvas = document.getElementById('ambient');
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext('2d', { alpha: true });
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  var palette = ['#8052ff', '#ffb829', '#53e1a7', '#e94da4', '#5f8cff', '#f7f6f2'];
  var OBJECTS = ['orb', 'torus', 'cube', 'helix', 'wave'];
  var shapes = {};
  var particleCount = 0;
  var width = 0;
  var height = 0;
  var dpr = 1;
  var activeShape = 'orb';
  var targetShape = 'orb';
  var shapeMix = 1;
  var previousShape = 'scatter';   /* the entrance field every object assembles from */
  var time = 0;
  var scrollY = window.scrollY;
  var particles = [];

  var random = function (min, max) { return min + Math.random() * (max - min); };

  function spherePoint(i, count) {
    var phi = Math.acos(1 - 2 * (i + 0.5) / count);
    var theta = Math.PI * (1 + Math.sqrt(5)) * i;
    var r = random(0.74, 1.05);
    return {
      x: Math.cos(theta) * Math.sin(phi) * r,
      y: Math.cos(phi) * r,
      z: Math.sin(theta) * Math.sin(phi) * r
    };
  }

  function makeShapes() {
    var orb = [], torus = [], cube = [], helix = [], wave = [], scatter = [];
    for (var i = 0; i < particleCount; i++) {
      var s = spherePoint(i, particleCount);
      orb.push({ x: s.x, y: s.y * 1.08, z: s.z });

      var u = random(0, Math.PI * 2);
      var v = random(0, Math.PI * 2);
      var tube = 0.28 + random(-0.05, 0.05);
      torus.push({
        x: (1 + tube * Math.cos(v)) * Math.cos(u),
        y: tube * Math.sin(v),
        z: (1 + tube * Math.cos(v)) * Math.sin(u)
      });

      var face = i % 6;
      var x = random(-1, 1), y = random(-1, 1), z = random(-1, 1);
      if (face === 0) x = -1;
      if (face === 1) x = 1;
      if (face === 2) y = -1;
      if (face === 3) y = 1;
      if (face === 4) z = -1;
      if (face === 5) z = 1;
      cube.push({ x: x * 0.82, y: y * 0.82, z: z * 0.82 });

      var t = (i / particleCount) * Math.PI * 9 - Math.PI * 4.5;
      var strand = i % 2 ? 0 : Math.PI;
      helix.push({
        x: Math.cos(t + strand) * 0.62,
        y: t / 5.2,
        z: Math.sin(t + strand) * 0.62
      });

      var wx = random(-1.5, 1.5);
      var wz = random(-1, 1);
      wave.push({ x: wx, y: Math.sin(wx * 3.2 + wz * 2) * 0.36, z: wz });

      /* The entrance field: every particle begins somewhere in the dust and
         assembles into the first object as the loader curtain lifts. */
      scatter.push({ x: random(-2.8, 2.8), y: random(-2.1, 2.1), z: random(-0.4, 0.4) });
    }
    shapes.orb = orb;
    shapes.torus = torus;
    shapes.cube = cube;
    shapes.helix = helix;
    shapes.wave = wave;
    shapes.scatter = scatter;
  }

  function makeParticles() {
    particles = new Array(particleCount);
    for (var i = 0; i < particleCount; i++) {
      particles[i] = {
        color: palette[i % palette.length],
        size: random(0.55, 1.65),
        alpha: random(0.35, 1),
        phase: random(0, Math.PI * 2),
        scatterX: random(-2.8, 2.8),
        scatterY: random(-2.1, 2.1)
      };
    }
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    /* The reference sizes its field once from the load-time width; rebuilding
       on a real resize (a phone rotation) keeps that behaviour honest. */
    var wanted = width < 700 ? 680 : 1450;
    if (wanted !== particleCount) {
      particleCount = wanted;
      makeParticles();
      makeShapes();
    }
  }

  function rotate(point, ax, ay) {
    var cy = Math.cos(ay), sy = Math.sin(ay);
    var cx = Math.cos(ax), sx = Math.sin(ax);
    var x1 = point.x * cy - point.z * sy;
    var z1 = point.x * sy + point.z * cy;
    return { x: x1, y: point.y * cx - z1 * sx, z: point.y * sx + z1 * cx };
  }

  function positionForScene(name) {
    var mobile = width < 800;
    name = name || activeShape;
    if (name === 'orb' && scrollY < height * 0.9) return { x: mobile ? width * 0.72 : width * 0.73, y: mobile ? height * 0.3 : height * 0.5, scale: Math.min(width, height) * (mobile ? 0.31 : 0.43) };
    if (name === 'torus') return { x: mobile ? width * 0.5 : width * 0.72, y: mobile ? height * 0.28 : height * 0.5, scale: Math.min(width, height) * 0.36 };
    /* The cube sits right of the copy on every page, one step smaller than the
       reference scale so its silhouette reads cleanly beside the text. */
    if (name === 'cube') return { x: mobile ? width * 0.72 : width * 0.72, y: mobile ? height * 0.32 : height * 0.5, scale: Math.min(width, height) * (mobile ? 0.28 : 0.37) };
    if (name === 'helix') return { x: mobile ? width * 0.5 : width * 0.72, y: mobile ? height * 0.34 : height * 0.5, scale: Math.min(width, height) * 0.34 };
    if (name === 'wave') return { x: width * 0.5, y: height * 0.5, scale: Math.min(width, height) * 0.42 };
    return { x: width * 0.5, y: height * 0.46, scale: Math.min(width, height) * 0.35 };
  }

  function drawTriangle(x, y, r, color, alpha, rotation) {
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = color;
    ctx.lineWidth = 0.65;
    ctx.beginPath();
    for (var n = 0; n < 3; n++) {
      var a = rotation + n * Math.PI * 2 / 3;
      var px = x + Math.cos(a) * r;
      var py = y + Math.sin(a) * r;
      if (n) ctx.lineTo(px, py); else ctx.moveTo(px, py);
    }
    ctx.closePath();
    ctx.stroke();
  }

  function render() {
    if (!reducedMotion) time += 0.006;
    mouse.x += (mouse.tx - mouse.x) * 0.035;
    mouse.y += (mouse.ty - mouse.y) * 0.035;
    if (shapeMix < 1) shapeMix = Math.min(1, shapeMix + 0.018);
    if (shapeMix === 1) activeShape = targetShape;

    ctx.clearRect(0, 0, width, height);
    var pos = positionForScene();
    var from = shapes[previousShape] || shapes.scatter;
    var to = shapes[targetShape] || shapes.orb;
    var eased = 1 - Math.pow(1 - shapeMix, 3);
    var rotationY = time + mouse.x * 0.28;
    var rotationX = -0.12 + mouse.y * 0.16;

    var projected = [];
    for (var i = 0; i < particleCount; i++) {
      var p = particles[i];
      var fp = from[i], tp = to[i];
      var base = {
        x: fp.x + (tp.x - fp.x) * eased,
        y: fp.y + (tp.y - fp.y) * eased,
        z: fp.z + (tp.z - fp.z) * eased
      };
      var drift = Math.sin(time * 2 + p.phase) * 0.012;
      base.x += drift;
      base.y += drift * 0.55;
      var r = rotate(base, rotationX, rotationY);
      var perspective = 3.2 / (3.2 + r.z);
      projected.push({
        x: pos.x + r.x * pos.scale * perspective,
        y: pos.y + r.y * pos.scale * perspective,
        z: r.z,
        size: p.size * perspective,
        alpha: p.alpha * (0.55 + perspective * 0.35),
        color: p.color,
        rot: p.phase + time
      });
    }
    projected.sort(function (a, b) { return b.z - a.z; });
    for (var j = 0; j < projected.length; j++) {
      var q = projected[j];
      drawTriangle(q.x, q.y, Math.max(1.1, q.size * 2.2), q.color, q.alpha, q.rot);
    }

    for (var k = 0; k < 46; k++) {
      var d = particles[k];
      if (!d) break;
      var dx = ((d.scatterX * width * 0.55 + time * 24 * (k % 3 + 1)) % (width * 1.2)) + width * 0.1;
      var dy = height * 0.5 + d.scatterY * height * 0.42 + Math.sin(time + d.phase) * 12;
      drawTriangle(dx, dy, d.size * 1.8, d.color, d.alpha * 0.23, d.phase);
    }
    ctx.globalAlpha = 1;
    requestAnimationFrame(render);
  }

  function changeShape(name) {
    if (name === targetShape || !shapes[name]) return;
    previousShape = activeShape;
    targetShape = name;
    activeShape = name;
    shapeMix = 0;
  }

  /* Entrance: the first object assembles out of the scatter field over roughly
     two seconds, timed to complete as the loader curtain finishes lifting. */
  function enterAs(shape) {
    if (!shapes[shape]) return;
    previousShape = 'scatter';
    targetShape = shape;
    activeShape = shape;
    shapeMix = 0;
  }

  /* ---- scenes ------------------------------------------------------------
     Sections are the scenes. Each page assigns the five objects in its own
     shuffled order (stable across reloads), then the observer that follows the
     most visible section drives changeShape, exactly as the reference does. */

  function seedFrom(text) {
    var h = 2166136261;
    for (var i = 0; i < text.length; i++) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function shuffled(list, seed) {
    var out = list.slice();
    var a = seed;
    var next = function () {
      a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    for (var i = out.length - 1; i > 0; i--) {
      var j = Math.floor(next() * (i + 1));
      var swap = out[i];
      out[i] = out[j];
      out[j] = swap;
    }
    return out;
  }

  function initObservers() {
    var scenes = [].slice.call(document.querySelectorAll('main > section'));
    if (!scenes.length) scenes = [].slice.call(document.querySelectorAll('section'));

    var order = shuffled(OBJECTS, seedFrom((window.location.pathname || '') + (document.title || '')));
    scenes.forEach(function (el, i) {
      if (!el.getAttribute('data-shape')) el.setAttribute('data-shape', order[i % order.length]);
    });

    if ('IntersectionObserver' in window && scenes.length) {
      var sceneObserver = new IntersectionObserver(function (entries) {
        var visible = entries.filter(function (e) { return e.isIntersecting; })
          .sort(function (a, b) { return b.intersectionRatio - a.intersectionRatio; })[0];
        if (visible) changeShape(visible.target.getAttribute('data-shape'));
      }, { threshold: [0.25, 0.4, 0.55, 0.7] });
      scenes.forEach(function (el) { sceneObserver.observe(el); });

      /* The entrance, from the first scene's object. The scatter-to-shape
         assembly plays once on load; a reader landing mid page from a restored
         scroll position gets it against the scene they arrived at. */
      var mid = window.innerHeight / 2;
      var first = scenes[0];
      scenes.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top <= mid && r.bottom >= mid) first = el;
      });
      enterAs(first.getAttribute('data-shape'));
    }
  }

  window.addEventListener('resize', resize, { passive: true });
  window.addEventListener('scroll', function () { scrollY = window.scrollY; }, { passive: true });
  window.addEventListener('pointermove', function (e) {
    mouse.tx = (e.clientX / width - 0.5) * 2;
    mouse.ty = (e.clientY / height - 0.5) * 2;
  }, { passive: true });

  function boot() {
    resize();
    initObservers();
    render();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
