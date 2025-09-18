Organic Background demos

Files

- `index.html` - combined demo that includes the CSS layered background and the canvas-based organic background.
- `background.html` - simple CSS-only demo (separate example).
- `background-canvas.js` - lightweight canvas organic background implementation.
- `design_tokens.json` - color palettes and timing constants.
- `BACKGROUND.md` - long-form design guidance and implementation notes.
- `USAGE.md` - integration and accessibility notes.

Preview

Open `background/index.html` in a browser (or serve the folder using `python -m http.server`) and the demo will run. The canvas script auto-appends a fullscreen canvas; use the toggles in the UI to enable/disable layers.

Integration

- Drop the CSS `.background` block into your site and include `background-canvas.js` for a canvas-driven variant.
- Provide a toggle that calls `window.__backgroundCanvas.stop()` / `start()` to disable/enable the canvas layer at runtime.

Accessibility

- Both demos respect `prefers-reduced-motion`.
- Use a semi-opaque scrim behind text for readability.

Performance

- For production environments consider replacing the canvas demo with a shader-based approach (WebGL fragment shader) for best long-running performance.
