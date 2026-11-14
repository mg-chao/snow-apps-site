import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { it } from 'node:test';
import { setImmediate } from 'node:timers/promises';
import { runInNewContext } from 'node:vm';
import React from 'react';
import Reconciler from 'react-reconciler';
import { JsxEmit, ModuleKind, transpileModule } from 'typescript';

// Render the real components and hooks without adding a DOM implementation.
// Only the browser boundaries (media, intersection, timer and clipboard) are fake.
const require = createRequire(import.meta.url);
const source = readFileSync(
  new URL('../theme/components/FeatureShowcase/shared.tsx', import.meta.url),
  'utf8',
);
const compiled = transpileModule(source, {
  compilerOptions: { module: ModuleKind.CommonJS, jsx: JsxEmit.ReactJSX },
}).outputText;
const context = {};
let priority = 2;
const append = (parent, child) => parent.children.push(child);
const remove = (parent, child) =>
  parent.children.splice(parent.children.indexOf(child), 1);
const renderer = Reconciler({
  rendererVersion: '1',
  rendererPackageName: 'snow-demo-tests',
  supportsMutation: true,
  supportsPersistence: false,
  supportsHydration: false,
  isPrimaryRenderer: true,
  supportsMicrotasks: true,
  scheduleMicrotask: queueMicrotask,
  scheduleTimeout: setTimeout,
  cancelTimeout: clearTimeout,
  noTimeout: -1,
  getPublicInstance: (instance) => instance,
  getRootHostContext: () => context,
  getChildHostContext: () => context,
  prepareForCommit: () => null,
  resetAfterCommit: () => {},
  createInstance: (type, props) => ({ type, props, children: [] }),
  createTextInstance: (text) => ({ text }),
  appendInitialChild: append,
  appendChild: append,
  appendChildToContainer: append,
  removeChild: remove,
  removeChildFromContainer: remove,
  insertBefore: (parent, child, before) =>
    parent.children.splice(parent.children.indexOf(before), 0, child),
  insertInContainerBefore: (parent, child, before) =>
    parent.children.splice(parent.children.indexOf(before), 0, child),
  finalizeInitialChildren: () => false,
  shouldSetTextContent: () => false,
  commitUpdate: (instance, _type, _old, props) => {
    instance.props = props;
  },
  commitTextUpdate: (instance, _old, text) => {
    instance.text = text;
  },
  resetTextContent: (instance) => {
    instance.children = [];
  },
  clearContainer: (container) => {
    container.children = [];
  },
  getCurrentUpdatePriority: () => priority,
  setCurrentUpdatePriority: (value) => {
    priority = value;
  },
  resolveUpdatePriority: () => priority || 2,
  trackSchedulerEvent: () => {},
  resolveEventType: () => null,
  resolveEventTimeStamp: () => -1.1,
  shouldAttemptEagerTransition: () => false,
  maySuspendCommit: () => false,
  maySuspendCommitOnUpdate: () => false,
  maySuspendCommitInSyncRender: () => false,
  preloadInstance: () => true,
  startSuspendingCommit: () => {},
  suspendInstance: () => {},
  waitForCommitToBeReady: () => null,
  detachDeletedInstance: () => {},
  NotPendingTransition: null,
});

function flush(action = () => {}) {
  renderer.flushSyncFromReconciler(action);
  renderer.flushPassiveEffects();
  renderer.flushSyncWork();
}

function runtime({ reduced = false, writeText = async () => {} } = {}) {
  let now = 0;
  let timerId = 0;
  const timers = new Map();
  const observers = [];
  const media = Object.assign(new EventTarget(), { matches: reduced });
  const window = Object.assign(new EventTarget(), {
    matchMedia: () => media,
    setInterval: (callback) => {
      timers.set(++timerId, callback);
      return timerId;
    },
    clearInterval: (id) => timers.delete(id),
    innerHeight: 700,
  });
  const document = Object.assign(new EventTarget(), { hidden: false });
  class IntersectionObserver {
    constructor(callback) {
      this.callback = callback;
      observers.push(this);
    }
    observe(target) {
      this.target = target;
    }
    disconnect() {}
    emit(ratio = 1, height = 500) {
      this.callback([
        {
          target: this.target,
          isIntersecting: ratio > 0,
          intersectionRatio: ratio,
          boundingClientRect: { height },
          intersectionRect: { height: ratio * height },
          rootBounds: { height: 700 },
        },
      ]);
    }
  }
  const exports = {};
  runInNewContext(compiled, {
    exports,
    window,
    document,
    IntersectionObserver,
    CustomEvent,
    performance: { now: () => now },
    navigator: { clipboard: { writeText } },
    require: (name) =>
      name.includes('/icons')
        ? { ReloadIcon: () => null, ScreenshotCopyIcon: () => null }
        : require(name),
  });
  const container = { children: [] };
  const fail = (error) => {
    throw error;
  };
  const root = renderer.createContainer(
    container,
    1,
    null,
    false,
    null,
    '',
    fail,
    fail,
    fail,
    null,
  );
  const render = (element) =>
    flush(() => renderer.updateContainerSync(element, root, null, null));
  return {
    api: exports,
    container,
    render,
    observers,
    timers,
    tick(ms) {
      now += ms;
      flush(() => {
        for (const callback of [...timers.values()]) callback();
      });
    },
    setReduced(value) {
      media.matches = value;
      flush(() => media.dispatchEvent(new Event('change')));
    },
    setHidden(value) {
      document.hidden = value;
      flush(() => document.dispatchEvent(new Event('visibilitychange')));
    },
    close() {
      render(null);
    },
  };
}

function text(node) {
  return node.text ?? node.children?.map(text).join('') ?? '';
}
function find(node, type) {
  return node.type === type
    ? node
    : node.children?.map((child) => find(child, type)).find(Boolean);
}
function hook(runtime) {
  let demo;
  function Probe() {
    demo = runtime.api.useDemo({ duration: 8000 });
    return React.createElement('div', { ref: demo.containerRef });
  }
  runtime.render(React.createElement(Probe));
  return () => demo;
}

it('the sample note renders in both languages and is excluded from search snippets', () => {
  const env = runtime();
  try {
    env.render(React.createElement(env.api.SampleNote, { isZh: true }));
    assert.equal(find(env.container, 'div').props['data-nosnippet'], '');
    assert.match(text(env.container), /发布检查清单/);

    env.render(
      React.createElement(env.api.SampleNote, { isZh: false, compact: true }),
    );
    assert.equal(find(env.container, 'div').props['data-nosnippet'], '');
    assert.match(text(env.container), /RELEASE CHECKLIST/);
  } finally {
    env.close();
  }
});

it('reduced motion suppresses autoplay but explicit replay presents the complete result', () => {
  const env = runtime({ reduced: true });
  try {
    const demo = hook(env);
    flush(() => env.observers[0].emit());
    assert.equal(demo().playing, false);
    assert.equal(demo().progress, 0);
    flush(() => demo().play());
    assert.equal(demo().progress, 1);
    assert.equal(demo().playing, false);
    assert.equal(env.timers.size, 0);
    flush(() => demo().reset());
    assert.equal(demo().progress, 0);
    flush(() => demo().play());
    assert.equal(demo().progress, 1);
  } finally {
    env.close();
  }
});

it('pausing freezes the workflow clock and hiding the page stops playback', () => {
  const env = runtime();
  try {
    const demo = hook(env);
    flush(() => env.observers[0].emit());
    env.tick(2000);
    assert.equal(demo().progress, 0.25);
    flush(() => demo().pause());
    env.tick(2000);
    assert.equal(demo().progress, 0.25);
    flush(() => demo().resume());
    env.tick(1000);
    assert.equal(demo().progress, 0.375);
    env.setHidden(true);
    assert.equal(demo().playing, false);
    env.tick(1000);
    assert.equal(demo().progress, 0.375);
  } finally {
    env.close();
  }
});

it('switching reduced motion on during playback stops the active clock', () => {
  const env = runtime();
  try {
    const demo = hook(env);
    flush(() => demo().play());
    env.tick(1000);
    env.setReduced(true);
    assert.equal(demo().playing, false);
    assert.equal(demo().reducedMotion, true);
    assert.equal(env.timers.size, 0);
    flush(() => demo().play());
    assert.equal(demo().progress, 1);
  } finally {
    env.close();
  }
});

it('a tall mobile demo starts within the viewport and remains active while partly visible', () => {
  const env = runtime();
  try {
    const demo = hook(env);
    flush(() => env.observers[0].emit(0.4, 1000));
    assert.equal(demo().visible, true);
    assert.equal(demo().playing, true);
    env.tick(1000);
    flush(() => env.observers[0].emit(0.1, 1000));
    env.tick(1000);
    assert.equal(demo().progress, 0.25);
    flush(() => env.observers[0].emit(0, 1000));
    assert.equal(demo().visible, false);
    assert.equal(demo().playing, false);
  } finally {
    env.close();
  }
});

it('manual interaction cancels autoplay without clearing progress or replaying on re-entry', () => {
  const env = runtime();
  try {
    const demo = hook(env);
    flush(() => env.observers[0].emit());
    env.tick(2000);
    flush(() => demo().interact());
    env.tick(2000);
    assert.equal(demo().progress, 0.25);
    assert.equal(demo().playing, false);
    flush(() => env.observers[0].emit(0));
    flush(() => env.observers[0].emit());
    assert.equal(demo().progress, 0.25);
    assert.equal(demo().playing, false);
  } finally {
    env.close();
  }
});

it('autoplay clocks are exclusive and interacting with another demo cancels the active one', () => {
  const env = runtime();
  let first;
  let second;
  function Pair() {
    first = env.api.useDemo({ duration: 8000 });
    second = env.api.useDemo({ duration: 8000 });
    return React.createElement(
      'div',
      null,
      React.createElement('div', { ref: first.containerRef }),
      React.createElement('div', { ref: second.containerRef }),
    );
  }
  try {
    env.render(React.createElement(Pair));
    flush(() => env.observers[0].emit());
    assert.equal(first.playing, true);
    flush(() => env.observers[1].emit());
    assert.equal(first.playing, false);
    assert.equal(second.playing, true);
    flush(() => first.interact());
    assert.equal(second.playing, false);
  } finally {
    env.close();
  }
});

it('the capture handler lets Playback pause its clock without immediately resuming it', () => {
  const env = runtime();
  let demo;
  function Probe() {
    demo = env.api.useDemo({ duration: 8000 });
    return React.createElement(
      'div',
      { ref: demo.containerRef, onPointerDownCapture: demo.interact },
      React.createElement(env.api.Playback, { demo, isZh: false }),
    );
  }
  try {
    env.render(React.createElement(Probe));
    flush(() => demo.play());
    env.tick(1000);
    flush(() =>
      find(env.container, 'div').props.onPointerDownCapture({
        target: { closest: () => ({}) },
      }),
    );
    assert.equal(demo.playing, true);
    const playback = find(env.container, 'div').children[0];
    flush(() =>
      playback.children
        .find((child) => text(child) === 'Pause demo')
        .props.onClick(),
    );
    assert.equal(demo.playing, false);
    env.tick(1000);
    assert.equal(demo.progress, 0.125);
  } finally {
    env.close();
  }
});

it('clipboard rejection shows failure and never claims success', async () => {
  const env = runtime({
    writeText: async () => {
      throw new Error('Permission denied');
    },
  });
  try {
    env.render(
      React.createElement(env.api.CopyButton, {
        value: 'sample result',
        isZh: false,
      }),
    );
    await find(env.container, 'button').props.onClick();
    flush();
    assert.match(text(env.container), /Copy failed/);
    assert.doesNotMatch(text(env.container), /Copied|Result copied/);
  } finally {
    env.close();
  }
});

it('a late clipboard response cannot mark a different document result as copied', async () => {
  let finish;
  const writes = [];
  const env = runtime({
    writeText: (value) => {
      writes.push(value);
      return new Promise((resolve) => {
        finish = resolve;
      });
    },
  });
  try {
    env.render(
      React.createElement(env.api.CopyButton, {
        value: 'old table',
        isZh: false,
      }),
    );
    let pending;
    flush(() => {
      pending = find(env.container, 'button').props.onClick();
    });
    assert.match(text(env.container), /Copying/);
    env.render(
      React.createElement(env.api.CopyButton, {
        value: 'new formula',
        isZh: false,
      }),
    );
    await setImmediate();
    flush();
    finish();
    await pending;
    flush();
    assert.deepEqual(writes, ['old table']);
    assert.doesNotMatch(text(env.container), /Copied|Result copied/);
    assert.match(text(env.container), /Copy result/);
  } finally {
    env.close();
  }
});

it('clipboard success is reported only after the exact displayed result is written', async () => {
  const writes = [];
  const env = runtime({
    writeText: async (value) => {
      writes.push(value);
    },
  });
  try {
    env.render(
      React.createElement(env.api.CopyButton, {
        value: '标题\n- 项目一',
        isZh: true,
      }),
    );
    await find(env.container, 'button').props.onClick();
    flush();
    assert.deepEqual(writes, ['标题\n- 项目一']);
    assert.match(text(env.container), /已复制/);
    env.render(
      React.createElement(env.api.CopyButton, {
        value: '标题\n- 项目一',
        isZh: true,
        disabled: true,
      }),
    );
    await setImmediate();
    flush();
    assert.doesNotMatch(text(env.container), /已复制/);
  } finally {
    env.close();
  }
});
