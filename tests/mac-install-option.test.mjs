import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { it } from 'node:test';
import {
  macosInstallCommand,
  releaseDownloadUrl,
} from '../theme/components/DownloadPage/releaseLinks.ts';

// These tests execute macOS Terminal commands with the system Bash.
const bashTest = process.platform === 'win32' ? it.skip : it;

for (const locale of ['en', 'zh']) {
  const language = locale === 'zh' ? 'zh-CN' : 'en';
  for (const edition of ['full', 'mini']) {
    bashTest(
      `the ${locale} command downloads and executes the ${edition} installer`,
      () => {
        const root = mkdtempSync(join(tmpdir(), 'snow-site-installer-'));
        try {
          writeFileSync(
            join(root, 'curl'),
            '#!/bin/bash\nprintf "%s\\n" "$@" > curl-args\ncp downloaded.sh install-snow-shot-macos.sh\n',
            { mode: 0o755 },
          );
          writeFileSync(join(root, 'downloaded.sh'), 'printf "%s\\n" "$@"\n');
          const result = spawnSync(
            '/bin/bash',
            ['-c', macosInstallCommand(locale, edition)],
            {
              cwd: root,
              env: { ...process.env, PATH: `${root}:/usr/bin:/bin` },
              encoding: 'utf8',
            },
          );
          assert.equal(result.status, 0, result.stderr);
          assert.equal(
            result.stdout,
            `--edition\n${edition}\n--lang\n${language}\n`,
          );
          assert.equal(
            readFileSync(join(root, 'curl-args'), 'utf8')
              .trim()
              .split('\n')
              .at(-1),
            releaseDownloadUrl(locale, 'macosInstallScript'),
          );
        } finally {
          rmSync(root, { recursive: true, force: true });
        }
      },
    );
  }

  bashTest(
    `a failed ${locale} download never executes a previously downloaded installer`,
    () => {
      const root = mkdtempSync(join(tmpdir(), 'snow-site-installer-'));
      try {
        writeFileSync(join(root, 'curl'), '#!/bin/bash\nexit 22\n', {
          mode: 0o755,
        });
        writeFileSync(
          join(root, 'install-snow-shot-macos.sh'),
          'touch executed\n',
        );
        const result = spawnSync(
          '/bin/bash',
          ['-c', macosInstallCommand(locale, 'full')],
          {
            cwd: root,
            env: { ...process.env, PATH: `${root}:/usr/bin:/bin` },
            encoding: 'utf8',
          },
        );
        assert.equal(result.status, 22, result.stderr);
        assert.throws(() => readFileSync(join(root, 'executed')), {
          code: 'ENOENT',
        });
      } finally {
        rmSync(root, { recursive: true, force: true });
      }
    },
  );
}
