# Motion & Animation Guidelines

**Version:** 1.0
**Date:** November 6, 2025

---

## Animation Philosophy

**Purpose:** Motion should enhance user experience by providing feedback, showing relationships, and directing attention—never as decoration.

**Principles:**
1. **Purposeful:** Every animation serves a function
2. **Performant:** Smooth 60fps on mobile devices
3. **Quick:** Respect users' time (200-300ms default)
4. **Respectful:** Honor prefers-reduced-motion preferences
5. **Natural:** Follow physics-inspired easing

---

## Animation Duration

### Standard Durations

```css
/* Use these predefined durations */
--duration-instant: 100ms;   /* Immediate feedback (hover, focus) */
--duration-fast: 200ms;      /* Quick transitions (dropdowns, tooltips) */
--duration-base: 300ms;      /* Default animations (modals, slides) */
--duration-slow: 500ms;      /* Deliberate animations (page transitions) */
--duration-slowest: 700ms;   /* Major state changes (rarely used) */
```

**Guidelines:**
- **Mobile:** Favor faster durations (100-300ms)
- **Desktop:** Can use slightly longer (300-500ms)
- **Large elements:** Need more time to feel natural
- **Small elements:** Should be quicker

---

## Easing Functions

### CSS Timing Functions

```css
/* Standard easings */
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

/* Custom easings for specific effects */
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
--ease-smooth: cubic-bezier(0.25, 0.1, 0.25, 1);
--ease-swift: cubic-bezier(0.55, 0, 0.1, 1);
```

**When to Use:**
- **ease-in:** Element leaving the screen
- **ease-out:** Element entering the screen (most common)
- **ease-in-out:** Element staying on screen but changing
- **ease-bounce:** Playful interactions (sparingly)
- **linear:** Progress indicators, loading animations

---

## Core Animations

### 1. Fade In/Out

**Usage:** Element appearance/disappearance

```css
/* Fade In */
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.fade-in {
  animation: fade-in var(--duration-fast) var(--ease-out);
}

/* Fade Out */
@keyframes fade-out {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

.fade-out {
  animation: fade-out var(--duration-fast) var(--ease-in);
}
```

---

### 2. Slide Animations

**Usage:** Modals, drawers, notifications

**Slide Up (Bottom Sheet)**
```css
@keyframes slide-up {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.slide-up {
  animation: slide-up var(--duration-base) var(--ease-out);
}

/* With fade */
@keyframes slide-fade-up {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

**Slide From Right (Side Panel)**
```css
@keyframes slide-in-right {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.slide-in-right {
  animation: slide-in-right var(--duration-base) var(--ease-out);
}
```

---

### 3. Scale Animations

**Usage:** Modals, popovers, emphasis

```css
@keyframes scale-up {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.scale-up {
  animation: scale-up var(--duration-fast) var(--ease-out);
}

/* Scale Down (closing) */
@keyframes scale-down {
  from {
    transform: scale(1);
    opacity: 1;
  }
  to {
    transform: scale(0.95);
    opacity: 0;
  }
}

.scale-down {
  animation: scale-down var(--duration-fast) var(--ease-in);
}
```

**Bounce Scale (Success Feedback)**
```css
@keyframes bounce-scale {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.bounce-scale {
  animation: bounce-scale 600ms var(--ease-bounce);
}
```

---

### 4. Spin (Loading)**

```css
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.spin {
  animation: spin 1s linear infinite;
}

/* Pulse (alternative loading) */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.pulse {
  animation: pulse 2s ease-in-out infinite;
}
```

---

### 5. Shimmer (Loading Content)

```css
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.shimmer {
  background: linear-gradient(
    90deg,
    var(--gray-100) 0%,
    var(--gray-200) 50%,
    var(--gray-100) 100%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s linear infinite;
}
```

---

## Transition Best Practices

### Basic Transitions

```css
/* Good - specific properties */
.button {
  transition: background-color var(--duration-fast) var(--ease-out),
              transform var(--duration-fast) var(--ease-out),
              box-shadow var(--duration-fast) var(--ease-out);
}

/* Avoid - transitioning all properties */
.button {
  transition: all var(--duration-fast);  /* ❌ Performance issue */
}
```

**Properties Safe to Animate (GPU-accelerated):**
- `transform` (translate, scale, rotate)
- `opacity`

**Properties to Avoid Animating:**
- `width` / `height` (causes reflow)
- `margin` / `padding` (causes reflow)
- `top` / `left` / `right` / `bottom` (use transform instead)

---

## Mobile-Specific Animations

### Touch Feedback

**Button Press**
```css
.button {
  transition: transform var(--duration-instant),
              box-shadow var(--duration-instant);
}

.button:active {
  transform: scale(0.98);
  box-shadow: var(--shadow-xs);
}

/* With haptic feedback (via JavaScript) */
/*
  element.addEventListener('touchstart', () => {
    if ('vibrate' in navigator) {
      navigator.vibrate(10);  // 10ms haptic
    }
  });
*/
```

**Card Tap**
```css
.card {
  transition: transform var(--duration-fast);
}

.card:active {
  transform: scale(0.97);
}
```

---

### Pull-to-Refresh

```css
.pull-indicator {
  transform: translateY(-60px) rotate(0deg);
  opacity: 0;
  transition: all var(--duration-fast) var(--ease-out);
}

.pull-indicator.pulling {
  transform: translateY(0) rotate(180deg);
  opacity: 1;
}

.pull-indicator.refreshing {
  animation: spin 1s linear infinite;
}
```

---

### Swipe Gestures

```css
.swipeable-item {
  transform: translateX(0);
  transition: transform var(--duration-base) var(--ease-out);
}

.swipeable-item.swiped-left {
  transform: translateX(-100px);
}

.swipeable-item.swiped-right {
  transform: translateX(100px);
}

/* Snap back if not fully swiped */
.swipeable-item.snap-back {
  transform: translateX(0);
}
```

---

## Page Transitions

### Navigation Animations

**Forward Navigation (New Page)**
```css
@keyframes page-enter-forward {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes page-exit-forward {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(-30%);
    opacity: 0;
  }
}

.page-transition-forward-enter {
  animation: page-enter-forward var(--duration-base) var(--ease-out);
}

.page-transition-forward-exit {
  animation: page-exit-forward var(--duration-base) var(--ease-in);
}
```

**Back Navigation**
```css
@keyframes page-enter-back {
  from {
    transform: translateX(-30%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes page-exit-back {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}
```

---

## Image-Specific Animations

### Image Load (Progressive)

```css
.image-loading {
  background: var(--gray-100);
  position: relative;
  overflow: hidden;
}

.image-loading::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.5),
    transparent
  );
  animation: shimmer 1.5s infinite;
}

.image-loaded {
  animation: fade-in var(--duration-fast) var(--ease-out);
}
```

### Zoom Animation (Image Viewer)

```css
@keyframes zoom-in {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.image-zoom-in {
  animation: zoom-in var(--duration-base) var(--ease-out);
}
```

### Image Processing Feedback

```css
/* Processing overlay */
.processing-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  animation: fade-in var(--duration-fast);
}

/* Progress ring animation */
@keyframes progress-ring {
  0% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: -283;  /* Circumference */
  }
}

.progress-ring {
  animation: progress-ring 2s linear infinite;
}
```

---

## Micro-Interactions

### Icon Animations

**Heart/Like Animation**
```css
@keyframes heart-beat {
  0%, 100% {
    transform: scale(1);
  }
  25% {
    transform: scale(1.3);
  }
  50% {
    transform: scale(0.9);
  }
}

.icon-heart.liked {
  animation: heart-beat 400ms ease-in-out;
  color: var(--error-500);
}
```

**Checkmark Success**
```css
@keyframes checkmark-draw {
  0% {
    stroke-dashoffset: 100;
  }
  100% {
    stroke-dashoffset: 0;
  }
}

.checkmark-path {
  stroke-dasharray: 100;
  animation: checkmark-draw 600ms var(--ease-out) forwards;
}
```

**Download Icon**
```css
@keyframes download-arrow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(4px);
  }
}

.icon-download:hover {
  animation: download-arrow 800ms ease-in-out infinite;
}
```

---

### Number Counter (Statistics)

```css
/* Animated via JavaScript */
/*
function animateValue(element, start, end, duration) {
  const range = end - start;
  const increment = range / (duration / 16);
  let current = start;

  const timer = setInterval(() => {
    current += increment;
    if (current >= end) {
      element.textContent = Math.round(end);
      clearInterval(timer);
    } else {
      element.textContent = Math.round(current);
    }
  }, 16);
}
*/

.stat-number {
  font-variant-numeric: tabular-nums;  /* Prevents jumping */
}
```

---

## Reduced Motion

### Respect User Preferences

```css
/* Default animations */
.animated-element {
  animation: fade-slide-in 300ms ease-out;
}

/* Remove animations for users who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  /* Provide instant feedback instead */
  .animated-element {
    animation: none;
    opacity: 1;
    transform: none;
  }
}
```

**JavaScript Detection:**
```javascript
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

if (!prefersReducedMotion) {
  // Add animations
  element.classList.add('animated');
}
```

---

## Performance Optimization

### GPU Acceleration

```css
/* Use transform and opacity for 60fps */
.optimized-animation {
  transform: translateZ(0);  /* Force GPU layer */
  will-change: transform, opacity;  /* Hint to browser */
}

/* Remove will-change after animation */
.optimized-animation.idle {
  will-change: auto;
}
```

**will-change Guidelines:**
- Only use on animating elements
- Remove when animation completes
- Don't apply to too many elements
- Apply just before animation starts

---

### Debouncing Scroll Animations

```javascript
// Throttle scroll events for performance
let ticking = false;

window.addEventListener('scroll', () => {
  if (!ticking) {
    window.requestAnimationFrame(() => {
      // Your scroll animation logic
      updateScrollAnimations();
      ticking = false;
    });
    ticking = true;
  }
});
```

---

## Animation Timing Reference

| Element | Duration | Easing | Purpose |
|---------|----------|--------|---------|
| Button hover | 100ms | ease-out | Immediate feedback |
| Button click | 100ms | ease-in-out | Press feedback |
| Tooltip | 200ms | ease-out | Quick information |
| Dropdown | 200ms | ease-out | Reveal options |
| Modal | 300ms | ease-out | Enter/exit |
| Bottom Sheet | 300ms | ease-out | Slide up |
| Tab switch | 200ms | ease-in-out | Content change |
| Page transition | 300-400ms | ease-out | Major navigation |
| Image load | 200ms | ease-out | Smooth appearance |
| Toast notification | 300ms | ease-out | Slide in/out |
| Skeleton shimmer | 1.5s | linear | Loading state |
| Spinner | 0.8-1s | linear | Processing |
| Success checkmark | 600ms | ease-out | Feedback |

---

## Animation Guidelines Summary

### DO:
- Use GPU-accelerated properties (transform, opacity)
- Keep animations under 300ms on mobile
- Provide haptic feedback for touch interactions
- Respect prefers-reduced-motion
- Use easing functions (not linear for UI)
- Test on real devices (especially low-end)
- Use animation to show relationships between elements
- Debounce scroll-triggered animations

### DON'T:
- Animate width/height (causes reflow)
- Use `transition: all`
- Create animations longer than 500ms
- Add animation without purpose
- Forget to remove will-change after animation
- Animate too many elements simultaneously
- Use auto-play animations (can be distracting)
- Rely solely on animation to convey information

---

## Testing Checklist

- [ ] Animations run at 60fps on target devices
- [ ] Reduced motion preference is respected
- [ ] Haptic feedback works on supported devices
- [ ] Page transitions feel natural in both directions
- [ ] Loading states provide adequate feedback
- [ ] Touch interactions feel responsive (< 100ms)
- [ ] No janky scrolling or stuttering
- [ ] Animations don't interfere with usability
- [ ] Performance is acceptable on low-end devices
- [ ] Animations pause when app is in background

---

**Next:** [Implementation Examples](IMPLEMENTATION_EXAMPLES.md)
