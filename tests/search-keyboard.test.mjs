import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';
import { it } from 'node:test';
import { runInNewContext } from 'node:vm';
import { RenderType } from '@rspress/core/dist/theme/components/Search/logic/types.js';
import { ModuleKind, transpileModule } from 'typescript';

const require = createRequire(import.meta.url);
const installedSource = require.resolve(
  '@rspress/core/dist/theme/components/Search/SearchPanel.js',
);
// Normal runs exercise the installed dependency. An explicit source override is
// useful for checking that these behavioral tests reject an unpatched release.
const sourcePath = process.env.SNOW_SEARCH_PANEL_TEST_SOURCE
  ? resolve(process.env.SNOW_SEARCH_PANEL_TEST_SOURCE)
  : installedSource;
const compiled = transpileModule(readFileSync(sourcePath, 'utf8'), {
  compilerOptions: { module: ModuleKind.CommonJS },
}).outputText;

function panel({ focused = false, suggestions = [], index = 0 } = {}) {
  const handlers = new Map();
  const navigations = [];
  const focusChanges = [];
  const resultTabChanges = [];
  const indexChanges = [];
  const cleanups = [];
  const element = (type, props) => ({ type, props });
  const searchState = {
    currentRenderType: RenderType.Default,
    currentSuggestions: suggestions,
    currentSuggestionIndex: index,
    clearQuery() {},
    handleQueryInput() {},
    initStatus: 'inited',
    isSearching: false,
    query: '',
    resultTabIndex: 0,
    searchError: undefined,
    searchIndexURL: undefined,
    searchResult: [
      { group: 'Guides', renderType: RenderType.Default, result: suggestions },
    ],
    searchEnabled: true,
    setCurrentSuggestionIndex: (value) => indexChanges.push(value),
    setResultTabIndex: (value) => resultTabChanges.push(value),
  };
  const mocks = {
    'react/jsx-runtime': { Fragment: 'Fragment', jsx: element, jsxs: element },
    '@rspress/core/runtime': { Head: 'Head', useI18n: () => (key) => key },
    '@rspress/core/theme': {
      IconClose: 'IconClose',
      IconSearch: 'IconSearch',
      SvgWrapper: 'SvgWrapper',
      Tab: 'Tab',
      Tabs: 'Tabs',
      useLinkNavigate: () => (href) => navigations.push(href),
    },
    react: {
      useEffect(setup) {
        cleanups.push(setup());
      },
      useRef: (current) => ({ current }),
      useState: (initial) => [initial, () => {}],
    },
    'react-dom': { createPortal: (children) => children },
    'virtual-search-hooks': {},
    './logic/types.js': { RenderType },
    './NoSearchResult.js': { NoSearchResult: 'NoSearchResult' },
    './SuggestItem.js': { SuggestItem: 'SuggestItem' },
    './useSearchPanel.js': { useSearchPanel: () => searchState },
  };
  const module = { exports: {} };
  runInNewContext(
    compiled,
    {
      module,
      exports: module.exports,
      require(id) {
        if (id.endsWith('.css')) return {};
        assert.ok(Object.hasOwn(mocks, id), `Unexpected dependency: ${id}`);
        return mocks[id];
      },
      document: {
        getElementById: () => ({}),
        addEventListener(type, callback) {
          assert.equal(type, 'keydown');
          handlers.set(type, callback);
        },
        removeEventListener(type, callback) {
          if (handlers.get(type) === callback) handlers.delete(type);
        },
      },
    },
    { filename: sourcePath },
  );
  module.exports.SearchPanel({
    focused,
    setFocused: (value) => focusChanges.push(value),
  });
  assert.equal(typeof handlers.get('keydown'), 'function');

  return {
    navigations,
    focusChanges,
    resultTabChanges,
    indexChanges,
    press(code, options = {}) {
      let prevented = false;
      const event = {
        code,
        isComposing: false,
        ctrlKey: false,
        metaKey: false,
        preventDefault() {
          prevented = true;
        },
        ...options,
      };
      handlers.get('keydown')(event);
      return { prevented };
    },
    dispose() {
      for (const cleanup of cleanups) cleanup?.();
      assert.equal(handlers.size, 0);
    },
  };
}

function untouched(runtime) {
  assert.deepEqual(runtime.navigations, []);
  assert.deepEqual(runtime.focusChanges, []);
  assert.deepEqual(runtime.resultTabChanges, []);
  assert.deepEqual(runtime.indexChanges, []);
}

it('closed search ignores Enter with no suggestions and preserves native activation', () => {
  const runtime = panel();
  assert.deepEqual(runtime.press('Enter'), { prevented: false });
  untouched(runtime);
  runtime.dispose();
});

it('closed search ignores Enter even when stale suggestions remain', () => {
  const runtime = panel({
    suggestions: [{ title: 'Previous search', link: '/guides/old.html' }],
  });
  assert.deepEqual(runtime.press('Enter'), { prevented: false });
  untouched(runtime);
  runtime.dispose();
});

it('open search ignores Enter when no result exists', () => {
  const runtime = panel({ focused: true });
  assert.doesNotThrow(() => runtime.press('Enter'));
  untouched(runtime);
  runtime.dispose();
});

it('open search ignores Enter after its selected result becomes out of range', () => {
  const runtime = panel({
    focused: true,
    suggestions: [{ title: 'One remaining result', link: '/guides/one.html' }],
    index: 2,
  });
  assert.doesNotThrow(() => runtime.press('Enter'));
  untouched(runtime);
  runtime.dispose();
});

it('open search navigates to the selected displayed result and closes', () => {
  const runtime = panel({
    focused: true,
    suggestions: [
      { title: 'First group', link: '/guides/first.html' },
      { title: 'Second group', link: '/guides/second.html' },
      { title: 'First group', link: '/guides/third.html#steps' },
    ],
    index: 1,
  });
  runtime.press('Enter');
  assert.deepEqual(runtime.navigations, ['/guides/third.html#steps']);
  assert.deepEqual(runtime.focusChanges, [false]);
  assert.deepEqual(runtime.resultTabChanges, [0]);
  assert.deepEqual(runtime.indexChanges, [0]);
  runtime.dispose();
});

it('IME composition does not submit an otherwise valid search result', () => {
  const runtime = panel({
    focused: true,
    suggestions: [{ title: 'Result', link: '/guides/result.html' }],
  });
  runtime.press('Enter', { isComposing: true });
  untouched(runtime);
  runtime.dispose();
});

it('Command+K and Control+K still open search from the document', () => {
  for (const modifier of ['metaKey', 'ctrlKey']) {
    const runtime = panel();
    assert.deepEqual(runtime.press('KeyK', { [modifier]: true }), {
      prevented: true,
    });
    assert.deepEqual(runtime.focusChanges, [true]);
    assert.deepEqual(runtime.navigations, []);
    runtime.dispose();
  }
});
