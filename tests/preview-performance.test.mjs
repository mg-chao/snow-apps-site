import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { describe, it } from 'node:test';
import { runInNewContext } from 'node:vm';
import { JsxEmit, ModuleKind, transpileModule } from 'typescript';

const overlaySource = readFileSync(
  new URL(
    '../theme/components/HomeLayout/selectionOverlay.ts',
    import.meta.url,
  ),
  'utf8',
);
const overlayCode = transpileModule(overlaySource, {
  compilerOptions: { module: ModuleKind.CommonJS },
}).outputText;

function frames() {
  let nextId = 0;
  const callbacks = new Map();
  return {
    request(callback) {
      callbacks.set(++nextId, callback);
      return nextId;
    },
    cancel(id) {
      callbacks.delete(id);
    },
    tick(now) {
      const pending = [...callbacks.values()];
      callbacks.clear();
      for (const callback of pending) callback(now);
    },
    get pending() {
      return callbacks.size;
    },
  };
}

function snowScene() {
  const raf = frames();
  const stats = { layoutReads: 0, bitmapWrites: 0, clears: 0, uploads: [] };
  const surfaces = [
    { left: 240, top: 500, right: 1200, width: 960, height: 600 },
    { left: 530, top: 400, right: 700, width: 170, height: 44 },
    { left: 720, top: 400, right: 890, width: 170, height: 44 },
  ].map((rect) => ({
    getBoundingClientRect() {
      stats.layoutReads++;
      return rect;
    },
  }));
  const rect = { left: 0, top: 0, width: 1440, height: 1100 };
  const gl = new Proxy(
    {},
    {
      get(_, name) {
        if (['createShader', 'createProgram', 'createBuffer'].includes(name))
          return () => ({});
        if (name === 'bufferData') return (_, data) => stats.uploads.push(data);
        if (name === 'clear') return () => stats.clears++;
        return () => {};
      },
    },
  );
  let bitmapWidth = 0;
  let bitmapHeight = 0;
  let cleanup;
  const canvas = {
    parentElement: {
      querySelector: () => surfaces[0],
      querySelectorAll: () => surfaces.slice(1),
    },
    getBoundingClientRect() {
      stats.layoutReads++;
      return rect;
    },
    getContext: () => gl,
    addEventListener() {},
    removeEventListener() {},
    set width(value) {
      stats.bitmapWrites++;
      bitmapWidth = value;
    },
    get width() {
      return bitmapWidth;
    },
    set height(value) {
      stats.bitmapWrites++;
      bitmapHeight = value;
    },
    get height() {
      return bitmapHeight;
    },
  };
  const exports = {};
  const runtime = {
    exports,
    require: () => ({
      useRef: () => ({ current: canvas }),
      useEffect: (effect) => {
        cleanup = effect();
      },
      jsx: () => null,
    }),
    document: { documentElement: { classList: { contains: () => false } } },
    window: { addEventListener() {}, removeEventListener() {} },
    devicePixelRatio: 1,
    performance: { now: () => 0 },
    requestAnimationFrame: raf.request,
    cancelAnimationFrame: raf.cancel,
  };
  const source = readFileSync(
    new URL('../theme/components/SnowCanvas/index.tsx', import.meta.url),
    'utf8',
  );
  runInNewContext(
    transpileModule(source, {
      compilerOptions: { module: ModuleKind.CommonJS, jsx: JsxEmit.ReactJSX },
    }).outputText,
    runtime,
  );
  exports.SnowCanvas();
  stats.layoutReads = 0;
  stats.bitmapWrites = 0;
  return {
    raf,
    stats,
    canvas,
    rect,
    runtime,
    dispose: () => cleanup(),
  };
}

describe('homepage animation frame budget', () => {
  it('measures each snow collision surface once per frame and keeps its bitmap', () => {
    const scene = snowScene();
    for (let i = 1; i <= 30; i++) scene.raf.tick(i * 16.67);
    assert.ok(scene.stats.layoutReads <= 4 * 30, scene.stats.layoutReads);
    assert.equal(scene.stats.bitmapWrites, 0);
    assert.equal(scene.stats.clears, 30);
    assert.equal(scene.raf.pending, 1);
    scene.dispose();
    assert.equal(scene.raf.pending, 0);
  });

  it('updates the snow bitmap when its container or pixel ratio changes', () => {
    const scene = snowScene();
    scene.rect.width = 1200;
    scene.rect.height = 900;
    scene.raf.tick(16.67);
    assert.equal(scene.canvas.width, 1200);
    assert.equal(scene.canvas.height, 900);
    scene.runtime.devicePixelRatio = 2;
    scene.raf.tick(33.34);
    assert.equal(scene.canvas.width, 2400);
    assert.equal(scene.canvas.height, 1800);
    scene.dispose();
  });

  it('reuses particle upload buffers on steady frames', () => {
    const scene = snowScene();
    scene.raf.tick(16.67);
    scene.raf.tick(33.34);
    assert.equal(scene.stats.uploads.length, 4);
    assert.ok(ArrayBuffer.isView(scene.stats.uploads[0]));
    assert.ok(ArrayBuffer.isView(scene.stats.uploads[1]));
    assert.equal(scene.stats.uploads[0], scene.stats.uploads[2]);
    assert.equal(scene.stats.uploads[1], scene.stats.uploads[3]);
    scene.dispose();
  });
});

function overlayScene() {
  const raf = frames();
  const stats = { layoutReads: 0, paints: 0, borders: [], text: [] };
  const ctx = {
    setTransform() {},
    clearRect() {
      stats.paints++;
    },
    fillRect(...rect) {
      if (this.fillStyle === '#4096ff') stats.borders.push(rect);
    },
    measureText: (text) => ({ width: text.length * 8 }),
    beginPath() {},
    roundRect() {},
    fill() {},
    fillText(text) {
      stats.text.push(text);
    },
  };
  const box = { left: 100, top: 200, width: 686, height: 445 };
  const win = {
    getBoundingClientRect() {
      stats.layoutReads++;
      return box;
    },
    get offsetWidth() {
      stats.layoutReads++;
      return 1372;
    },
    get offsetHeight() {
      stats.layoutReads++;
      return 890;
    },
  };
  const exports = {};
  const runtime = {
    exports,
    requestAnimationFrame: raf.request,
    cancelAnimationFrame: raf.cancel,
    performance: { now: () => 0 },
    window: { devicePixelRatio: 2 },
    getComputedStyle: () => ({ fontFamily: 'sans-serif' }),
  };
  runInNewContext(overlayCode, runtime);
  const canvas = { width: 0, height: 0, getContext: () => ctx };
  const overlay = new exports.PreviewSelectionOverlay(canvas, win);
  overlay.render();
  return {
    overlay,
    raf,
    stats,
    canvas,
    box,
    runtime,
    duration: exports.SELECTION_TRANSITION_MS,
  };
}

const first = { x: 50, y: 60, width: 300, height: 90 };
const second = { x: 100, y: 260, width: 600, height: 120 };

describe('preview selection rendering', () => {
  it('animates without reading DOM layout on every frame', () => {
    const scene = overlayScene();
    scene.overlay.moveTo(first);
    scene.raf.tick(0);
    scene.overlay.moveTo(second);
    const reads = scene.stats.layoutReads;
    scene.raf.tick(scene.duration / 2);
    assert.equal(scene.stats.borders.at(-4)[0], 87);
    assert.equal(scene.stats.borders.at(-4)[1], 209);
    scene.raf.tick(scene.duration);
    assert.equal(scene.stats.layoutReads, reads);
    assert.deepEqual(scene.stats.borders.at(-4), [99, 259, 603, 3]);
    assert.equal(scene.raf.pending, 0);
  });

  it('paints only the latest selection in a burst of reduced-motion updates', () => {
    const scene = overlayScene();
    scene.overlay.setReducedMotion(true);
    scene.raf.tick(0);
    const paints = scene.stats.paints;
    scene.overlay.moveTo(first);
    scene.overlay.moveTo(second);
    scene.overlay.moveTo({ ...second, x: 200 });
    scene.raf.tick(16.67);
    assert.equal(scene.stats.paints - paints, 1);
    assert.deepEqual(scene.stats.borders.at(-4), [199, 259, 603, 3]);
    assert.equal(scene.raf.pending, 0);
  });

  it('measures only the latest pointer target once per frame', () => {
    const scene = overlayScene();
    const targetReads = [0, 0];
    const targets = [first, second].map((selection, index) => ({
      getBoundingClientRect() {
        targetReads[index]++;
        return {
          left: scene.box.left + selection.x / 2,
          top: scene.box.top + selection.y / 2,
          width: selection.width / 2,
          height: selection.height / 2,
        };
      },
    }));
    const reads = scene.stats.layoutReads;
    for (let i = 0; i < 20; i++) scene.overlay.moveToTarget(targets[i % 2]);
    assert.deepEqual(targetReads, [0, 0]);
    scene.raf.tick(16.67);
    assert.deepEqual(targetReads, [0, 1]);
    assert.equal(scene.stats.layoutReads - reads, 1);
    assert.deepEqual(scene.stats.borders.at(-4), [99, 259, 603, 3]);
    assert.equal(scene.raf.pending, 0);
    scene.overlay.moveToTarget(targets[1]);
    assert.equal(scene.raf.pending, 0);
    scene.overlay.refreshTarget();
    scene.raf.tick(33.34);
    assert.deepEqual(targetReads, [0, 2]);
  });

  it('refreshes the backing bitmap and border after resize and DPR changes', () => {
    const scene = overlayScene();
    scene.overlay.moveTo(first);
    scene.raf.tick(0);
    scene.box.width = 343;
    scene.box.height = 222.5;
    scene.overlay.resize();
    scene.raf.tick(16.67);
    assert.equal(scene.canvas.width, 686);
    assert.equal(scene.canvas.height, 445);
    assert.deepEqual(scene.stats.borders.at(-4), [24, 29, 152, 2]);
    scene.runtime.window.devicePixelRatio = 4;
    scene.overlay.moveTo(second);
    scene.raf.tick(scene.duration);
    assert.equal(scene.canvas.width, 1372);
    assert.equal(scene.canvas.height, 890);
    assert.deepEqual(scene.stats.borders.at(-4), [99, 259, 603, 3]);
    assert.equal(scene.raf.pending, 0);
  });

  it('snaps a running transition when reduced motion is enabled', () => {
    const scene = overlayScene();
    scene.overlay.moveTo(first);
    scene.raf.tick(0);
    scene.overlay.moveTo(second);
    scene.raf.tick(scene.duration / 2);
    scene.overlay.setUnit('dp');
    scene.overlay.setReducedMotion(true);
    scene.raf.tick(scene.duration / 2 + 1);
    assert.deepEqual(scene.stats.borders.at(-4), [99, 259, 603, 3]);
    assert.deepEqual(scene.stats.text.slice(-4), ['400', 'x', '80', 'dp']);
    assert.equal(scene.raf.pending, 0);
  });

  it('clears and cancels a pending target on pointer leave or disposal', () => {
    const scene = overlayScene();
    const target = {
      getBoundingClientRect: () => assert.fail('dismissed target'),
    };
    scene.overlay.moveToTarget(target);
    scene.overlay.dismiss();
    const paints = scene.stats.paints;
    scene.raf.tick(16.67);
    assert.equal(scene.raf.pending, 0);
    assert.equal(scene.stats.paints, paints);
    scene.overlay.moveTo(first);
    scene.raf.tick(33.34);
    assert.deepEqual(scene.stats.borders.at(-4), [49, 59, 303, 3]);
    scene.overlay.moveToTarget(target);
    scene.overlay.dispose();
    scene.raf.tick(50);
    assert.equal(scene.raf.pending, 0);
  });

  it('stops scheduling frames while the preview has no layout size', () => {
    const scene = overlayScene();
    scene.box.width = 0;
    scene.overlay.resize();
    scene.overlay.moveToTarget({
      getBoundingClientRect: () => assert.fail('hidden target'),
    });
    scene.raf.tick(16.67);
    assert.equal(scene.raf.pending, 0);
  });
});
