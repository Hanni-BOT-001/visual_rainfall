Design notes for dynamic organic background

Goal

Replace static/line-based backgrounds with a dynamic, organic gradient that enhances agent animation without competing with it. Visual direction: soft shapes, continuous color transitions, layered gradients, organic motion, subtle texture, interaction-aware, dark/light modes, and accessibility-first design.

Visual direction

- No lines. Avoid grid/line motifs entirely. Use soft shapes and continuous color transitions.
- Layered gradients. Combine 2–4 overlapping gradients (linear, radial, conic) with varying blend modes and blur to create depth.
- Organic motion. Slow, non-repeating movement (drift + warp) driven by CSS keyframes for simple effects, or programmable shaders/canvas noise for richer flows.
- Subtle texture. Low-contrast, low-frequency noise or film grain so gradients don't look flat.
- Interaction-aware. Slightly accelerate or shift colors when the agent speaks/animates, when the user types or hovers, or when the window is active/inactive.
- Dark/light modes. Provide two palettes and transition smoothly between them.

Animation & behavior

- Base motion: Very slow drift of gradient anchor points — full cycle ~20–40s.
- Micro-warp: Perlin/simplex noise-based distortions with very small amplitude to feel fluid.
- Parallax: Multiple gradient layers move at different speeds relative to pointer/scroll.
- Event pulses: Short, soft luminosity or color shift pulses on agent events (200–600ms).
- Reduce motion: Honor user `prefers-reduced-motion` — fall back to static gradients or very subtle opacity shifts.

Accessibility & legibility

- Ensure high contrast between UI text and animated background; use semi-opaque scrims or softly blurred cards behind text.
- Provide toggle to disable background animation.
- Test text readability for WCAG AA contrast and offer alternate palettes if needed.

Performance considerations

- Prefer GPU-accelerated techniques (CSS transforms, compositing) and avoid layout-thrashing.
- For complex noise/flow, use a shader (WebGL) or an offscreen canvas; scale down canvas and reuse textures.
- Pause/reduce animation when the tab is hidden (`document.visibilityState`) and honor `prefers-reduced-motion`.

Implementation options

- Simple (CSS-only): layered gradients, `background-position` animation, `filter: blur()`, `mix-blend-mode`.
- Mid (Canvas+2D noise): draw blurred shapes + animate positions and alpha; fast and flexible.
- Advanced (WebGL/fragment shader): smooth, non-repeating flow using noise octaves in a shader.

When to choose shader / three.js

If you want flowing veins of color, continuous warps, or interaction-driven fluid motion with low CPU on long sessions — write a small fragment shader combining noise octaves and time-based offsets. Use `requestAnimationFrame`, scale down canvas for high-DPR devices, and throttle when hidden.

Notes

- This document provides the conceptual design and practical guidance for implementing the background. See `design_tokens.json` for palettes and constants, and `background.html` and `background-canvas.js` for working demos and usage examples.
