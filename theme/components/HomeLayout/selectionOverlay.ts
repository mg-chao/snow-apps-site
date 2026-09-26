// Canvas overlay for the homepage preview, matching Snow Shot's intelligent
// selection. Metrics come from ScreenshotCanvasRenderer, ScreenshotSmartSelectionTransition,
// and the selection toolbar's size-only readout. The preview is drawn at 1.5×
// the product's logical pixels, so those metrics are scaled by CAPTURE_SCALE.

export const CAPTURE_SCALE = 1.5;
export const SELECTION_TRANSITION_MS = 101;

const BORDER_PRODUCT_PX = 2;
const BORDER_COLOR = '#4096ff';
const MASK_ALPHA = 128 / 255;
const CHIP_ALPHA = 115 / 255;
const PANEL_HEIGHT = 26;
const PANEL_RADIUS = 6;
const PANEL_PADDING_X = 8;
const PANEL_INSET = 0.5;
const VALUE_INSET = 2;
const SYMBOL_MARGIN = 2;
const UNIT_MARGIN = 2;
const TOOLBAR_GAP = 4;
const VALUE_FONT_PX = 14;

export type SelectionRect = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type SelectionUnit = 'px' | 'dp';

type ClientBox = {
  left: number;
  top: number;
  width: number;
  height: number;
};

export function easeOutQuad(progress: number): number {
  const t = Math.min(1, Math.max(0, progress));
  return t * (2 - t);
}

function qRound(value: number): number {
  return Math.sign(value) * Math.round(Math.abs(value));
}

function sameRect(a: SelectionRect | null, b: SelectionRect | null): boolean {
  if (a === b) {
    return true;
  }
  if (!a || !b) {
    return false;
  }
  return (
    a.x === b.x && a.y === b.y && a.width === b.width && a.height === b.height
  );
}

function quantize(value: number): number {
  return Math.round(value * 2) / 2;
}

export function selectionRectFromClientBoxes(
  windowBox: ClientBox,
  windowOffsetWidth: number,
  targetBox: ClientBox,
): SelectionRect | null {
  const scale = windowBox.width / windowOffsetWidth;
  if (!Number.isFinite(scale) || scale <= 0) {
    return null;
  }
  const width = quantize(targetBox.width / scale);
  const height = quantize(targetBox.height / scale);
  if (width <= 0 || height <= 0) {
    return null;
  }
  return {
    x: quantize((targetBox.left - windowBox.left) / scale),
    y: quantize((targetBox.top - windowBox.top) / scale),
    width,
    height,
  };
}

function interpolateRect(
  start: SelectionRect,
  end: SelectionRect,
  progress: number,
): SelectionRect {
  const lerp = (from: number, to: number) => from + (to - from) * progress;
  return {
    x: lerp(start.x, end.x),
    y: lerp(start.y, end.y),
    width: lerp(start.width, end.width),
    height: lerp(start.height, end.height),
  };
}

class SmartSelectionTransition {
  private enabled = true;
  private hasPresented = false;
  private displayed: SelectionRect | null = null;
  private target: SelectionRect | null = null;
  private from: SelectionRect | null = null;
  private startedAt = 0;
  private running = false;

  setEnabled(enabled: boolean) {
    if (this.enabled === enabled) {
      return;
    }
    this.enabled = enabled;
    if (!enabled && this.running && this.target) {
      this.present(this.target);
    }
  }

  isRunning(): boolean {
    return this.running;
  }

  current(): SelectionRect | null {
    return this.displayed;
  }

  update(selection: SelectionRect, now: number): boolean {
    if (!this.enabled || !this.hasPresented) {
      this.hasPresented = true;
      return this.present(selection);
    }
    if (this.target && sameRect(selection, this.target)) {
      return false;
    }
    this.from = this.displayed ?? selection;
    this.target = selection;
    this.startedAt = now;
    this.running = true;
    return false;
  }

  tick(now: number) {
    if (!this.running || !this.from || !this.target) {
      return;
    }
    const elapsed = Math.max(0, now - this.startedAt);
    if (elapsed >= SELECTION_TRANSITION_MS) {
      this.displayed = this.target;
      this.running = false;
      return;
    }
    this.displayed = interpolateRect(
      this.from,
      this.target,
      easeOutQuad(elapsed / SELECTION_TRANSITION_MS),
    );
  }

  dismiss() {
    this.hasPresented = false;
    this.present(null);
  }

  private present(selection: SelectionRect | null): boolean {
    const changed = !sameRect(this.displayed, selection);
    this.running = false;
    this.displayed = selection;
    this.target = selection;
    this.from = selection;
    return changed;
  }
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function placeSizeChip(
  selection: SelectionRect,
  chipWidth: number,
  chipHeight: number,
  boundsWidth: number,
  boundsHeight: number,
): { x: number; y: number } {
  const gap = TOOLBAR_GAP * CAPTURE_SCALE;
  const left = qRound(selection.x / CAPTURE_SCALE) * CAPTURE_SCALE;
  const top = qRound(selection.y / CAPTURE_SCALE) * CAPTURE_SCALE;
  const right =
    qRound((selection.x + selection.width) / CAPTURE_SCALE) * CAPTURE_SCALE;
  const bottom =
    qRound((selection.y + selection.height) / CAPTURE_SCALE) * CAPTURE_SCALE;
  const candidates = [
    { x: left, y: top - chipHeight - gap },
    { x: right + gap, y: top },
    { x: left - chipWidth - gap, y: top },
    { x: left, y: bottom + gap },
  ];
  for (const candidate of candidates) {
    if (
      candidate.x >= 0 &&
      candidate.y >= 0 &&
      candidate.x + chipWidth <= boundsWidth + 0.5 &&
      candidate.y + chipHeight <= boundsHeight + 0.5
    ) {
      return candidate;
    }
  }
  return {
    x: clamp(candidates[0].x, 0, Math.max(0, boundsWidth - chipWidth)),
    y: clamp(candidates[0].y, 0, Math.max(0, boundsHeight - chipHeight)),
  };
}

function paintSizeChip(
  ctx: CanvasRenderingContext2D,
  selection: SelectionRect,
  scale: number,
  layoutWidth: number,
  layoutHeight: number,
  unit: SelectionUnit,
  fontFamily: string,
) {
  const widthText = String(qRound(selection.width / CAPTURE_SCALE));
  const heightText = String(qRound(selection.height / CAPTURE_SCALE));
  const unitText = unit;
  const fontSize = VALUE_FONT_PX * CAPTURE_SCALE * scale;
  ctx.font = `400 ${fontSize}px ${fontFamily}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';

  const productToDevice = (productPx: number) =>
    productPx * CAPTURE_SCALE * scale;
  const widthLabel =
    ctx.measureText(widthText).width + productToDevice(VALUE_INSET) * 2;
  const heightLabel =
    ctx.measureText(heightText).width + productToDevice(VALUE_INSET) * 2;
  const symbolLabel =
    ctx.measureText('x').width + productToDevice(SYMBOL_MARGIN) * 2;
  const unitLabel =
    ctx.measureText(unitText).width + productToDevice(UNIT_MARGIN);
  const panelWidth =
    productToDevice(PANEL_PADDING_X) * 2 +
    widthLabel +
    symbolLabel +
    heightLabel +
    unitLabel;
  const panelHeight = productToDevice(PANEL_HEIGHT);
  const place = placeSizeChip(
    selection,
    panelWidth / scale,
    panelHeight / scale,
    layoutWidth,
    layoutHeight,
  );
  const originX = Math.round(place.x * scale);
  const originY = Math.round(place.y * scale);
  const inset = productToDevice(PANEL_INSET);
  const radius = productToDevice(PANEL_RADIUS);

  ctx.beginPath();
  ctx.roundRect(
    originX + inset,
    originY + inset,
    Math.max(0, panelWidth - inset * 2),
    Math.max(0, panelHeight - inset * 2),
    radius,
  );
  ctx.fillStyle = `rgba(0, 0, 0, ${CHIP_ALPHA})`;
  ctx.fill();

  ctx.fillStyle = '#ffffff';
  let cursor = originX + productToDevice(PANEL_PADDING_X);
  const textY = originY + panelHeight / 2;
  ctx.fillText(widthText, cursor + productToDevice(VALUE_INSET), textY);
  cursor += widthLabel;
  ctx.fillText('x', cursor + productToDevice(SYMBOL_MARGIN), textY);
  cursor += symbolLabel;
  ctx.fillText(heightText, cursor + productToDevice(VALUE_INSET), textY);
  cursor += heightLabel;
  ctx.fillText(unitText, cursor + productToDevice(UNIT_MARGIN), textY);
}

function paintOverlay(
  ctx: CanvasRenderingContext2D,
  bitmapWidth: number,
  bitmapHeight: number,
  scale: number,
  layoutWidth: number,
  layoutHeight: number,
  selection: SelectionRect | null,
  unit: SelectionUnit,
  fontFamily: string,
) {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, bitmapWidth, bitmapHeight);
  if (!selection) {
    return;
  }

  const x0 = Math.round(selection.x * scale);
  const y0 = Math.round(selection.y * scale);
  const x1 = Math.round((selection.x + selection.width) * scale);
  const y1 = Math.round((selection.y + selection.height) * scale);
  const left = Math.max(0, Math.min(bitmapWidth, x0));
  const top = Math.max(0, Math.min(bitmapHeight, y0));
  const right = Math.max(left, Math.min(bitmapWidth, x1));
  const bottom = Math.max(top, Math.min(bitmapHeight, y1));

  ctx.fillStyle = `rgba(0, 0, 0, ${MASK_ALPHA})`;
  ctx.fillRect(0, 0, bitmapWidth, top);
  ctx.fillRect(0, bottom, bitmapWidth, Math.max(0, bitmapHeight - bottom));
  ctx.fillRect(0, top, left, Math.max(0, bottom - top));
  ctx.fillRect(
    right,
    top,
    Math.max(0, bitmapWidth - right),
    Math.max(0, bottom - top),
  );

  const border = Math.max(
    1,
    Math.round(BORDER_PRODUCT_PX * CAPTURE_SCALE * scale),
  );
  const outside = Math.floor(border / 2);
  const inside = border - outside;
  const span = Math.max(0, x1 - x0) + outside + inside;
  ctx.fillStyle = BORDER_COLOR;
  ctx.fillRect(x0 - outside, y0 - outside, span, border);
  ctx.fillRect(x0 - outside, y1 - inside, span, border);
  const sideHeight = y1 - y0 - inside * 2;
  if (sideHeight > 0) {
    ctx.fillRect(x0 - outside, y0 + inside, border, sideHeight);
    ctx.fillRect(x1 - inside, y0 + inside, border, sideHeight);
  }

  paintSizeChip(
    ctx,
    selection,
    scale,
    layoutWidth,
    layoutHeight,
    unit,
    fontFamily,
  );
}

export class PreviewSelectionOverlay {
  private readonly transition = new SmartSelectionTransition();
  private readonly context: CanvasRenderingContext2D | null;
  private frameId = 0;
  private unit: SelectionUnit = 'px';
  private reducedMotion = false;
  private fontFamily = '';

  constructor(
    private readonly canvas: HTMLCanvasElement,
    private readonly windowEl: HTMLElement,
  ) {
    this.context = canvas.getContext('2d', { alpha: true });
  }

  setUnit(unit: SelectionUnit) {
    if (this.unit === unit) {
      return;
    }
    this.unit = unit;
    this.render();
  }

  setReducedMotion(reduced: boolean) {
    if (this.reducedMotion === reduced) {
      return;
    }
    this.reducedMotion = reduced;
    this.transition.setEnabled(!reduced);
    this.render();
    this.syncFrame();
  }

  moveTo(selection: SelectionRect) {
    const changed = this.transition.update(selection, performance.now());
    if (changed) {
      this.render();
    }
    this.syncFrame();
  }

  dismiss() {
    this.stopFrame();
    this.transition.dismiss();
    this.render();
  }

  render() {
    const ctx = this.context;
    if (!ctx) {
      return;
    }
    const displayed = this.windowEl.getBoundingClientRect();
    const layoutWidth = this.windowEl.offsetWidth;
    const layoutHeight = this.windowEl.offsetHeight;
    if (
      displayed.width < 1 ||
      displayed.height < 1 ||
      layoutWidth < 1 ||
      layoutHeight < 1
    ) {
      return;
    }
    const dpr = window.devicePixelRatio || 1;
    const bitmapWidth = Math.max(1, Math.round(displayed.width * dpr));
    const bitmapHeight = Math.max(1, Math.round(displayed.height * dpr));
    if (
      this.canvas.width !== bitmapWidth ||
      this.canvas.height !== bitmapHeight
    ) {
      this.canvas.width = bitmapWidth;
      this.canvas.height = bitmapHeight;
    }
    if (!this.fontFamily) {
      this.fontFamily =
        getComputedStyle(this.windowEl).fontFamily || 'sans-serif';
    }
    paintOverlay(
      ctx,
      bitmapWidth,
      bitmapHeight,
      bitmapWidth / layoutWidth,
      layoutWidth,
      layoutHeight,
      this.transition.current(),
      this.unit,
      this.fontFamily,
    );
  }

  dispose() {
    this.stopFrame();
  }

  private readonly step = (now: number) => {
    this.frameId = 0;
    this.transition.tick(now);
    this.render();
    if (this.transition.isRunning()) {
      this.frameId = requestAnimationFrame(this.step);
    }
  };

  private syncFrame() {
    if (!this.transition.isRunning()) {
      this.stopFrame();
      return;
    }
    if (this.frameId !== 0) {
      return;
    }
    this.frameId = requestAnimationFrame(this.step);
  }

  private stopFrame() {
    if (this.frameId !== 0) {
      cancelAnimationFrame(this.frameId);
      this.frameId = 0;
    }
  }
}
