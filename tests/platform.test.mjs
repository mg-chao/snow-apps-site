import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { describe, it } from 'node:test';
import { setImmediate } from 'node:timers/promises';
import { runInNewContext } from 'node:vm';
import { ModuleKind, transpileModule } from 'typescript';

const source = readFileSync(
  new URL('../theme/platform.ts', import.meta.url),
  'utf8',
);
const compiled = transpileModule(source, {
  compilerOptions: { module: ModuleKind.CommonJS },
}).outputText;

function platformRuntime({ navigator, search = '', server = false } = {}) {
  const stores = [];
  const exports = {};
  runInNewContext(compiled, {
    exports,
    URLSearchParams,
    ...(navigator ? { navigator: { maxTouchPoints: 0, ...navigator } } : {}),
    ...(!server ? { window: { location: { search } } } : {}),
    require: () => ({
      useSyncExternalStore(subscribe, snapshot, serverSnapshot) {
        stores.push({ subscribe, snapshot, serverSnapshot });
        return server ? serverSnapshot() : snapshot();
      },
    }),
  });
  return { api: exports, stores };
}

const windows = {
  platform: 'Win32',
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/142.0.0.0',
};
const macos = {
  platform: 'MacIntel',
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15',
};

describe('download platform and CPU detection', () => {
  it('uses deterministic Windows defaults during server rendering', () => {
    const { api } = platformRuntime({ server: true });
    assert.equal(api.detectDownloadPlatform(), 'windows');
    assert.equal(api.detectDownloadArchitecture(), null);
    assert.equal(api.useResolvedDownloadTarget().platform, 'windows');
    assert.equal(api.useResolvedDownloadTarget().architecture, null);
  });

  it('recognizes explicit Windows ARM64 and existing x64 user agents', () => {
    for (const token of ['ARM64', 'aarch64']) {
      const { api } = platformRuntime({
        navigator: { ...windows, userAgent: `Windows NT 10.0; ${token}` },
      });
      assert.equal(api.detectDownloadPlatform(), 'windows');
      assert.equal(api.detectDownloadArchitecture(), 'arm64');
    }
    assert.equal(
      platformRuntime({ navigator: windows }).api.detectDownloadArchitecture(),
      'x64',
    );
  });

  it('does not infer Intel from the MacIntel platform or Intel Mac OS X user agent', () => {
    const { api } = platformRuntime({ navigator: macos });
    assert.equal(api.detectDownloadPlatform(), 'macos');
    assert.equal(api.detectDownloadArchitecture(), null);
  });

  it('recognizes an explicit ARM64 Mac without client hints', () => {
    const { api } = platformRuntime({
      navigator: {
        ...macos,
        platform: 'MacARM64',
        userAgent: 'Macintosh; arm64',
      },
    });
    assert.equal(api.detectDownloadPlatform(), 'macos');
    assert.equal(api.detectDownloadArchitecture(), 'arm64');
  });

  for (const [name, navigator] of [
    [
      'iPhone',
      { platform: 'iPhone', userAgent: 'iPhone OS 18_0 like Mac OS X; ARM64' },
    ],
    ['iPad in desktop mode', { ...macos, maxTouchPoints: 5 }],
    ['Android', { platform: 'Linux aarch64', userAgent: 'Android 16; ARM64' }],
    ['Linux', { platform: 'Linux x86_64', userAgent: 'Linux x86_64' }],
  ]) {
    it(`does not detect a supported desktop CPU for ${name}`, () => {
      const { api } = platformRuntime({ navigator });
      assert.equal(api.detectDownloadPlatform(), 'windows');
      assert.equal(api.detectDownloadArchitecture(), null);
    });
  }

  for (const [name, navigator, hints, expected] of [
    [
      'Windows ARM64 with a reduced x64 user agent',
      windows,
      { architecture: 'arm', bitness: '64' },
      'arm64',
    ],
    ['Windows x64', windows, { architecture: 'x86', bitness: '64' }, 'x64'],
    [
      'Apple silicon with an Intel user agent',
      macos,
      { architecture: 'arm', bitness: '64' },
      'arm64',
    ],
    ['Intel Mac', macos, { architecture: 'x86', bitness: '64' }, 'x64'],
  ]) {
    it(`updates subscribers using native CPU hints for ${name}`, async () => {
      let requests = 0;
      const { api, stores } = platformRuntime({
        navigator: {
          ...navigator,
          userAgentData: {
            platform: name.startsWith('Windows') ? 'Windows' : 'macOS',
            async getHighEntropyValues(requested) {
              requests++;
              assert.deepEqual(Array.from(requested), [
                'architecture',
                'bitness',
              ]);
              return hints;
            },
          },
        },
      });
      api.useDownloadTarget();
      let changes = 0;
      const store = stores.at(-1);
      const unsubscribe = store.subscribe(() => {
        changes++;
      });
      await setImmediate();
      assert.equal(store.snapshot(), expected);
      assert.equal(changes, 1);
      const unsubscribeAgain = store.subscribe(() => {
        changes++;
      });
      assert.equal(requests, 1);
      unsubscribe();
      unsubscribeAgain();
    });
  }

  for (const [name, getHighEntropyValues] of [
    [
      'denied hints',
      async () => {
        throw new Error('NotAllowedError');
      },
    ],
    ['omitted hints', async () => ({})],
    [
      'unknown architecture',
      async () => ({ architecture: 'unknown', bitness: '64' }),
    ],
    ['32-bit hints', async () => ({ architecture: 'arm', bitness: '32' })],
  ]) {
    it(`keeps manual selection available with ${name}`, async () => {
      const { api, stores } = platformRuntime({
        navigator: {
          ...macos,
          userAgentData: { getHighEntropyValues },
        },
      });
      api.useDownloadTarget();
      const store = stores.at(-1);
      let changes = 0;
      const unsubscribe = store.subscribe(() => {
        changes++;
      });
      await setImmediate();
      assert.equal(store.snapshot(), null);
      assert.equal(changes, 0);
      unsubscribe();
    });
  }
});

describe('download navigation and explicit choices', () => {
  it('accepts both architectures and OS values, rejecting unsupported values', () => {
    for (const os of ['windows', 'macos']) {
      for (const arch of ['x64', 'arm64']) {
        const { api } = platformRuntime({
          navigator: windows,
          search: `?os=${os}&arch=${arch}`,
        });
        // biome-ignore lint/correctness/useHookAtTopLevel: This VM uses a mocked external store to exercise each URL.
        const target = api.useResolvedDownloadTarget();
        assert.equal(target.platform, os);
        assert.equal(target.architecture, arch);
      }
    }
    const { api } = platformRuntime({
      navigator: windows,
      search: '?os=linux&arch=arm32',
    });
    assert.equal(api.readPlatformQuery(), null);
    assert.equal(api.readArchitectureQuery(), null);
    assert.equal(api.useResolvedDownloadTarget().platform, 'windows');
    assert.equal(api.useResolvedDownloadTarget().architecture, 'x64');
  });

  it('keeps legacy OS-only URLs and does not reuse a CPU from another OS', () => {
    const { api } = platformRuntime({
      navigator: windows,
      search: '?os=macos',
    });
    assert.equal(api.useResolvedDownloadTarget().platform, 'macos');
    assert.equal(api.useResolvedDownloadTarget().architecture, null);
  });

  it('prioritizes explicit URL choices over asynchronous detection', async () => {
    const { api, stores } = platformRuntime({
      navigator: {
        ...windows,
        userAgentData: {
          getHighEntropyValues: async () => ({
            architecture: 'arm',
            bitness: '64',
          }),
        },
      },
      search: '?os=macos&arch=x64',
    });
    api.useResolvedDownloadTarget();
    const unsubscribe = stores.at(-1).subscribe(() => {});
    await setImmediate();
    assert.equal(api.detectDownloadArchitecture(), 'arm64');
    assert.equal(api.useResolvedDownloadTarget().platform, 'macos');
    assert.equal(api.useResolvedDownloadTarget().architecture, 'x64');
    unsubscribe();
  });

  it('carries detected architectures from either homepage without guessing an unknown CPU', () => {
    const { api } = platformRuntime();
    for (const locale of ['en', 'zh']) {
      for (const platform of ['windows', 'macos']) {
        for (const architecture of ['x64', 'arm64', null]) {
          const url = new URL(
            api.downloadPageUrl(locale, { platform, architecture }),
            'https://snowshot.top',
          );
          assert.equal(
            url.pathname,
            locale === 'zh' ? '/zh/download' : '/download',
          );
          assert.equal(url.searchParams.get('os'), platform);
          assert.equal(url.searchParams.get('arch'), architecture);
        }
      }
    }
  });
});
