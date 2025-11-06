# Component Library - Mobile-First Image-to-Image Transfer

**Version:** 1.0
**Date:** November 6, 2025

---

## Component Architecture

### Atomic Design Methodology

Components are organized using atomic design principles:

```
Atoms → Molecules → Organisms → Templates → Pages
```

- **Atoms:** Basic building blocks (buttons, inputs, icons)
- **Molecules:** Simple component groups (search bars, image cards)
- **Organisms:** Complex UI sections (navigation bars, image editors)
- **Templates:** Page-level layouts
- **Pages:** Specific instances with real content

---

## Navigation Components

### 1. Bottom Navigation Bar

**Purpose:** Primary navigation for mobile apps, easily accessible with thumb

**Anatomy:**
- Container: Fixed bottom position, safe-area padding
- Items: 3-5 navigation items (optimal: 4)
- Icons: 24x24px, filled when active
- Labels: 12px, optional (show on active only to save space)
- Active indicator: Color change + icon fill

**Specifications:**
```css
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  padding-bottom: env(safe-area-inset-bottom);
  background: var(--white);
  border-top: 1px solid var(--gray-200);
  box-shadow: var(--shadow-lg);
  display: flex;
  justify-content: space-around;
  z-index: 100;
}

.bottom-nav__item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 60px;
  gap: 2px;
  color: var(--gray-500);
  transition: color var(--duration-fast) var(--ease-out);
}

.bottom-nav__item--active {
  color: var(--purple-600);
}

.bottom-nav__icon {
  width: 24px;
  height: 24px;
}

.bottom-nav__label {
  font-size: 10px;
  font-weight: var(--font-medium);
  letter-spacing: var(--tracking-wide);
}
```

**Navigation Items:**
1. **Home** - Main feed/gallery
2. **Upload** - New image input
3. **Process** - Transformation center
4. **Library** - Saved results
5. **Profile** - Settings/account

**Accessibility:**
- Minimum touch target: 48x48dp
- Clear focus indicators
- ARIA labels for screen readers
- Haptic feedback on selection (mobile native)

---

### 2. Top Navigation Bar (App Bar)

**Purpose:** Contextual navigation, page titles, actions

**Anatomy:**
- Height: 56px (mobile), 64px (tablet+)
- Safe area: Status bar padding
- Leading: Back button or menu
- Title: Centered or left-aligned
- Actions: Icon buttons (max 2-3)

**Specifications:**
```css
.app-bar {
  position: sticky;
  top: 0;
  height: 56px;
  padding-top: env(safe-area-inset-top);
  background: var(--white);
  border-bottom: 1px solid var(--gray-200);
  display: flex;
  align-items: center;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
  z-index: 99;
}

.app-bar__leading {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.app-bar__title {
  flex: 1;
  font-size: var(--text-h4);
  font-weight: var(--font-semibold);
  color: var(--gray-900);
  padding: 0 var(--space-4);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.app-bar__actions {
  display: flex;
  gap: var(--space-2);
}
```

**States:**
- Default: White background
- Scrolled: Add shadow for depth
- Transparent: On hero images (with blur background)

---

### 3. Tab Bar

**Purpose:** Switch between views within the same context

**Anatomy:**
- Container: Full width, scrollable if needed
- Tabs: 2-5 items optimal
- Indicator: Bottom border or pill background
- Text: 14px medium weight

**Specifications:**
```css
.tab-bar {
  display: flex;
  border-bottom: 1px solid var(--gray-200);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.tab-bar::-webkit-scrollbar {
  display: none;
}

.tab {
  flex-shrink: 0;
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--gray-600);
  border-bottom: 2px solid transparent;
  transition: all var(--duration-fast) var(--ease-out);
  cursor: pointer;
}

.tab--active {
  color: var(--purple-600);
  border-bottom-color: var(--purple-600);
}
```

---

## Image Components

### 1. Image Upload Component

**Purpose:** Primary entry point for images - camera, gallery, or file system

**Mobile-Optimized Features:**
- Direct camera access
- Photo library integration
- Drag-and-drop (tablets)
- Paste from clipboard
- URL import

**Specifications:**
```css
.image-upload {
  position: relative;
  width: 100%;
  min-height: 240px;
  border: 2px dashed var(--gray-300);
  border-radius: var(--radius-lg);
  background: var(--gray-50);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
  gap: var(--space-4);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.image-upload:hover,
.image-upload--dragover {
  border-color: var(--purple-500);
  background: var(--purple-50);
}

.image-upload__icon {
  width: 48px;
  height: 48px;
  color: var(--purple-500);
}

.image-upload__title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--gray-900);
}

.image-upload__subtitle {
  font-size: var(--text-sm);
  color: var(--gray-500);
  text-align: center;
}

.image-upload__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: center;
}
```

**Action Buttons:**
- Primary: "Choose from Library" (purple button)
- Secondary: "Take Photo" (outline button)
- Tertiary: "From URL" (text button)

**File Input (Hidden):**
```html
<input
  type="file"
  accept="image/jpeg,image/png,image/webp"
  capture="environment"
  multiple
  aria-label="Upload image"
/>
```

**Progressive Upload States:**
1. **Idle:** Dashed border, upload icon
2. **Hover/Drag:** Solid border, purple tint
3. **Uploading:** Progress bar, percentage
4. **Success:** Checkmark, preview thumbnail
5. **Error:** Red border, error message

---

### 2. Image Preview Component

**Purpose:** Display uploaded/processed images with zoom and inspect capabilities

**Features:**
- Pinch-to-zoom support
- Pan when zoomed
- Image metadata display
- Comparison mode (before/after slider)

**Specifications:**
```css
.image-preview {
  position: relative;
  width: 100%;
  background: var(--gray-900);
  border-radius: var(--radius-base);
  overflow: hidden;
  touch-action: pan-x pan-y pinch-zoom;
}

.image-preview__image {
  width: 100%;
  height: auto;
  display: block;
  object-fit: contain;
  max-height: 60vh;
  user-select: none;
  -webkit-user-drag: none;
}

.image-preview__overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: var(--space-4);
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.6) 0%,
    transparent 100%
  );
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.image-preview__metadata {
  font-size: var(--text-xs);
  color: var(--white);
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-full);
}

.image-preview__actions {
  display: flex;
  gap: var(--space-2);
}
```

**Zoom Controls:**
- Pinch gesture: Native zoom
- Double-tap: Toggle 2x zoom
- Buttons: +/- zoom controls
- Reset: Fit to container

**Comparison Slider:**
```css
.comparison-slider {
  position: relative;
  overflow: hidden;
  touch-action: pan-y;
}

.comparison-slider__after {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  clip-path: inset(0 50% 0 0);
}

.comparison-slider__handle {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--white);
  cursor: ew-resize;
  transform: translateX(-50%);
}

.comparison-slider__handle::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 44px;
  height: 44px;
  background: var(--white);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: var(--shadow-lg);
}
```

---

### 3. Image Card Component

**Purpose:** Display image thumbnails in galleries, grids, or lists

**Anatomy:**
- Container: Rounded card with shadow
- Thumbnail: Aspect ratio preserved
- Overlay: Quick actions on touch/hover
- Metadata: Title, date, status

**Specifications:**
```css
.image-card {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--white);
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-fast) var(--ease-out);
}

.image-card:active {
  transform: scale(0.98);
  box-shadow: var(--shadow-xs);
}

.image-card__thumbnail {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  display: block;
  background: var(--gray-100);
}

.image-card__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.7) 0%,
    transparent 50%
  );
  opacity: 0;
  transition: opacity var(--duration-fast) var(--ease-out);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: var(--space-4);
}

.image-card:hover .image-card__overlay,
.image-card:focus-within .image-card__overlay {
  opacity: 1;
}

.image-card__title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--white);
  margin-bottom: var(--space-1);
}

.image-card__meta {
  font-size: var(--text-xs);
  color: rgba(255, 255, 255, 0.8);
}
```

**Variants:**
- **Square:** `aspect-ratio: 1/1` (default)
- **Landscape:** `aspect-ratio: 16/9`
- **Portrait:** `aspect-ratio: 3/4`
- **Free:** No aspect ratio constraint

---

## Transformation Controls

### 1. Slider Component

**Purpose:** Adjust transformation parameters (strength, intensity, etc.)

**Mobile Optimization:**
- Large touch area (44px minimum)
- Haptic feedback at 25% intervals
- Value display always visible
- Reset double-tap

**Specifications:**
```css
.slider {
  width: 100%;
  padding: var(--space-4) 0;
}

.slider__label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.slider__label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--gray-700);
}

.slider__value {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--purple-600);
  min-width: 48px;
  text-align: right;
}

.slider__track {
  position: relative;
  height: 4px;
  background: var(--gray-200);
  border-radius: var(--radius-full);
  cursor: pointer;
}

.slider__fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  background: var(--purple-600);
  border-radius: var(--radius-full);
  transition: width var(--duration-instant);
}

.slider__thumb {
  position: absolute;
  top: 50%;
  width: 24px;
  height: 24px;
  background: var(--white);
  border: 3px solid var(--purple-600);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  cursor: grab;
  box-shadow: var(--shadow-base);
  transition: transform var(--duration-fast) var(--ease-out);
}

.slider__thumb:active {
  cursor: grabbing;
  transform: translate(-50%, -50%) scale(1.2);
}
```

**Input Range (Native):**
```html
<input
  type="range"
  min="0"
  max="100"
  value="50"
  step="1"
  aria-label="Transformation strength"
  aria-valuemin="0"
  aria-valuemax="100"
  aria-valuenow="50"
/>
```

**With Presets:**
```css
.slider__presets {
  display: flex;
  justify-content: space-between;
  margin-top: var(--space-3);
  gap: var(--space-2);
}

.slider__preset {
  flex: 1;
  padding: var(--space-2);
  font-size: var(--text-xs);
  text-align: center;
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-sm);
  background: var(--white);
  color: var(--gray-700);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.slider__preset--active {
  background: var(--purple-600);
  border-color: var(--purple-600);
  color: var(--white);
}
```

**Presets Example:** Low (25%) | Medium (50%) | High (75%) | Max (100%)

---

### 2. Color Picker Component

**Purpose:** Select colors for style transfer or color adjustments

**Mobile-Optimized Features:**
- Large touch targets
- Preset color swatches
- Eyedropper tool (from image)
- HSL sliders for fine control
- Recent colors history

**Specifications:**
```css
.color-picker {
  background: var(--white);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  box-shadow: var(--shadow-base);
}

.color-picker__preview {
  width: 100%;
  height: 80px;
  border-radius: var(--radius-base);
  border: 1px solid var(--gray-300);
  margin-bottom: var(--space-4);
  position: relative;
  overflow: hidden;
}

.color-picker__preview-color {
  width: 100%;
  height: 100%;
  background: currentColor;
}

.color-picker__preview-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: var(--space-2) var(--space-3);
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  color: var(--white);
  text-align: center;
}

.color-picker__swatches {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.color-swatch {
  aspect-ratio: 1;
  border-radius: var(--radius-sm);
  border: 2px solid var(--gray-200);
  cursor: pointer;
  transition: all var(--duration-fast);
  position: relative;
}

.color-swatch--active {
  border-color: var(--purple-600);
  box-shadow: 0 0 0 2px var(--purple-100);
}

.color-swatch:active {
  transform: scale(0.9);
}
```

**HSL Sliders:**
```html
<div class="color-picker__sliders">
  <div class="color-picker__slider">
    <label>Hue</label>
    <input type="range" min="0" max="360" />
  </div>
  <div class="color-picker__slider">
    <label>Saturation</label>
    <input type="range" min="0" max="100" />
  </div>
  <div class="color-picker__slider">
    <label>Lightness</label>
    <input type="range" min="0" max="100" />
  </div>
</div>
```

**Eyedropper Button:**
```css
.eyedropper-button {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--purple-600);
  color: var(--white);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
  cursor: pointer;
}
```

---

### 3. Style Selector Component

**Purpose:** Choose from predefined transformation styles

**Anatomy:**
- Scrollable horizontal list
- Style preview thumbnails
- Style name and description
- Selected indicator

**Specifications:**
```css
.style-selector {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding: var(--space-4) 0;
  margin: 0 calc(var(--space-4) * -1);
  padding-left: var(--space-4);
}

.style-selector::-webkit-scrollbar {
  display: none;
}

.style-selector__list {
  display: flex;
  gap: var(--space-3);
  padding-right: var(--space-4);
}

.style-card {
  flex-shrink: 0;
  width: 120px;
  cursor: pointer;
}

.style-card__thumbnail {
  width: 120px;
  height: 120px;
  border-radius: var(--radius-lg);
  object-fit: cover;
  border: 3px solid transparent;
  transition: all var(--duration-fast) var(--ease-out);
  box-shadow: var(--shadow-sm);
}

.style-card--active .style-card__thumbnail {
  border-color: var(--purple-600);
  box-shadow: 0 0 0 2px var(--purple-100), var(--shadow-md);
  transform: scale(1.05);
}

.style-card__name {
  margin-top: var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--gray-700);
  text-align: center;
}

.style-card--active .style-card__name {
  color: var(--purple-600);
}
```

**Scroll Hint:**
- Fade gradient on edges
- Scroll indicator dots
- "Swipe for more" hint on first use

---

## Buttons & Actions

### 1. Primary Button

**Purpose:** Main call-to-action

**Specifications:**
```css
.button-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  min-height: 44px;
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--white);
  background: var(--purple-600);
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  box-shadow: var(--shadow-sm);
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.button-primary:hover {
  background: var(--purple-700);
  box-shadow: var(--shadow-base);
}

.button-primary:active {
  transform: scale(0.98);
  box-shadow: var(--shadow-xs);
}

.button-primary:disabled {
  background: var(--gray-300);
  color: var(--gray-500);
  cursor: not-allowed;
  box-shadow: none;
}
```

**Variants:**
- **Full Width:** `width: 100%` (mobile)
- **Large:** `min-height: 52px; padding: 0 32px`
- **Small:** `min-height: 36px; padding: 8px 16px; font-size: 14px`

### 2. Secondary Button

```css
.button-secondary {
  /* Same base as primary */
  background: var(--white);
  color: var(--purple-600);
  border: 2px solid var(--purple-600);
}

.button-secondary:hover {
  background: var(--purple-50);
}
```

### 3. Icon Button

**Purpose:** Compact action button with icon only

```css
.button-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 50%;
  color: var(--gray-700);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.button-icon:active {
  background: var(--gray-100);
  transform: scale(0.95);
}
```

### 4. Floating Action Button (FAB)

**Purpose:** Primary action, always accessible

```css
.fab {
  position: fixed;
  bottom: calc(var(--space-6) + 56px); /* Above bottom nav */
  right: var(--space-4);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--accent-gradient);
  color: var(--white);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  z-index: 98;
}

.fab:active {
  transform: scale(0.95);
  box-shadow: var(--shadow-md);
}

.fab__icon {
  width: 24px;
  height: 24px;
}
```

**Extended FAB:**
```css
.fab--extended {
  width: auto;
  padding: 0 var(--space-6);
  border-radius: var(--radius-full);
  gap: var(--space-2);
}

.fab__label {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
}
```

---

## Feedback Components

### 1. Progress Bar

**Purpose:** Show loading/processing progress

```css
.progress-bar {
  width: 100%;
  height: 4px;
  background: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
  position: relative;
}

.progress-bar__fill {
  height: 100%;
  background: var(--purple-600);
  border-radius: var(--radius-full);
  transition: width var(--duration-base) var(--ease-out);
}

/* Indeterminate (unknown progress) */
.progress-bar--indeterminate .progress-bar__fill {
  width: 30%;
  animation: progress-indeterminate 1.5s ease-in-out infinite;
}

@keyframes progress-indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}
```

**With Label:**
```html
<div class="progress">
  <div class="progress__label">
    <span>Processing image...</span>
    <span>67%</span>
  </div>
  <div class="progress-bar">
    <div class="progress-bar__fill" style="width: 67%"></div>
  </div>
</div>
```

### 2. Loading Spinner

**Purpose:** Indicate loading state

```css
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--gray-200);
  border-top-color: var(--purple-600);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Small variant */
.spinner--sm {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

/* Large variant */
.spinner--lg {
  width: 60px;
  height: 60px;
  border-width: 6px;
}
```

### 3. Toast Notification

**Purpose:** Brief feedback messages

```css
.toast {
  position: fixed;
  bottom: calc(var(--space-6) + 56px);
  left: var(--space-4);
  right: var(--space-4);
  padding: var(--space-4);
  background: var(--gray-900);
  color: var(--white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  z-index: 101;
  animation: toast-slide-up var(--duration-base) var(--ease-out);
}

@keyframes toast-slide-up {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.toast__icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.toast__message {
  flex: 1;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

/* Success variant */
.toast--success {
  background: var(--success-600);
}

/* Error variant */
.toast--error {
  background: var(--error-600);
}
```

**Auto-dismiss:** 3-5 seconds
**Action:** Optional undo/retry button

---

## Modal & Overlay Components

### 1. Bottom Sheet

**Purpose:** Mobile-native modal alternative

```css
.bottom-sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--white);
  border-top-left-radius: var(--radius-xl);
  border-top-right-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  z-index: 102;
  transform: translateY(100%);
  transition: transform var(--duration-base) var(--ease-out);
}

.bottom-sheet--open {
  transform: translateY(0);
}

.bottom-sheet__handle {
  width: 40px;
  height: 4px;
  background: var(--gray-300);
  border-radius: var(--radius-full);
  margin: var(--space-3) auto;
}

.bottom-sheet__content {
  padding: var(--space-4);
  max-height: 80vh;
  overflow-y: auto;
}
```

**Backdrop:**
```css
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 101;
  opacity: 0;
  transition: opacity var(--duration-base);
}

.backdrop--visible {
  opacity: 1;
}
```

### 2. Modal Dialog

**Purpose:** Desktop-style modal (tablets/desktop)

```css
.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.9);
  width: calc(100% - 32px);
  max-width: 480px;
  max-height: 90vh;
  background: var(--white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  opacity: 0;
  transition: all var(--duration-base) var(--ease-out);
  z-index: 103;
}

.modal--open {
  transform: translate(-50%, -50%) scale(1);
  opacity: 1;
}

.modal__header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--gray-200);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal__title {
  font-size: var(--text-h3);
  font-weight: var(--font-semibold);
  color: var(--gray-900);
}

.modal__content {
  padding: var(--space-6);
  overflow-y: auto;
  max-height: calc(90vh - 140px);
}

.modal__footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--gray-200);
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
}
```

---

*Continue to implementation examples...*
