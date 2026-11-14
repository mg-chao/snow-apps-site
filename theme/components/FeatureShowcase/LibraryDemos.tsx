import { type PointerEvent, useEffect, useRef, useState } from 'react';
import { HistoryIcon, PinToScreenIcon, ReloadIcon } from '../HomeLayout/icons';
import { Playback, SampleNote, useDemo } from './shared';

export function PinDemo({ isZh }: { isZh: boolean }) {
  const demo = useDemo({ duration: 7400 });
  const [manual, setManual] = useState(false);
  const [pinned, setPinned] = useState(false);
  const [position, setPosition] = useState({ x: 12, y: 12 });
  const [limits, setLimits] = useState({ x: 32, y: 0 });
  const [opacity, setOpacity] = useState(100);
  const stage = useRef<HTMLDivElement>(null);
  const card = useRef<HTMLDivElement>(null);
  const drag = useRef<{
    x: number;
    y: number;
    left: number;
    top: number;
  } | null>(null);
  const isPinned = manual ? pinned : demo.progress > 0.23;
  const autoX =
    demo.progress < 0.42
      ? 12
      : 12 + Math.min(1, (demo.progress - 0.42) / 0.34) * 16;
  const x = Math.min(limits.x, manual ? position.x : autoX);
  const y = Math.min(
    limits.y,
    manual
      ? position.y
      : 12 + Math.sin(Math.min(1, demo.progress / 0.8) * Math.PI) * 5,
  );
  useEffect(() => {
    const bounds = stage.current;
    const pinnedCard = card.current;
    if (!bounds || !pinnedCard) return;
    const observer = new ResizeObserver(() => {
      const width = bounds.clientWidth;
      const height = bounds.clientHeight;
      setLimits({
        x: Math.max(0, ((width - pinnedCard.offsetWidth) / width) * 100),
        y: Math.max(0, ((height - pinnedCard.offsetHeight) / height) * 100),
      });
      setPosition((current) => {
        const next = {
          x: Math.max(
            0,
            Math.min(
              current.x,
              ((width - pinnedCard.offsetWidth) / width) * 100,
            ),
          ),
          y: Math.max(
            0,
            Math.min(
              current.y,
              ((height - pinnedCard.offsetHeight) / height) * 100,
            ),
          ),
        };
        return next.x === current.x && next.y === current.y ? current : next;
      });
    });
    observer.observe(bounds);
    observer.observe(pinnedCard);
    return () => observer.disconnect();
  }, []);
  function takeControl() {
    demo.interact();
    setManual(true);
    setPinned(isPinned);
    setPosition({ x, y });
  }
  function moveTo(left: number, top: number) {
    const bounds = stage.current?.getBoundingClientRect();
    const size = card.current?.getBoundingClientRect();
    if (!bounds || !size || !card.current) return position;
    const next = {
      x:
        (Math.max(0, Math.min(bounds.width - size.width, left)) /
          bounds.width) *
        100,
      y:
        (Math.max(0, Math.min(bounds.height - size.height, top)) /
          bounds.height) *
        100,
    };
    card.current.style.left = `${next.x}%`;
    card.current.style.top = `${next.y}%`;
    return next;
  }
  function startDrag(event: PointerEvent<HTMLButtonElement>) {
    takeControl();
    const bounds = stage.current?.getBoundingClientRect();
    const rect = card.current?.getBoundingClientRect();
    if (!isPinned || !bounds || !rect) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    drag.current = {
      x: event.clientX,
      y: event.clientY,
      left: rect.left - bounds.left,
      top: rect.top - bounds.top,
    };
  }
  function finishDrag(event: PointerEvent<HTMLButtonElement>) {
    if (!drag.current) return;
    setPosition(
      moveTo(
        drag.current.left + event.clientX - drag.current.x,
        drag.current.top + event.clientY - drag.current.y,
      ),
    );
    drag.current = null;
  }
  function reset() {
    demo.reset();
    setManual(true);
    setPinned(isPinned);
    setPosition({ x: 12, y: 12 });
    setOpacity(100);
  }
  return (
    <div
      className="snow-demo snow-pin-demo"
      ref={demo.containerRef}
      onPointerDownCapture={(event) => {
        if (!(event.target as Element).closest('.snow-demo-footer'))
          takeControl();
      }}
      onKeyDownCapture={(event) => {
        if (!(event.target as Element).closest('.snow-demo-footer'))
          takeControl();
      }}
    >
      <div className="snow-demo-titlebar">
        <PinToScreenIcon />
        <span>{isZh ? '贴图' : 'Pin to screen'}</span>
        <span className="snow-demo-badge">
          {isZh ? '交互演示' : 'Interactive demo'}
        </span>
      </div>
      <div className="snow-pin-stage" ref={stage}>
        <div className="snow-pin-editor" data-nosnippet="">
          <div>review.md</div>
          <p># {isZh ? '设计评审' : 'Design review'}</p>
          <p>
            {isZh
              ? '参考截图，继续你的工作。'
              : 'Keep your reference beside your work.'}
          </p>
          <code>capture → annotate → share</code>
          <p className="snow-pin-editor__comment">
            {isZh
              ? '无需在窗口之间反复切换。'
              : 'Stay focused without switching windows.'}
          </p>
        </div>
        <div
          ref={card}
          className={`snow-pin-card${isPinned ? ' is-pinned' : ''}`}
          style={{ left: `${x}%`, top: `${y}%`, opacity: opacity / 100 }}
        >
          {isPinned && (
            <button
              type="button"
              className="snow-pin-handle"
              onPointerDown={startDrag}
              onPointerMove={(event) => {
                if (drag.current)
                  moveTo(
                    drag.current.left + event.clientX - drag.current.x,
                    drag.current.top + event.clientY - drag.current.y,
                  );
              }}
              onPointerUp={finishDrag}
              onPointerCancel={finishDrag}
              onKeyDown={(event) => {
                if (
                  !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(
                    event.key,
                  )
                )
                  return;
                event.preventDefault();
                takeControl();
                const bounds = stage.current?.getBoundingClientRect();
                if (!bounds) return;
                const dx =
                  event.key === 'ArrowLeft'
                    ? -12
                    : event.key === 'ArrowRight'
                      ? 12
                      : 0;
                const dy =
                  event.key === 'ArrowUp'
                    ? -12
                    : event.key === 'ArrowDown'
                      ? 12
                      : 0;
                setPosition(
                  moveTo(
                    (x / 100) * bounds.width + dx,
                    (y / 100) * bounds.height + dy,
                  ),
                );
              }}
              aria-label={
                isZh
                  ? '拖动贴图，或用方向键移动'
                  : 'Drag pin, or move with arrow keys'
              }
            >
              <PinToScreenIcon />
              {isZh ? '始终置顶 · 拖动这里' : 'Always on top · drag here'}
            </button>
          )}
          <SampleNote isZh={isZh} compact />
        </div>
      </div>
      <div
        className="snow-demo-controls"
        onPointerDownCapture={demo.interact}
        onKeyDownCapture={demo.interact}
      >
        <button
          type="button"
          className="snow-demo-button snow-demo-button--primary"
          onClick={() => {
            takeControl();
            setPinned(!isPinned);
          }}
        >
          {isPinned
            ? isZh
              ? '取消贴图'
              : 'Unpin image'
            : isZh
              ? '固定到屏幕'
              : 'Pin image'}
        </button>
        <button type="button" className="snow-demo-button" onClick={reset}>
          <ReloadIcon />
          {isZh ? '重置位置' : 'Reset position'}
        </button>
        <label className="snow-pin-opacity">
          {isZh ? '透明度' : 'Opacity'}
          <input
            type="range"
            min="25"
            max="100"
            value={opacity}
            disabled={!isPinned}
            onChange={(event) => {
              takeControl();
              setOpacity(Number(event.target.value));
            }}
          />
          <span>{opacity}%</span>
        </label>
      </div>
      <p className="snow-demo-hint" role="status">
        {isPinned
          ? isZh
            ? '拖动标题栏；键盘聚焦后用方向键移动。'
            : 'Drag the title bar, or focus it and use the arrow keys.'
          : isZh
            ? '把截图变成浮在其他窗口上方的参考图。'
            : 'Turn a capture into a reference above other windows.'}
      </p>
      <div className="snow-demo-footer">
        <span>
          {isZh ? '截图 → 贴图 → 继续工作' : 'Capture → pin → keep working'}
        </span>
        <Playback
          demo={demo}
          isZh={isZh}
          active={!manual}
          onReplay={() => {
            setManual(false);
            setPinned(false);
            setOpacity(100);
            demo.play();
          }}
        />
      </div>
    </div>
  );
}

type HistoryEntry = {
  id: string;
  source: string;
  zh: string;
  en: string;
  time: string;
  kind: 'note' | 'table' | 'ocr' | 'app';
};
const entries: HistoryEntry[] = [
  {
    id: 'review',
    source: 'clipboard',
    zh: '设计评审截图',
    en: 'Design review capture',
    time: '10:42',
    kind: 'note',
  },
  {
    id: 'table',
    source: 'file',
    zh: '发布任务表格',
    en: 'Release task table',
    time: '10:38',
    kind: 'table',
  },
  {
    id: 'text',
    source: 'clipboard',
    zh: '文本识别素材',
    en: 'Text recognition source',
    time: '10:31',
    kind: 'ocr',
  },
  {
    id: 'reference',
    source: 'pinned',
    zh: 'Snow Shot 设置参考',
    en: 'Snow Shot settings reference',
    time: '09:56',
    kind: 'app',
  },
];
function HistoryImage({ entry, isZh }: { entry: HistoryEntry; isZh: boolean }) {
  if (entry.kind === 'note') return <SampleNote isZh={isZh} compact />;
  if (entry.kind === 'app')
    return (
      <img
        src={`/images/${isZh ? 'zh' : 'en'}/main.webp`}
        alt={isZh ? 'Snow Shot 实际应用界面' : 'Actual Snow Shot application'}
        loading="lazy"
      />
    );
  if (entry.kind === 'ocr')
    return (
      <img
        src={`/images/demos/recognition-text-${isZh ? 'zh' : 'en'}.svg`}
        alt={
          isZh
            ? '文本识别的原始发布说明'
            : 'Original release note from the text recognition demo'
        }
        loading="lazy"
      />
    );
  return (
    <img
      src={`/images/demos/recognition-table-${isZh ? 'zh' : 'en'}.svg`}
      alt={
        isZh
          ? '文档识别的原始任务表格'
          : 'Original task table from document recognition'
      }
      loading="lazy"
    />
  );
}

export function HistoryDemo({ isZh }: { isZh: boolean }) {
  const demo = useDemo({ duration: 7200 });
  const [manual, setManual] = useState(false);
  const [filter, setFilter] = useState('all');
  const [selected, setSelected] = useState('review');
  const [opened, setOpened] = useState(false);
  const close = useRef<HTMLButtonElement>(null);
  const previousFocus = useRef<HTMLElement | null>(null);
  const currentId = manual
    ? selected
    : demo.progress > 0.25
      ? 'table'
      : 'review';
  const preview = manual ? opened : demo.progress > 0.48 && demo.progress < 0.9;
  const entry = entries.find((item) => item.id === currentId) ?? entries[0];
  const filtered = entries.filter(
    (item) => filter === 'all' || item.source === filter,
  );
  const sources = isZh
    ? {
        all: '所有来源',
        clipboard: '剪贴板',
        file: '文件',
        pinned: '贴图',
        monitor: '当前显示器',
      }
    : {
        all: 'All sources',
        clipboard: 'Clipboard',
        file: 'File',
        pinned: 'Pinned image',
        monitor: 'Current monitor',
      };
  function takeControl() {
    demo.interact();
    setManual(true);
    setSelected(currentId);
    setOpened(preview);
  }
  function open() {
    takeControl();
    previousFocus.current = document.activeElement as HTMLElement;
    setOpened(true);
  }
  function back() {
    takeControl();
    setOpened(false);
  }
  useEffect(() => {
    if (opened) close.current?.focus();
    else if (previousFocus.current) {
      previousFocus.current.focus();
      previousFocus.current = null;
    }
  }, [opened]);
  return (
    <div
      className="snow-demo snow-history-demo"
      ref={demo.containerRef}
      onPointerDownCapture={(event) => {
        if (!(event.target as Element).closest('.snow-demo-playback'))
          takeControl();
      }}
      onKeyDownCapture={(event) => {
        if (!(event.target as Element).closest('.snow-demo-playback'))
          takeControl();
      }}
    >
      <div className="snow-demo-titlebar">
        <HistoryIcon />
        <span>{isZh ? '截图历史' : 'Screenshot history'}</span>
        <span className="snow-demo-badge">
          {isZh ? '示例记录' : 'Sample library'}
        </span>
      </div>
      <div className="snow-history-bar">
        <label>
          {isZh ? '来源' : 'Source'}
          <select
            value={filter}
            onChange={(event) => {
              takeControl();
              setFilter(event.target.value);
              setOpened(false);
              const first = entries.find(
                (item) =>
                  event.target.value === 'all' ||
                  item.source === event.target.value,
              );
              if (first) setSelected(first.id);
            }}
          >
            {Object.entries(sources).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <span data-nosnippet="">
          {isZh
            ? `今天 · ${filtered.length} 张截图`
            : `Today · ${filtered.length} captures`}
        </span>
      </div>
      <div className="snow-history-content">
        <div className="snow-history-list" hidden={preview}>
          {filtered.length ? (
            filtered.map((item) => (
              <button
                type="button"
                key={item.id}
                className={`snow-history-entry${currentId === item.id ? ' is-selected' : ''}`}
                aria-pressed={currentId === item.id}
                aria-label={`${isZh ? item.zh : item.en}, ${item.time}, ${sources[item.source as keyof typeof sources]}`}
                onClick={() => {
                  takeControl();
                  setSelected(item.id);
                  setOpened(false);
                }}
                onDoubleClick={() => {
                  takeControl();
                  setSelected(item.id);
                  setOpened(true);
                  previousFocus.current = document.activeElement as HTMLElement;
                }}
              >
                <div className="snow-history-thumb" data-nosnippet="">
                  <HistoryImage entry={item} isZh={isZh} />
                </div>
                <strong>
                  <span data-nosnippet="">{isZh ? item.zh : item.en}</span>
                </strong>
                <span data-nosnippet="">
                  {item.time} / {sources[item.source as keyof typeof sources]}
                </span>
              </button>
            ))
          ) : (
            <div className="snow-history-empty">
              <HistoryIcon />
              <strong>
                {isZh ? '这个来源还没有截图' : 'No captures from this source'}
              </strong>
              <p>
                {isZh
                  ? '选择其他来源，继续浏览示例记录。'
                  : 'Choose another source to explore the sample captures.'}
              </p>
              <button
                type="button"
                className="snow-demo-button"
                onClick={() => {
                  takeControl();
                  setFilter('all');
                  setSelected('review');
                }}
              >
                {isZh ? '显示全部' : 'Show all captures'}
              </button>
            </div>
          )}
        </div>
        {preview && (
          <section
            className="snow-history-preview"
            aria-label={isZh ? '大图预览' : 'Large preview'}
            onKeyDown={(event) => {
              if (event.key === 'Escape') back();
            }}
          >
            <div>
              <strong>
                <span data-nosnippet="">{isZh ? entry.zh : entry.en}</span>
              </strong>
              <button
                ref={close}
                type="button"
                className="snow-demo-button"
                onClick={back}
              >
                {isZh ? '返回列表' : 'Back to library'}
              </button>
            </div>
            <div className="snow-history-preview__image" data-nosnippet="">
              <HistoryImage entry={entry} isZh={isZh} />
            </div>
          </section>
        )}
      </div>
      <div className="snow-demo-controls">
        <button
          type="button"
          className="snow-demo-button snow-demo-button--primary"
          disabled={!filtered.length || preview}
          onClick={open}
        >
          {isZh ? '打开选中截图' : 'Open selected capture'}
        </button>
        <span className="snow-demo-hint">
          {isZh
            ? '选择缩略图，再打开预览。也可双击打开。'
            : 'Select a thumbnail and open it, or double-click to preview.'}
        </span>
      </div>
      <div className="snow-demo-footer">
        <span>
          {isZh
            ? '截过的内容，随时找回。'
            : 'Your earlier captures, ready to revisit.'}
        </span>
        <Playback
          demo={{
            ...demo,
            play: () => {
              setManual(false);
              setFilter('all');
              setOpened(false);
              demo.play();
            },
          }}
          isZh={isZh}
        />
      </div>
    </div>
  );
}
