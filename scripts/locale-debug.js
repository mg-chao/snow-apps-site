// Temporary diagnostics, enabled per tab by opening /?locale-debug=1.
(() => {
  const revision = 'locale-debug-4';
  const enabledKey = 'snow-shot-locale-debug-enabled';
  const traceKey = 'snow-shot-locale-debug-v3';
  let enabled = new URLSearchParams(location.search).has('locale-debug');
  let trace = [];
  try {
    enabled ||= sessionStorage.getItem(enabledKey) === '1';
    if (enabled) sessionStorage.setItem(enabledKey, '1');
    const previous = JSON.parse(sessionStorage.getItem(traceKey) ?? '[]');
    if (Array.isArray(previous)) trace = previous.slice(-59);
  } catch {
    // Diagnostics still work on this page when session storage is unavailable.
  }
  if (!enabled) return;
  window.__SNOW_SHOT_LOCALE_DEBUG__ = true;

  const loadId = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
  const entryUrl = location.href;
  let output;
  let previousState;
  let decisionReceived = false;
  const readStorage = (key) => {
    try {
      return localStorage.getItem(key);
    } catch (error) {
      return `unavailable: ${error.message}`;
    }
  };
  const browserInfo = () => {
    let intlLocale;
    try {
      intlLocale = Intl.DateTimeFormat().resolvedOptions().locale;
    } catch (error) {
      intlLocale = `unavailable: ${error.message}`;
    }
    return {
      navigatorLanguage: navigator.language,
      navigatorLanguages: Array.from(navigator.languages ?? []),
      intlLocale,
      userAgent: navigator.userAgent,
    };
  };
  const pageState = () => ({
    page: location.href,
    readyState: document.readyState,
    renderedLanguage: document.documentElement.lang,
    title: document.title,
    heading: document.querySelector('h1')?.textContent.trim().slice(0, 200),
    savedSitePreference: readStorage('snow-shot-language'),
    legacyVisitedFlag: readStorage('rspress-visited'),
  });
  const render = () => {
    if (!output || !enabled) return;
    output.value = JSON.stringify(
      {
        debugRevision: revision,
        redirectScriptRevision: document
          .getElementById('snow-shot-locale')
          ?.getAttribute('data-revision'),
        loadId,
        entryUrl,
        redirectScriptReported: decisionReceived,
        ...pageState(),
        ...browserInfo(),
        trace,
      },
      null,
      2,
    );
  };
  const record = (event, details = {}) => {
    if (!enabled) return;
    const entry = {
      time: new Date().toISOString(),
      loadId,
      event,
      ...pageState(),
      ...details,
    };
    trace = [...trace, entry].slice(-60);
    try {
      sessionStorage.setItem(traceKey, JSON.stringify(trace));
    } catch {
      // Keep the report in memory if persistence is blocked.
    }
    console.info('[Snow Shot locale]', entry);
    render();
  };
  const sample = (event) => {
    const state = JSON.stringify(pageState());
    if (state !== previousState) {
      previousState = state;
      record(event);
    }
  };

  window.addEventListener('snow-shot:locale-debug', (event) => {
    decisionReceived = true;
    record('redirect script', event.detail);
  });
  window.addEventListener(
    'error',
    (event) => {
      record('script or resource error', {
        message: event.message,
        file: event.filename,
        line: event.lineno,
        column: event.colno,
        resource: event.target?.src ?? event.target?.href,
      });
    },
    true,
  );
  window.addEventListener('unhandledrejection', (event) => {
    record('unhandled promise rejection', {
      message: String(event.reason?.message ?? event.reason).slice(0, 1000),
    });
  });
  for (const event of ['pageshow', 'pagehide', 'popstate', 'hashchange']) {
    window.addEventListener(event, (details) => {
      record(event, { restoredFromCache: details.persisted });
    });
  }
  window.addEventListener('languagechange', () => {
    record('browser languages changed', browserInfo());
  });
  window.addEventListener('storage', (event) => {
    if (event.key === 'snow-shot-language') {
      record('site language changed in another tab', {
        previousPreference: event.oldValue,
        newPreference: event.newValue,
      });
    }
  });
  document.addEventListener(
    'click',
    (event) => {
      if (!(event.target instanceof Element)) return;
      const link = event.target.closest('a[href]');
      if (
        !link ||
        new URL(link.href, location.href).origin !== location.origin
      ) {
        return;
      }
      record('internal link clicked', {
        target: link.href,
        linkText: link.textContent.trim().slice(0, 100),
        linkLanguage: link.getAttribute('hreflang'),
        linkRel: link.getAttribute('rel'),
        trusted: event.isTrusted,
        button: event.button,
        modifiers: {
          ctrl: event.ctrlKey,
          meta: event.metaKey,
          shift: event.shiftKey,
          alt: event.altKey,
        },
      });
    },
    true,
  );
  record('diagnostics started', {
    debugRevision: revision,
    navigationType: performance.getEntriesByType('navigation')[0]?.type,
    ...browserInfo(),
  });

  document.addEventListener('DOMContentLoaded', () => {
    const panel = document.createElement('aside');
    panel.id = 'snow-shot-locale-debug-panel';
    panel.setAttribute('aria-label', 'Language debug report');
    panel.style.cssText =
      'position:fixed;right:12px;bottom:12px;z-index:2147483647;width:min(600px,calc(100vw - 24px));padding:16px;background:#fff;color:#111;border:2px solid #555;border-radius:8px;box-shadow:0 4px 24px #0005;font:14px/1.5 monospace;text-align:left;';
    const title = document.createElement('strong');
    title.textContent = `语言诊断 / Language debug (${revision})`;
    const hint = document.createElement('p');
    hint.textContent =
      '复现问题后复制报告。诊断会跟随本标签页的导航。Reproduce the issue, then copy the report.';
    output = document.createElement('textarea');
    output.readOnly = true;
    output.setAttribute('aria-label', 'Language debug JSON');
    output.style.cssText =
      'display:block;width:100%;height:260px;max-height:40vh;padding:8px;margin:8px 0;background:#f5f5f5;color:#111;border:1px solid #888;font:12px/1.5 monospace;box-sizing:border-box;';
    const copy = document.createElement('button');
    copy.textContent = '复制报告 / Copy report';
    copy.style.cssText =
      'padding:6px 12px;border:1px solid #888;border-radius:4px;background:#eee;color:#111;cursor:pointer;';
    copy.addEventListener('click', async () => {
      sample('state at report copy');
      render();
      try {
        await navigator.clipboard.writeText(output.value);
        copy.textContent = '已复制 / Copied';
      } catch {
        output.focus();
        output.select();
        copy.textContent = '按 Ctrl+C 复制 / Press Ctrl+C';
      }
    });
    const stop = document.createElement('button');
    stop.textContent = '停止诊断 / Stop debug';
    stop.style.cssText = copy.style.cssText;
    stop.style.marginLeft = '8px';
    stop.addEventListener('click', () => {
      enabled = false;
      window.__SNOW_SHOT_LOCALE_DEBUG__ = false;
      clearInterval(timer);
      observer.disconnect();
      try {
        sessionStorage.removeItem(enabledKey);
      } catch {
        // Stopping in-memory diagnostics does not require storage access.
      }
      const url = new URL(location.href);
      url.searchParams.delete('locale-debug');
      history.replaceState(history.state, '', url);
      panel.remove();
    });
    panel.append(title, hint, output, copy, stop);
    document.body.append(panel);
    record('DOM ready', { redirectScriptReported: decisionReceived });
    const observer = new MutationObserver(() =>
      sample('HTML language changed'),
    );
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['lang'],
    });
    // Observe SPA navigation, rendered headings and preference changes without
    // replacing History or Storage methods. Only changed snapshots are logged.
    const timer = setInterval(() => sample('page or preference changed'), 500);
  });
})();
