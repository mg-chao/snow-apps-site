import { useEffect, useRef, useState } from 'react';
import { RecordScreenIcon, ReloadIcon } from '../HomeLayout/icons';
import { Playback, useDemo } from './shared';
import './RecordingDemo.css';

type Region = { x: number; y: number; w: number; h: number };
type Phase = 'select' | 'ready' | 'recording' | 'paused' | 'result';
const defaultRegion: Region = { x: 4, y: 8, w: 92, h: 85 };
const clamp = (n: number, min: number, max: number) =>
  Math.min(max, Math.max(min, n));
const timeLabel = (seconds: number) => {
  const total = Math.max(0, Math.floor(seconds));
  return `${Math.floor(total / 60)
    .toString()
    .padStart(2, '0')}:${(total % 60).toString().padStart(2, '0')}`;
};

function RecordingScene({ seconds, isZh }: { seconds: number; isZh: boolean }) {
  const progress = clamp((seconds - 0.5) / 4, 0, 1);
  const eased = progress * progress * (3 - 2 * progress);
  const finished = progress >= 1;
  return (
    <div className="snow-rec__scene">
      <div className="snow-rec__window-bar">
        <span className="snow-rec__window-dots" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
        <span>{isZh ? '工作流笔记' : 'Workflow notes'} / Snow Shot</span>
      </div>
      <div className="snow-rec__board-title">
        <strong>
          {isZh ? '把操作过程，讲清楚。' : 'Show how it gets done.'}
        </strong>
        <span>
          {isZh ? '产品演示 · 今日计划' : 'Product walkthrough · Today'}
        </span>
      </div>
      <div className="snow-rec__columns">
        {[
          isZh ? '待开始' : 'To do',
          isZh ? '进行中' : 'In progress',
          isZh ? '已完成' : 'Done',
        ].map((label, i) => (
          <div className="snow-rec__column" key={label}>
            <div>
              <span>{label}</span>
              <b>
                {i === 0
                  ? finished
                    ? '0'
                    : '1'
                  : i === 2 && finished
                    ? '1'
                    : '0'}
              </b>
            </div>
          </div>
        ))}
      </div>
      <div
        className="snow-rec__moving-card"
        style={{
          left: `${6 + eased * 60}%`,
          top: `${48 - Math.sin(progress * Math.PI) * 5}%`,
        }}
      >
        <span>{isZh ? '操作说明' : 'WALKTHROUGH'}</span>
        <strong>{isZh ? '整理录屏指南' : 'Prepare recording guide'}</strong>
        <small>{isZh ? '选区 → 录制 → 分享' : 'Select → Record → Share'}</small>
        <div className="snow-rec__task-progress">
          <i style={{ width: `${progress * 100}%` }} />
        </div>
      </div>
      <div
        className="snow-rec__cursor"
        aria-hidden="true"
        style={{
          left: `${26 + eased * 60}%`,
          top: `${72 - Math.sin(progress * Math.PI) * 5}%`,
        }}
      />
      <div className="snow-rec__scene-note">
        {finished
          ? isZh
            ? '✓ 指南已完成'
            : '✓ Guide completed'
          : isZh
            ? '把任务从「待开始」移到「已完成」'
            : 'Move the task from To do to Done'}
      </div>
    </div>
  );
}

export function ScreenRecordingDemo({ isZh }: { isZh: boolean }) {
  const demo = useDemo({ duration: 10500 });
  const [manual, setManual] = useState(false);
  const [phase, setPhase] = useState<Phase>('select');
  const [region, setRegion] = useState<Region | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [savedDuration, setSavedDuration] = useState(0);
  const [previewTime, setPreviewTime] = useState(0);
  const [replaying, setReplaying] = useState(false);
  const replayPosition = useRef(0);
  const drag = useRef<{ x: number; y: number } | null>(null);
  const canvasRef = useRef<HTMLButtonElement>(null);
  const p = demo.progress;
  const autoPhase: Phase =
    p < 0.21
      ? 'select'
      : p < 0.43
        ? 'recording'
        : p < 0.53
          ? 'paused'
          : p < 0.83
            ? 'recording'
            : 'result';
  const activePhase = manual ? phase : autoPhase;
  const autoElapsed =
    clamp((Math.min(p, 0.43) - 0.21) * 10.5, 0, 2.31) +
    clamp((p - 0.53) * 10.5, 0, 3.15);
  const activeElapsed = manual ? elapsed : autoElapsed;
  const activeDuration = manual ? savedDuration : 5.46;
  const activeRegion = manual
    ? region
    : p < 0.055
      ? null
      : {
          x: 4,
          y: 8,
          w: 92 * clamp((p - 0.055) / 0.12, 0.03, 1),
          h: 85 * clamp((p - 0.055) / 0.12, 0.03, 1),
        };
  const sceneSeconds =
    activePhase === 'result' && manual ? previewTime : activeElapsed;
  const labels: Record<Phase, string> = {
    select: isZh ? '选择录制区域' : 'Select a recording region',
    ready: isZh ? '选区就绪' : 'Region ready',
    recording: isZh ? '正在录制' : 'Recording',
    paused: isZh ? '录制已暂停' : 'Recording paused',
    result: isZh ? '录制结果预览' : 'Recording preview',
  };

  useEffect(() => {
    if (
      !manual ||
      !demo.visible ||
      (phase !== 'recording' && !(phase === 'result' && replaying))
    )
      return;
    let frame = 0;
    let last = performance.now();
    const tick = (now: number) => {
      const dt = Math.min((now - last) / 1000, 0.1);
      last = now;
      if (phase === 'recording') setElapsed((value) => value + dt);
      else {
        replayPosition.current = Math.min(
          savedDuration,
          replayPosition.current + dt,
        );
        setPreviewTime(replayPosition.current);
        if (replayPosition.current >= savedDuration) setReplaying(false);
      }
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [manual, phase, replaying, savedDuration, demo.visible]);

  useEffect(() => {
    const pauseForAnotherDemo = () => {
      if (manual && phase === 'recording') setPhase('paused');
      setReplaying(false);
    };
    window.addEventListener('snow-demo-play', pauseForAnotherDemo);
    const yieldToAnotherDemo = (event: Event) => {
      if (
        (event as CustomEvent<HTMLElement>).detail !== demo.containerRef.current
      )
        pauseForAnotherDemo();
    };
    window.addEventListener('snow-demo-claim', yieldToAnotherDemo);
    return () => {
      window.removeEventListener('snow-demo-play', pauseForAnotherDemo);
      window.removeEventListener('snow-demo-claim', yieldToAnotherDemo);
    };
  }, [manual, phase, demo.containerRef]);

  const takeControl = () => {
    demo.interact();
    if (!manual) {
      setManual(true);
      setPhase(activePhase);
      setRegion(activeRegion);
      setElapsed(activeElapsed);
      setSavedDuration(activeDuration);
      setPreviewTime(activeElapsed);
    }
  };
  const selectPreset = () => {
    takeControl();
    setRegion(defaultRegion);
    setPhase('ready');
    setElapsed(0);
    setReplaying(false);
  };
  const reset = () => {
    demo.reset();
    setManual(true);
    setPhase('select');
    setRegion(null);
    setElapsed(0);
    setPreviewTime(0);
    setSavedDuration(0);
    setReplaying(false);
    drag.current = null;
  };
  const point = (clientX: number, clientY: number) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    return rect
      ? {
          x: clamp(((clientX - rect.left) / rect.width) * 100, 0, 100),
          y: clamp(((clientY - rect.top) / rect.height) * 100, 0, 100),
        }
      : { x: 0, y: 0 };
  };

  return (
    <div className="snow-demo snow-rec" ref={demo.containerRef}>
      <div className="snow-demo-titlebar">
        <RecordScreenIcon />
        <span>{isZh ? '屏幕录制' : 'Screen recording'}</span>
        <span
          className={`snow-demo-badge snow-rec__status snow-rec__status--${activePhase}`}
        >
          <i />
          {labels[activePhase]}{' '}
          <b>
            {timeLabel(
              activePhase === 'result' ? activeDuration : activeElapsed,
            )}
          </b>
        </span>
      </div>
      <button
        type="button"
        ref={canvasRef}
        className={`snow-rec__canvas ${activePhase === 'result' ? 'snow-rec__canvas--result' : ''}`}
        aria-label={
          isZh
            ? '录制画面。拖动选择区域，或按 Enter 选择示例区域；方向键移动选区。'
            : 'Recording scene. Drag to select, or press Enter for a sample region; arrow keys move the region.'
        }
        onPointerDown={(event) => {
          takeControl();
          if (activePhase !== 'select' && activePhase !== 'ready') return;
          setPhase('select');
          const start = point(event.clientX, event.clientY);
          drag.current = start;
          setRegion({ ...start, w: 0, h: 0 });
          event.currentTarget.setPointerCapture(event.pointerId);
        }}
        onPointerMove={(event) => {
          if (!drag.current) return;
          const next = point(event.clientX, event.clientY);
          setRegion({
            x: Math.min(drag.current.x, next.x),
            y: Math.min(drag.current.y, next.y),
            w: Math.abs(next.x - drag.current.x),
            h: Math.abs(next.y - drag.current.y),
          });
        }}
        onPointerUp={(event) => {
          if (!drag.current) return;
          const end = point(event.clientX, event.clientY);
          const completed = {
            x: Math.min(drag.current.x, end.x),
            y: Math.min(drag.current.y, end.y),
            w: Math.abs(end.x - drag.current.x),
            h: Math.abs(end.y - drag.current.y),
          };
          drag.current = null;
          setRegion(
            completed.w < 15 || completed.h < 20 ? defaultRegion : completed,
          );
          setPhase('ready');
          if (event.currentTarget.hasPointerCapture(event.pointerId))
            event.currentTarget.releasePointerCapture(event.pointerId);
        }}
        onPointerCancel={() => {
          if (!drag.current) return;
          drag.current = null;
          setPhase('ready');
          setRegion(defaultRegion);
        }}
        onKeyDown={(event) => {
          if (event.key === 'Tab') return;
          takeControl();
          if (activePhase !== 'select' && activePhase !== 'ready') return;
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            selectPreset();
            return;
          }
          if (
            !event.key.startsWith('Arrow') ||
            (activePhase !== 'select' && activePhase !== 'ready')
          )
            return;
          event.preventDefault();
          takeControl();
          setPhase('ready');
          const current = activeRegion ?? defaultRegion;
          setRegion({
            ...current,
            x: clamp(
              current.x +
                (event.key === 'ArrowLeft'
                  ? -2
                  : event.key === 'ArrowRight'
                    ? 2
                    : 0),
              0,
              100 - current.w,
            ),
            y: clamp(
              current.y +
                (event.key === 'ArrowUp'
                  ? -2
                  : event.key === 'ArrowDown'
                    ? 2
                    : 0),
              0,
              100 - current.h,
            ),
          });
        }}
      >
        <div
          className="snow-rec__capture-content"
          style={
            activePhase === 'result' && activeRegion
              ? {
                  clipPath: `inset(${activeRegion.y}% ${100 - activeRegion.x - activeRegion.w}% ${100 - activeRegion.y - activeRegion.h}% ${activeRegion.x}%)`,
                }
              : undefined
          }
        >
          <RecordingScene
            seconds={
              demo.reducedMotion ? Math.floor(sceneSeconds) : sceneSeconds
            }
            isZh={isZh}
          />
        </div>
        {activeRegion && (
          <div
            className="snow-rec__region"
            style={{
              left: `${activeRegion.x}%`,
              top: `${activeRegion.y}%`,
              width: `${activeRegion.w}%`,
              height: `${activeRegion.h}%`,
            }}
          >
            <span style={activeRegion.y < 8 ? { top: 5, left: 5 } : undefined}>
              {Math.round(activeRegion.w * 8)} ×{' '}
              {Math.round(activeRegion.h * 4.5)}
            </span>
            <i />
            <i />
            <i />
            <i />
          </div>
        )}
        {!manual && demo.playing && p < 0.21 && (
          <div
            className="snow-rec__selection-cursor"
            aria-hidden="true"
            style={{
              left: `${4 + (activeRegion?.w ?? 0)}%`,
              top: `${8 + (activeRegion?.h ?? 0)}%`,
            }}
          />
        )}
        {!activeRegion && (
          <span className="snow-rec__select-hint">
            {isZh
              ? '在画面内拖动，选择录制区域'
              : 'Drag within the scene to select a region'}
          </span>
        )}
      </button>
      <div className="snow-demo-controls">
        {(activePhase === 'select' || activePhase === 'ready') && (
          <>
            <button
              type="button"
              className="snow-demo-button"
              onClick={selectPreset}
            >
              {isZh ? '选择示例区域' : 'Use sample region'}
            </button>
            <button
              type="button"
              className="snow-demo-button snow-demo-button--primary"
              disabled={
                !activeRegion || activeRegion.w < 15 || activeRegion.h < 20
              }
              onClick={() => {
                takeControl();
                setElapsed(0);
                setPhase('recording');
              }}
            >
              {isZh ? '开始录制' : 'Start recording'}
            </button>
          </>
        )}
        {(activePhase === 'recording' || activePhase === 'paused') && (
          <>
            <button
              type="button"
              className="snow-demo-button"
              onClick={() => {
                takeControl();
                setPhase(activePhase === 'recording' ? 'paused' : 'recording');
              }}
            >
              {activePhase === 'recording'
                ? isZh
                  ? '暂停录制'
                  : 'Pause recording'
                : isZh
                  ? '继续录制'
                  : 'Resume recording'}
            </button>
            <button
              type="button"
              className="snow-demo-button snow-demo-button--primary"
              onClick={() => {
                takeControl();
                setPhase('result');
                setSavedDuration(activeElapsed);
                setPreviewTime(activeElapsed);
                setReplaying(false);
              }}
            >
              {isZh ? '停止并查看' : 'Stop & preview'}
            </button>
          </>
        )}
        {activePhase === 'result' && (
          <button
            type="button"
            className="snow-demo-button snow-demo-button--primary"
            onClick={() => {
              takeControl();
              if (manual && replaying) setReplaying(false);
              else {
                replayPosition.current = 0;
                setPreviewTime(0);
                setReplaying(true);
              }
            }}
          >
            {manual && replaying
              ? isZh
                ? '暂停播放'
                : 'Pause playback'
              : isZh
                ? '播放录制结果'
                : 'Play recording'}
          </button>
        )}
        <button
          type="button"
          className="snow-demo-button snow-rec__reset"
          onClick={reset}
          aria-label={isZh ? '重置录屏' : 'Reset recording'}
        >
          <ReloadIcon />
        </button>
      </div>
      <div className="snow-rec__timeline">
        {activePhase === 'result' ? (
          <>
            <label htmlFor={`recording-timeline-${isZh ? 'zh' : 'en'}`}>
              {isZh ? '结果时间轴' : 'Preview timeline'}
            </label>
            <input
              id={`recording-timeline-${isZh ? 'zh' : 'en'}`}
              type="range"
              min="0"
              max={Math.max(activeDuration, 0.01)}
              step="0.01"
              value={manual ? previewTime : activeDuration}
              onChange={(event) => {
                takeControl();
                setReplaying(false);
                setPreviewTime(Number(event.currentTarget.value));
              }}
            />
            <span>
              {timeLabel(manual ? previewTime : activeDuration)} /{' '}
              {timeLabel(activeDuration)}
            </span>
          </>
        ) : (
          <p>
            {activePhase === 'paused'
              ? isZh
                ? '计时与画面活动已一起暂停。点击继续，从原处接上。'
                : 'The timer and scene are both paused. Resume exactly where you left off.'
              : isZh
                ? '体验选区、录制、暂停与回放。此处为模拟演示，不会录制你的屏幕。'
                : 'Try selecting, recording, pausing and replaying. This demo does not record your screen.'}
          </p>
        )}
      </div>
      <div className="snow-demo-footer">
        <span>{isZh ? '选区 → 录制 → 回放' : 'Select → record → replay'}</span>
        <Playback
          demo={demo}
          isZh={isZh}
          active={!manual}
          onReplay={() => {
            setManual(false);
            setReplaying(false);
            demo.play();
          }}
        />
      </div>
      <span className="snow-rec__announcement" aria-live="polite">
        {labels[activePhase]}
      </span>
    </div>
  );
}
