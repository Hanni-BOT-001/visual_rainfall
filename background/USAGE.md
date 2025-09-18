Usage & integration notes for the organic background demos

Files

- `background.html` — small standalone HTML demo using layered CSS gradients. Good as a simple drop-in for static sites or quick prototypes.
- `background-canvas.js` — lightweight canvas-based demo that draws blurred radial color fields and uses cheap value-noise to slightly modulate positions. Designed to be appended to a page for a richer effect without WebGL.
- `design_tokens.json` — color palettes and timing constants to keep implementations consistent.
- `BACKGROUND.md` — long-form design notes and guidance.

How to use

- CSS demo: Copy the `.background` CSS and the small control script into your site. Place an element with class `background` as the first child of the body or as a fixed background element.

- Canvas demo: Include `<script src="background-canvas.js"></script>` at the end of your body (or import and initialize) to attach a fullscreen organic background. Controls are available at `window.__backgroundCanvas.start()` and `stop()`.

Accessibility & toggles

- Both demos respect `prefers-reduced-motion` and will stop animation when the user prefers reduced motion.
- Provide a UI toggle (example in `background.html`) that calls `window.__backgroundCanvas.stop()` / `start()` or toggles the CSS animation to disable motion.
- For text overlays, use a semi-opaque scrim or blurred card (example `.card` in `background.html`) to ensure readability.

Performance notes

- The CSS-only approach is the lightest on JS but less flexible. It uses GPU compositing-friendly properties (`transform`, `filter`).
- The canvas demo intentionally uses a simple noise approximation and low-frequency visuals. For production, consider switching to a shader-based approach (WebGL) for smoother, cheaper long-running animations.

Development

- Tweak `design_tokens.json` to alter palettes and timings. The canvas demo is intentionally minimal and can be extended with perlin/simplex libraries for richer noise.
