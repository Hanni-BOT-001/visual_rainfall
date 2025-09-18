// Lightweight canvas-based organic background using 2D noise (Perlin-like) and blurred radial blobs.
// This is intentionally minimal and uses a simple value-noise function rather than a full simplex implementation
// for portability. It supports reduced-motion and visibility throttling.

(() => {
  const canvas = document.createElement('canvas');
  canvas.style.position = 'fixed';
  canvas.style.inset = '0';
  canvas.style.zIndex = '-1';
  canvas.style.pointerEvents = 'none';
  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  let w = 0, h = 0, dpr = 1;
  let raf = null; let running = true;

  function resize(){
    dpr = window.devicePixelRatio || 1;
    w = innerWidth; h = innerHeight;
    canvas.width = Math.max(1, Math.floor(w * dpr));
    canvas.height = Math.max(1, Math.floor(h * dpr));
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
  }
  resize();
  window.addEventListener('resize', resize);

  // Simple value noise
  function makeGrid(seed){
    const rng = mulberry32(seed);
    const grid = new Float32Array(256);
    for(let i=0;i<256;i++) grid[i] = rng();
    return grid;
  }
  const grid = makeGrid(1337);
  function noise(x,y){
    // tile-safe simple noise
    const xi = Math.floor(x)%256, yi = Math.floor(y)%256;
    const xf = x - Math.floor(x), yf = y - Math.floor(y);
    const a = grid[(xi + yi*13) & 255];
    const b = grid[(xi+1 + yi*13) & 255];
    const c = grid[(xi + (yi+1)*13) & 255];
    const d = grid[(xi+1 + (yi+1)*13) & 255];
    const u = fade(xf), v = fade(yf);
    return lerp(lerp(a,b,u), lerp(c,d,u), v);
  }
  function fade(t){return t*t*(3-2*t)}
  function lerp(a,b,t){return a + (b-a)*t}
  function mulberry32(a){return function(){let t=a+=0x6D2B79F5; t=Math.imul(t^t>>>15,t|1); t^=t+Math.imul(t^t>>>7,t|61); return ((t^(t>>>14))>>>0)/4294967296}}

  let t0 = performance.now()/1000;
  function draw(){
    const now = performance.now()/1000; const dt = now - t0; t0 = now;
    const time = now * 0.08; // slow
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.save();
    ctx.scale(dpr,dpr);

    // Background fill
    ctx.fillStyle = 'rgba(8,10,14,1)'; ctx.fillRect(0,0,w,h);

    // Draw multiple blurred radial blobs, their positions modulated by noise
    const layers = [ {size:0.9, hue:200, sat:70, light:55, alpha:0.16, speed:0.3},
                     {size:0.6, hue:260, sat:80, light:48, alpha:0.12, speed:0.5},
                     {size:0.4, hue:180, sat:72, light:60, alpha:0.10, speed:0.7}];

    for(let li=0;li<layers.length;li++){
      const L = layers[li];
      const cx = w * (0.25 + 0.5 * noise(time*L.speed, li*10));
      const cy = h * (0.25 + 0.5 * noise(time*L.speed + 10, li*10+5));
      const radius = Math.max(200, Math.min(w,h) * L.size * (0.7 + 0.3*noise(time*L.speed+20, li)));

      // draw blurred blob by drawing gradient-filled circle onto an offscreen canvas and then compositing
      const g = ctx.createRadialGradient(cx,cy,0,cx,cy,radius);
      g.addColorStop(0, `hsla(${L.hue}, ${L.sat}%, ${L.light}%, ${L.alpha})`);
      g.addColorStop(1, `hsla(${L.hue}, ${L.sat}%, ${L.light}%, 0)`);
      ctx.globalCompositeOperation = 'screen';
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(cx,cy,radius,0,Math.PI*2); ctx.fill();
    }

    ctx.restore();
    // subtle film grain
    ctx.save();
    ctx.globalAlpha = 0.03; ctx.fillStyle = '#000';
    for(let i=0;i<200;i++){ ctx.fillRect(Math.random()*w, Math.random()*h, 1,1) }
    ctx.restore();

    if(running) raf = requestAnimationFrame(draw); else raf = null;
  }

  function start(){ if(!raf) { running = true; t0 = performance.now()/1000; raf = requestAnimationFrame(draw);} }
  function stop(){ running = false; if(raf) cancelAnimationFrame(raf); raf = null }

  // visibility & reduced motion
  document.addEventListener('visibilitychange', ()=>{ if(document.hidden) stop(); else start(); })
  const mq = window.matchMedia('(prefers-reduced-motion: reduce)'); if(mq && mq.matches) stop();

  // Expose control
  window.__backgroundCanvas = { start, stop };
  start();
})();
