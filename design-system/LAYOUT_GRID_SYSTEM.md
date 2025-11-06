# Layout & Grid System - Mobile-First Image-to-Image Applications

**Version:** 1.0
**Date:** November 6, 2025

---

## Responsive Grid System

### Mobile-First Breakpoints

```css
/* Design mobile-first, enhance progressively */

/* Small phones (default - no media query needed) */
--breakpoint-xs: 0px;       /* 320px+ */

/* Large phones */
--breakpoint-sm: 375px;     /* iPhone 12/13 Pro */

/* Phablets / Small tablets */
--breakpoint-md: 768px;     /* iPad Mini, typical tablets */

/* Tablets / Small desktops */
--breakpoint-lg: 1024px;    /* iPad Pro, landscape tablets */

/* Large desktops */
--breakpoint-xl: 1280px;    /* Desktop monitors */

/* Extra large screens */
--breakpoint-2xl: 1536px;   /* Large desktop monitors */
```

**Media Query Usage:**
```css
/* Mobile first - no media query */
.element {
  width: 100%;
}

/* Tablet and above */
@media (min-width: 768px) {
  .element {
    width: 50%;
  }
}

/* Desktop and above */
@media (min-width: 1024px) {
  .element {
    width: 33.333%;
  }
}
```

---

## Container System

### Max-Width Containers

```css
.container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--space-4);  /* 16px */
  padding-right: var(--space-4);
}

/* Responsive max-widths */
@media (min-width: 640px) {
  .container {
    max-width: 640px;
  }
}

@media (min-width: 768px) {
  .container {
    max-width: 768px;
    padding-left: var(--space-6);  /* 24px */
    padding-right: var(--space-6);
  }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1024px;
  }
}

@media (min-width: 1280px) {
  .container {
    max-width: 1280px;
    padding-left: var(--space-8);  /* 32px */
    padding-right: var(--space-8);
  }
}
```

### Fluid Container

```css
.container-fluid {
  width: 100%;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
}
```

---

## Grid System

### 12-Column Responsive Grid

```css
.grid {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: repeat(4, 1fr);  /* Mobile: 4 columns */
}

@media (min-width: 768px) {
  .grid {
    gap: var(--space-6);
    grid-template-columns: repeat(8, 1fr);  /* Tablet: 8 columns */
  }
}

@media (min-width: 1024px) {
  .grid {
    gap: var(--space-8);
    grid-template-columns: repeat(12, 1fr);  /* Desktop: 12 columns */
  }
}
```

### Column Spans

```css
/* Mobile */
.col-span-1 { grid-column: span 1; }
.col-span-2 { grid-column: span 2; }
.col-span-3 { grid-column: span 3; }
.col-span-4 { grid-column: span 4; }
.col-span-full { grid-column: 1 / -1; }

/* Tablet */
@media (min-width: 768px) {
  .md\:col-span-1 { grid-column: span 1; }
  .md\:col-span-2 { grid-column: span 2; }
  .md\:col-span-4 { grid-column: span 4; }
  .md\:col-span-6 { grid-column: span 6; }
  .md\:col-span-8 { grid-column: span 8; }
}

/* Desktop */
@media (min-width: 1024px) {
  .lg\:col-span-3 { grid-column: span 3; }
  .lg\:col-span-4 { grid-column: span 4; }
  .lg\:col-span-6 { grid-column: span 6; }
  .lg\:col-span-8 { grid-column: span 8; }
  .lg\:col-span-9 { grid-column: span 9; }
  .lg\:col-span-12 { grid-column: span 12; }
}
```

**Example Usage:**
```html
<div class="grid">
  <!-- Full width on mobile, half on tablet, third on desktop -->
  <div class="col-span-4 md:col-span-4 lg:col-span-4">Card 1</div>
  <div class="col-span-4 md:col-span-4 lg:col-span-4">Card 2</div>
  <div class="col-span-4 md:col-span-4 lg:col-span-4">Card 3</div>
</div>
```

---

## Layout Patterns for Image Applications

### 1. Image Gallery Layout

**Masonry Grid (Pinterest-style)**

```css
.gallery-masonry {
  display: grid;
  grid-template-columns: repeat(2, 1fr);  /* Mobile: 2 columns */
  gap: var(--space-2);
  grid-auto-rows: 10px;  /* Small row height for masonry effect */
}

@media (min-width: 768px) {
  .gallery-masonry {
    grid-template-columns: repeat(3, 1fr);  /* Tablet: 3 columns */
    gap: var(--space-3);
  }
}

@media (min-width: 1024px) {
  .gallery-masonry {
    grid-template-columns: repeat(4, 1fr);  /* Desktop: 4 columns */
    gap: var(--space-4);
  }
}

.gallery-masonry__item {
  /* Each item calculates its span based on height */
  grid-row-end: span var(--row-span);
}
```

**Uniform Grid**

```css
.gallery-uniform {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-2);
}

@media (min-width: 768px) {
  .gallery-uniform {
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4);
  }
}

@media (min-width: 1024px) {
  .gallery-uniform {
    grid-template-columns: repeat(4, 1fr);
  }
}

.gallery-uniform__item {
  aspect-ratio: 1 / 1;
  overflow: hidden;
  border-radius: var(--radius-lg);
}

.gallery-uniform__item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

---

### 2. Image Editor Layout

**Split View (Before/After)**

```css
.editor-split {
  display: grid;
  grid-template-columns: 1fr;  /* Mobile: stacked */
  gap: var(--space-4);
  height: calc(100vh - var(--header-height) - var(--bottom-nav-height));
}

@media (min-width: 768px) and (orientation: landscape) {
  .editor-split {
    grid-template-columns: 1fr 1fr;  /* Landscape tablet: side-by-side */
  }
}

@media (min-width: 1024px) {
  .editor-split {
    grid-template-columns: 1fr 1fr;  /* Desktop: side-by-side */
  }
}

.editor-split__pane {
  position: relative;
  overflow: hidden;
  background: var(--gray-900);
  border-radius: var(--radius-lg);
}
```

**Editor with Controls**

```css
.editor-workspace {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
}

.editor-workspace__header {
  flex-shrink: 0;
  height: 56px;
  /* App bar component */
}

.editor-workspace__canvas {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: var(--gray-900);
}

.editor-workspace__controls {
  flex-shrink: 0;
  background: var(--white);
  border-top: 1px solid var(--gray-200);
  padding: var(--space-4);
  max-height: 40vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.editor-workspace__footer {
  flex-shrink: 0;
  height: 56px;
  /* Bottom nav component */
}
```

---

### 3. Feed/Timeline Layout

```css
.feed {
  max-width: 600px;  /* Optimal reading width */
  margin: 0 auto;
  padding: var(--space-4);
}

.feed__item {
  margin-bottom: var(--space-6);
  background: var(--white);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.feed__item-header {
  padding: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.feed__item-image {
  width: 100%;
  display: block;
  background: var(--gray-100);
}

.feed__item-actions {
  padding: var(--space-3) var(--space-4);
  display: flex;
  gap: var(--space-4);
}

.feed__item-caption {
  padding: 0 var(--space-4) var(--space-4);
  font-size: var(--text-sm);
  color: var(--gray-600);
}
```

---

### 4. Modal Full-Screen Image View

```css
.image-viewer {
  position: fixed;
  inset: 0;
  background: var(--black);
  z-index: 200;
  display: flex;
  flex-direction: column;
}

.image-viewer__header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: env(safe-area-inset-top) var(--space-4) var(--space-4);
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.8),
    transparent
  );
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1;
}

.image-viewer__canvas {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  touch-action: pinch-zoom pan-x pan-y;
}

.image-viewer__canvas img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  user-select: none;
  -webkit-user-drag: none;
}

.image-viewer__footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: var(--space-4) var(--space-4) calc(var(--space-4) + env(safe-area-inset-bottom));
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.8),
    transparent
  );
  z-index: 1;
}
```

---

## Safe Area Handling

### iOS Safe Area Insets

```css
/* Ensure content doesn't get cut off by notches, home indicators */

.safe-top {
  padding-top: env(safe-area-inset-top);
}

.safe-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}

.safe-left {
  padding-left: env(safe-area-inset-left);
}

.safe-right {
  padding-right: env(safe-area-inset-right);
}

.safe-all {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}
```

**Viewport Meta Tag:**
```html
<meta name="viewport"
      content="width=device-width, initial-scale=1, viewport-fit=cover">
```

---

## Spacing System

### Consistent Vertical Rhythm

```css
/* Stack spacing utility */
.stack {
  display: flex;
  flex-direction: column;
}

.stack > * + * {
  margin-top: var(--stack-gap, var(--space-4));
}

/* Variants */
.stack-xs { --stack-gap: var(--space-2); }
.stack-sm { --stack-gap: var(--space-3); }
.stack-base { --stack-gap: var(--space-4); }
.stack-lg { --stack-gap: var(--space-6); }
.stack-xl { --stack-gap: var(--space-8); }
```

### Section Spacing

```css
.section {
  padding-top: var(--space-8);
  padding-bottom: var(--space-8);
}

@media (min-width: 768px) {
  .section {
    padding-top: var(--space-12);
    padding-bottom: var(--space-12);
  }
}

@media (min-width: 1024px) {
  .section {
    padding-top: var(--space-16);
    padding-bottom: var(--space-16);
  }
}

/* Section variants */
.section--sm { padding-top: var(--space-6); padding-bottom: var(--space-6); }
.section--lg { padding-top: var(--space-12); padding-bottom: var(--space-12); }
```

---

## Image Aspect Ratios

### Predefined Ratios

```css
.aspect-ratio {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.aspect-ratio::before {
  content: '';
  display: block;
  padding-bottom: var(--aspect-ratio);
}

.aspect-ratio > * {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Common ratios for images */
.aspect-square { --aspect-ratio: 100%; }           /* 1:1 */
.aspect-video { --aspect-ratio: 56.25%; }          /* 16:9 */
.aspect-portrait { --aspect-ratio: 133.333%; }     /* 3:4 */
.aspect-landscape { --aspect-ratio: 75%; }         /* 4:3 */
.aspect-wide { --aspect-ratio: 42.857%; }          /* 21:9 */
.aspect-golden { --aspect-ratio: 61.803%; }        /* φ (golden ratio) */

/* Native CSS aspect-ratio support */
@supports (aspect-ratio: 1) {
  .aspect-square { aspect-ratio: 1 / 1; }
  .aspect-video { aspect-ratio: 16 / 9; }
  .aspect-portrait { aspect-ratio: 3 / 4; }
  .aspect-landscape { aspect-ratio: 4 / 3; }
  .aspect-wide { aspect-ratio: 21 / 9; }
  .aspect-golden { aspect-ratio: 1.618 / 1; }

  .aspect-ratio::before {
    display: none;
  }

  .aspect-ratio > * {
    position: static;
  }
}
```

---

## Flexbox Utilities

### Common Flex Patterns

```css
/* Horizontal centering */
.flex-center-h {
  display: flex;
  justify-content: center;
}

/* Vertical centering */
.flex-center-v {
  display: flex;
  align-items: center;
}

/* Full centering */
.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Space between */
.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Wrap */
.flex-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
}

/* Column on mobile, row on desktop */
.flex-responsive {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

@media (min-width: 768px) {
  .flex-responsive {
    flex-direction: row;
  }
}
```

---

## Z-Index Scale

### Consistent Layering

```css
/* Z-index scale for predictable stacking */
:root {
  --z-base: 0;
  --z-dropdown: 10;
  --z-sticky: 20;
  --z-fixed: 30;
  --z-modal-backdrop: 40;
  --z-modal: 50;
  --z-popover: 60;
  --z-tooltip: 70;
  --z-notification: 80;
  --z-max: 9999;
}

/* Usage */
.header {
  position: sticky;
  z-index: var(--z-sticky);
}

.modal-backdrop {
  z-index: var(--z-modal-backdrop);
}

.modal {
  z-index: var(--z-modal);
}

.toast {
  z-index: var(--z-notification);
}
```

---

## Scroll Behavior

### Smooth Scrolling

```css
html {
  scroll-behavior: smooth;
}

/* Disable for users who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }
}
```

### Scrollable Containers

```css
.scroll-container {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;  /* iOS momentum scrolling */
  overscroll-behavior: contain;  /* Prevent scroll chaining */
  scrollbar-width: thin;
}

/* Hide scrollbar on mobile */
@media (max-width: 767px) {
  .scroll-container {
    scrollbar-width: none;
  }

  .scroll-container::-webkit-scrollbar {
    display: none;
  }
}

/* Horizontal scroll with fade indicators */
.scroll-horizontal {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  position: relative;
}

.scroll-horizontal::before,
.scroll-horizontal::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 24px;
  pointer-events: none;
  z-index: 1;
}

.scroll-horizontal::before {
  left: 0;
  background: linear-gradient(to right, var(--white), transparent);
}

.scroll-horizontal::after {
  right: 0;
  background: linear-gradient(to left, var(--white), transparent);
}
```

---

## Accessibility Helpers

### Screen Reader Only

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

### Skip Links

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  padding: var(--space-3) var(--space-4);
  background: var(--purple-600);
  color: var(--white);
  text-decoration: none;
  border-radius: var(--radius-base);
  z-index: var(--z-max);
  transition: top var(--duration-fast);
}

.skip-link:focus {
  top: var(--space-2);
}
```

---

## Print Styles (for documentation/reports)

```css
@media print {
  *,
  *::before,
  *::after {
    background: transparent !important;
    color: #000 !important;
    box-shadow: none !important;
    text-shadow: none !important;
  }

  a,
  a:visited {
    text-decoration: underline;
  }

  a[href]::after {
    content: " (" attr(href) ")";
  }

  img {
    max-width: 100% !important;
    page-break-inside: avoid;
  }

  h2,
  h3 {
    page-break-after: avoid;
  }

  .no-print {
    display: none !important;
  }
}
```

---

## Performance Optimizations

### Content Visibility (for long lists)

```css
.lazy-section {
  content-visibility: auto;
  contain-intrinsic-size: 500px;  /* Estimated height */
}
```

### GPU Acceleration

```css
.gpu-accelerated {
  transform: translateZ(0);
  will-change: transform;
}

/* Use sparingly - only for animating elements */
.animating {
  will-change: transform, opacity;
}

.animating.idle {
  will-change: auto;
}
```

---

## Layout Best Practices

### DO:
- Design for 320px width minimum (smallest common phone)
- Use flexible units (%, vh, vw, em, rem)
- Test on real devices, not just emulators
- Account for safe areas (notches, home indicators)
- Implement touch-friendly spacing (minimum 8px between elements)
- Use aspect-ratio for image containers to prevent layout shift
- Optimize for thumb-reachable areas on mobile

### DON'T:
- Use fixed pixel widths for layout containers
- Assume screen orientation (portrait vs landscape)
- Forget to test with real content (long names, text, etc.)
- Rely solely on hover states (not available on touch)
- Create horizontal scroll on mobile (except intentional carousels)
- Use viewport units for everything (can cause issues on mobile browsers)
- Ignore safe area insets on notched devices

---

**Next:** [Motion & Animation Guidelines](MOTION_ANIMATION.md)
