import {
  type CSSProperties,
  type KeyboardEvent,
  type PointerEvent,
  useEffect,
  useId,
  useRef,
  useState,
} from 'react';
import { ReloadIcon } from '../HomeLayout/icons';
import { SampleNote, useDemo } from './shared';
import './CaptureDemos.css';

type Point = { x: number; y: number };
type Selection = Point & { w: number; h: number };
type Tool = 'arrow' | 'rectangle' | 'highlight';
type Mark = { id: number; tool: Tool; from: Point; to: Point };

const defaultSelection: Selection = { x: 12, y: 17, w: 75, h: 66 };
const clamp = (value: number, min = 0, max = 100) =>
  Math.min(max, Math.max(min, value));
const between = (a: number, b: number, t: number) =>
  a + (b - a) * clamp(t, 0, 1);

function atPointer(event: PointerEvent<HTMLElement>, node: HTMLElement): Point {
  const bounds = node.getBoundingClientRect();
  return {
    x: clamp(((event.clientX - bounds.left) / bounds.width) * 100),
    y: clamp(((event.clientY - bounds.top) / bounds.height) * 100),
  };
}

function rectBetween(a: Point, b: Point): Selection {
  return {
    x: Math.min(a.x, b.x),
    y: Math.min(a.y, b.y),
    w: Math.abs(a.x - b.x),
    h: Math.abs(a.y - b.y),
  };
}

function ToolIcon({ tool }: { tool: Tool }) {
  return (
    <img
      src={`/images/demos/capture-${tool}.svg`}
      className="snow-capture-tool-icon"
      alt=""
      width="20"
      height="20"
      draggable={false}
    />
  );
}

function Scene({ isZh }: { isZh: boolean }) {
  return (
    <div className="snow-capture-desktop" aria-hidden="true">
      <div className="snow-capture-desktop__menu">
        <img src="/images/app-icon.webp" alt="" width="15" height="15" />
        <span>Snow Shot</span>
        <span>{isZh ? '项目工作区' : 'Project workspace'}</span>
        <time>09:41</time>
      </div>
      <div className="snow-capture-desktop__note">
        <div className="snow-capture-windowbar">
          <i />
          <i />
          <i />
          <span>{isZh ? '发布笔记.md' : 'release-notes.md'}</span>
        </div>
        <SampleNote isZh={isZh} />
      </div>
      <div className="snow-capture-desktop__aside">
        <span>{isZh ? '今天' : 'TODAY'}</span>
        <strong>09:30</strong>
        <p>{isZh ? '一起打磨下一次更新' : 'Make the next update better'}</p>
        <span>{isZh ? '产品评审 · 30 分钟' : 'Product review · 30 min'}</span>
      </div>
    </div>
  );
}

function DemoReplay({
  isZh,
  playing,
  canResume,
  onReplay,
  onPause,
  onResume,
}: {
  isZh: boolean;
  playing: boolean;
  canResume: boolean;
  onReplay: () => void;
  onPause: () => void;
  onResume: () => void;
}) {
  return (
    <div className="snow-capture-playback" data-demo-playback="true">
      <button type="button" onClick={onReplay}>
        <ReloadIcon /> {isZh ? '重播演示' : 'Replay demo'}
      </button>
      {(playing || canResume) && (
        <button type="button" onClick={playing ? onPause : onResume}>
          <span aria-hidden="true">{playing ? 'Ⅱ' : '▷'}</span>
          {playing ? (isZh ? '暂停' : 'Pause') : isZh ? '继续' : 'Resume'}
        </button>
      )}
    </div>
  );
}

export function RegionSelectionDemo({ isZh }: { isZh: boolean }) {
  const demo = useDemo({ duration: 7600 });
  const sceneRef = useRef<HTMLDivElement>(null);
  const drag = useRef<{
    start: Point;
    selection: Selection | null;
    mode: 'new' | 'move' | 'resize';
  } | null>(null);
  const [manual, setManual] = useState(false);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [drawing, setDrawing] = useState(false);
  const [sceneSize, setSceneSize] = useState({ width: 600, height: 340 });
  const sampleSelection: Selection =
    sceneSize.width < 400 ? { x: 5, y: 12, w: 90, h: 82 } : defaultSelection;
  const p = demo.progress;
  const autoSelection =
    p < 0.16
      ? null
      : {
          x: sampleSelection.x,
          y: sampleSelection.y,
          w:
            p < 0.46
              ? between(1, sampleSelection.w * 0.84, (p - 0.16) / 0.3)
              : between(
                  sampleSelection.w * 0.84,
                  sampleSelection.w,
                  (p - 0.58) / 0.19,
                ),
          h:
            p < 0.46
              ? between(1, sampleSelection.h * 0.8, (p - 0.16) / 0.3)
              : between(
                  sampleSelection.h * 0.8,
                  sampleSelection.h,
                  (p - 0.58) / 0.19,
                ),
        };
  const visibleSelection = manual ? selection : autoSelection;
  const complete = manual ? Boolean(selection) && !drawing : p >= 0.8;

  useEffect(() => {
    const node = sceneRef.current;
    if (!node) return;
    const observer = new ResizeObserver(([entry]) => {
      setSceneSize({
        width: entry.contentRect.width,
        height: entry.contentRect.height,
      });
    });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  function takeControl() {
    demo.interact();
    if (!manual) setSelection(autoSelection);
    setManual(true);
  }

  function captureInteraction(
    event: PointerEvent<HTMLDivElement> | KeyboardEvent<HTMLDivElement>,
  ) {
    if ((event.target as HTMLElement).closest('[data-demo-playback]')) return;
    takeControl();
  }

  function pointerDown(event: PointerEvent<HTMLDivElement>) {
    if (event.button !== 0) return;
    const point = atPointer(event, event.currentTarget);
    const handle = (event.target as HTMLElement).closest('[data-resize]');
    const current = visibleSelection;
    const inSelection =
      current &&
      point.x >= current.x &&
      point.x <= current.x + current.w &&
      point.y >= current.y &&
      point.y <= current.y + current.h;
    drag.current = {
      start: point,
      selection: current,
      mode: handle ? 'resize' : inSelection ? 'move' : 'new',
    };
    takeControl();
    setDrawing(true);
    if (!inSelection && !handle) setSelection({ ...point, w: 0, h: 0 });
    event.currentTarget.setPointerCapture(event.pointerId);
    event.preventDefault();
  }

  function pointerMove(event: PointerEvent<HTMLDivElement>) {
    const active = drag.current;
    if (!active) return;
    const point = atPointer(event, event.currentTarget);
    if (active.mode === 'new') setSelection(rectBetween(active.start, point));
    else if (active.selection) {
      const original = active.selection;
      setSelection(
        active.mode === 'move'
          ? {
              ...original,
              x: clamp(
                original.x + point.x - active.start.x,
                0,
                100 - original.w,
              ),
              y: clamp(
                original.y + point.y - active.start.y,
                0,
                100 - original.h,
              ),
            }
          : {
              ...original,
              w: clamp(point.x - original.x, 6, 100 - original.x),
              h: clamp(point.y - original.y, 6, 100 - original.y),
            },
      );
    }
  }

  function pointerUp(event: PointerEvent<HTMLDivElement>) {
    if (!drag.current) return;
    drag.current = null;
    setDrawing(false);
    setSelection((current) =>
      current && current.w > 2 && current.h > 2 ? current : null,
    );
    if (event.currentTarget.hasPointerCapture(event.pointerId))
      event.currentTarget.releasePointerCapture(event.pointerId);
  }

  function adjust(event: KeyboardEvent<HTMLDivElement>) {
    if (
      !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Escape'].includes(
        event.key,
      )
    )
      return;
    event.preventDefault();
    takeControl();
    if (event.key === 'Escape') {
      setSelection(null);
      return;
    }
    const current = visibleSelection ?? sampleSelection;
    const dx =
      event.key === 'ArrowLeft' ? -2 : event.key === 'ArrowRight' ? 2 : 0;
    const dy = event.key === 'ArrowUp' ? -2 : event.key === 'ArrowDown' ? 2 : 0;
    setSelection(
      event.shiftKey
        ? {
            ...current,
            w: clamp(current.w + dx, 6, 100 - current.x),
            h: clamp(current.h + dy, 6, 100 - current.y),
          }
        : {
            ...current,
            x: clamp(current.x + dx, 0, 100 - current.w),
            y: clamp(current.y + dy, 0, 100 - current.h),
          },
    );
  }

  function reset() {
    takeControl();
    drag.current = null;
    setSelection(null);
    setDrawing(false);
  }

  const pointer =
    p < 0.16
      ? {
          x: between(25, sampleSelection.x, p / 0.16),
          y: between(85, sampleSelection.y, p / 0.16),
        }
      : {
          x: sampleSelection.x + (autoSelection?.w ?? 0),
          y: sampleSelection.y + (autoSelection?.h ?? 0),
        };
  const style = visibleSelection
    ? ({
        left: `${visibleSelection.x}%`,
        top: `${visibleSelection.y}%`,
        width: `${visibleSelection.w}%`,
        height: `${visibleSelection.h}%`,
      } satisfies CSSProperties)
    : undefined;

  return (
    <div
      className="snow-demo snow-capture-demo"
      ref={demo.containerRef}
      onPointerDownCapture={captureInteraction}
      onKeyDownCapture={captureInteraction}
    >
      <div className="snow-capture-demo__head">
        <span>{isZh ? '区域截图' : 'Region capture'}</span>
        <span className="snow-capture-demo__badge">
          {isZh ? '交互演示' : 'Interactive demo'}
        </span>
      </div>
      <div
        className={`snow-capture-scene ${!manual && demo.playing ? 'is-playing' : ''}`}
        ref={sceneRef}
        role="application"
        aria-label={
          isZh
            ? '拖拽选择截图区域。方向键移动，Shift 加方向键调整大小，Escape 重置。'
            : 'Drag to select. Arrow keys move; Shift and arrows resize; Escape resets.'
        }
        // biome-ignore lint/a11y/noNoninteractiveTabindex: This canvas implements arrow-key movement and resizing of a two-dimensional selection.
        tabIndex={0}
        onPointerDown={pointerDown}
        onPointerMove={pointerMove}
        onPointerUp={pointerUp}
        onPointerCancel={pointerUp}
        onKeyDown={adjust}
      >
        <Scene isZh={isZh} />
        {visibleSelection && (
          <div className="snow-capture-selection" style={style}>
            <span
              className="snow-capture-dimensions"
              style={{
                top: visibleSelection.y < 10 ? 8 : undefined,
                bottom: visibleSelection.y < 10 ? 'auto' : undefined,
                left: visibleSelection.x > 75 ? 'auto' : undefined,
                right: visibleSelection.x > 75 ? 0 : undefined,
              }}
            >
              {Math.round((visibleSelection.w * sceneSize.width) / 100)} ×{' '}
              {Math.round((visibleSelection.h * sceneSize.height) / 100)}
            </span>
            <i className="snow-capture-corner snow-capture-corner--tl" />
            <i className="snow-capture-corner snow-capture-corner--tr" />
            <i className="snow-capture-corner snow-capture-corner--bl" />
            <span
              className="snow-capture-corner snow-capture-corner--br"
              data-resize="true"
              aria-hidden="true"
            />
          </div>
        )}
        {!manual && demo.playing && (
          <span
            className="snow-capture-pointer"
            style={{ left: `${pointer.x}%`, top: `${pointer.y}%` }}
            aria-hidden="true"
          />
        )}
      </div>
      <div
        className={`snow-capture-result-toolbar ${complete ? 'is-visible' : ''}`}
      >
        <div className="snow-capture-result-toolbar__tools" aria-hidden="true">
          <ToolIcon tool="rectangle" />
          <ToolIcon tool="arrow" />
          <ToolIcon tool="highlight" />
          <span>T</span>
        </div>
        <span>{isZh ? '选区已就绪' : 'Selection ready'}</span>
        <button
          type="button"
          disabled={!complete}
          onClick={() => {
            takeControl();
            const current = visibleSelection ?? sampleSelection;
            setSelection({
              ...current,
              w: clamp(current.w + 4, 6, 100 - current.x),
              h: clamp(current.h + 4, 6, 100 - current.y),
            });
          }}
        >
          {isZh ? '扩大选区' : 'Expand'}
        </button>
      </div>
      <div className="snow-capture-controls" onPointerDownCapture={takeControl}>
        <button
          type="button"
          onClick={() => {
            takeControl();
            setSelection(sampleSelection);
          }}
        >
          {isZh ? '选择示例区域' : 'Select sample region'}
        </button>
        <button type="button" onClick={reset}>
          {isZh ? '重置' : 'Reset'}
        </button>
      </div>
      <div className="snow-capture-demo__footer">
        <p role="status">
          {drawing
            ? isZh
              ? '松开以确认选区'
              : 'Release to confirm'
            : complete
              ? isZh
                ? '拖动选区移动；拖动右下角调整大小。'
                : 'Drag the selection to move; drag its corner to resize.'
              : isZh
                ? '在画面上拖拽，或点击“选择示例区域”。'
                : 'Drag on the scene or select the sample region.'}
        </p>
        <DemoReplay
          isZh={isZh}
          playing={demo.playing}
          canResume={!manual && !demo.reducedMotion && p > 0 && p < 1}
          onPause={demo.pause}
          onResume={demo.resume}
          onReplay={() => {
            drag.current = null;
            setManual(false);
            setDrawing(false);
            setSelection(null);
            demo.play();
          }}
        />
      </div>
    </div>
  );
}

const exampleMarks: Mark[] = [
  { id: 1, tool: 'rectangle', from: { x: 8, y: 14 }, to: { x: 90, y: 35 } },
  { id: 2, tool: 'highlight', from: { x: 11, y: 53 }, to: { x: 77, y: 60 } },
  { id: 3, tool: 'arrow', from: { x: 81, y: 85 }, to: { x: 66, y: 64 } },
];

function MarkShape({ mark, markerId }: { mark: Mark; markerId: string }) {
  const x = Math.min(mark.from.x, mark.to.x) * 6;
  const y = Math.min(mark.from.y, mark.to.y) * 3;
  const w = Math.abs(mark.from.x - mark.to.x) * 6;
  const h = Math.abs(mark.from.y - mark.to.y) * 3;
  if (mark.tool === 'arrow')
    return (
      <line
        className="snow-annotation-arrow"
        x1={mark.from.x * 6}
        y1={mark.from.y * 3}
        x2={mark.to.x * 6}
        y2={mark.to.y * 3}
        markerEnd={`url(#${markerId})`}
      />
    );
  return (
    <rect
      className={`snow-annotation-${mark.tool}`}
      x={x}
      y={y}
      width={Math.max(w, 3)}
      height={Math.max(h, 4)}
      rx="2"
    />
  );
}

export function AnnotationDemo({ isZh }: { isZh: boolean }) {
  const demo = useDemo({ duration: 8000 });
  const markerId = useId().replace(/:/g, '');
  const [tool, setTool] = useState<Tool>('arrow');
  const [marks, setMarks] = useState<Mark[]>([]);
  const [draft, setDraft] = useState<Mark | null>(null);
  const draftRef = useRef<Mark | null>(null);
  const nextId = useRef(10);
  const [manual, setManual] = useState(false);
  const p = demo.progress;
  const autoMarks = exampleMarks.flatMap((mark, index) => {
    const phase = clamp((p - 0.13 - index * 0.23) / 0.18, 0, 1);
    if (phase <= 0) return [];
    return [
      {
        ...mark,
        to: {
          x: between(mark.from.x, mark.to.x, phase),
          y: between(mark.from.y, mark.to.y, phase),
        },
      },
    ];
  });
  const shownMarks = manual ? marks : autoMarks;
  const activeTool = manual
    ? tool
    : p < 0.36
      ? 'rectangle'
      : p < 0.59
        ? 'highlight'
        : 'arrow';

  function takeControl() {
    demo.interact();
    if (!manual) {
      setMarks(autoMarks);
      setTool(activeTool);
    }
    setManual(true);
  }

  function captureInteraction(
    event: PointerEvent<HTMLDivElement> | KeyboardEvent<HTMLDivElement>,
  ) {
    if ((event.target as HTMLElement).closest('[data-demo-playback]')) return;
    takeControl();
  }

  function pointerDown(event: PointerEvent<HTMLDivElement>) {
    if (event.button !== 0) return;
    takeControl();
    const point = atPointer(event, event.currentTarget);
    const mark = {
      id: nextId.current++,
      tool: activeTool,
      from: point,
      to: point,
    };
    draftRef.current = mark;
    setDraft(mark);
    event.currentTarget.setPointerCapture(event.pointerId);
    event.preventDefault();
  }

  function pointerMove(event: PointerEvent<HTMLDivElement>) {
    if (!draftRef.current) return;
    draftRef.current = {
      ...draftRef.current,
      to: atPointer(event, event.currentTarget),
    };
    setDraft(draftRef.current);
  }

  function pointerUp(event: PointerEvent<HTMLDivElement>) {
    const mark = draftRef.current;
    if (!mark) return;
    if (
      Math.abs(mark.to.x - mark.from.x) + Math.abs(mark.to.y - mark.from.y) >
      1
    )
      setMarks((current) => [...current, mark]);
    draftRef.current = null;
    setDraft(null);
    if (event.currentTarget.hasPointerCapture(event.pointerId))
      event.currentTarget.releasePointerCapture(event.pointerId);
  }

  function reset() {
    takeControl();
    draftRef.current = null;
    setDraft(null);
    setMarks([]);
  }

  const labels: Record<Tool, string> = isZh
    ? { arrow: '箭头', rectangle: '矩形', highlight: '荧光笔' }
    : { arrow: 'Arrow', rectangle: 'Rectangle', highlight: 'Highlighter' };

  return (
    <div
      className="snow-demo snow-annotation-demo"
      ref={demo.containerRef}
      onPointerDownCapture={captureInteraction}
      onKeyDownCapture={captureInteraction}
    >
      <div className="snow-capture-demo__head">
        <span>{isZh ? '截图标注' : 'Screenshot annotation'}</span>
        <span className="snow-capture-demo__badge">
          {isZh ? '交互演示' : 'Interactive demo'}
        </span>
      </div>
      <fieldset
        className="snow-annotation-toolbar"
        aria-label={isZh ? '标注工具' : 'Annotation tools'}
      >
        {(['rectangle', 'arrow', 'highlight'] as Tool[]).map((item) => (
          <button
            type="button"
            key={item}
            aria-pressed={activeTool === item}
            onClick={() => {
              takeControl();
              setTool(item);
            }}
          >
            <ToolIcon tool={item} />
            <span>{labels[item]}</span>
          </button>
        ))}
        <span
          className="snow-annotation-color"
          title={isZh ? '标注颜色' : 'Annotation color'}
        />
        <button
          type="button"
          className="snow-annotation-undo"
          disabled={shownMarks.length === 0}
          onClick={() => {
            takeControl();
            setMarks((current) => current.slice(0, -1));
          }}
        >
          {isZh ? '撤销' : 'Undo'}
        </button>
      </fieldset>
      <div
        className={`snow-annotation-canvas ${!manual && demo.playing ? 'is-playing' : ''}`}
        role="application"
        aria-label={
          isZh
            ? '在截图上拖拽以绘制标注；也可以使用下方的添加标注按钮。'
            : 'Drag on the screenshot to annotate, or use Add annotation below.'
        }
        onPointerDown={pointerDown}
        onPointerMove={pointerMove}
        onPointerUp={pointerUp}
        onPointerCancel={() => {
          draftRef.current = null;
          setDraft(null);
        }}
      >
        <div className="snow-annotation-paper">
          <SampleNote isZh={isZh} />
        </div>
        <svg
          viewBox="0 0 600 300"
          preserveAspectRatio="none"
          className="snow-annotation-layer"
          aria-hidden="true"
        >
          <defs>
            <marker
              id={markerId}
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="7"
              markerHeight="7"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
            </marker>
          </defs>
          {shownMarks.map((mark) => (
            <MarkShape key={mark.id} mark={mark} markerId={markerId} />
          ))}
          {draft && <MarkShape mark={draft} markerId={markerId} />}
        </svg>
        {!manual && demo.playing && autoMarks.length > 0 && (
          <span
            className="snow-capture-pointer"
            aria-hidden="true"
            style={{
              left: `${autoMarks[autoMarks.length - 1].to.x}%`,
              top: `${autoMarks[autoMarks.length - 1].to.y}%`,
            }}
          />
        )}
      </div>
      <div className="snow-capture-controls">
        <button
          type="button"
          onClick={() => {
            takeControl();
            const example =
              exampleMarks.find((mark) => mark.tool === activeTool) ??
              exampleMarks[0];
            setMarks((current) => [
              ...current,
              { ...example, id: nextId.current++ },
            ]);
          }}
        >
          {isZh
            ? `添加${labels[activeTool]}`
            : `Add ${labels[activeTool].toLowerCase()}`}
        </button>
        <button type="button" onClick={reset}>
          {isZh ? '清空' : 'Clear'}
        </button>
        <span className="snow-annotation-count" role="status">
          {shownMarks.length}
          {isZh ? ' 处标注' : ' annotations'}
        </span>
      </div>
      <div className="snow-capture-demo__footer">
        <p>
          {isZh
            ? '选择工具后，在截图上拖拽绘制。'
            : 'Choose a tool, then drag on the screenshot.'}
        </p>
        <DemoReplay
          isZh={isZh}
          playing={demo.playing}
          canResume={!manual && !demo.reducedMotion && p > 0 && p < 1}
          onPause={demo.pause}
          onResume={demo.resume}
          onReplay={() => {
            draftRef.current = null;
            setDraft(null);
            setMarks([]);
            setManual(false);
            demo.play();
          }}
        />
      </div>
    </div>
  );
}
