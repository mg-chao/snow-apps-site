import {
  type SyntheticEvent,
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
} from 'react';
import { ReloadIcon, ScreenshotCopyIcon } from '../HomeLayout/icons';

/** A single, cancellable clock for each product workflow. No desktop APIs are used. */
export function useDemo({
  duration,
  autoplay = true,
}: {
  duration: number;
  autoplay?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const id = useId();
  const [progress, setProgress] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [visible, setVisible] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const elapsed = useRef(0);
  const interacted = useRef(false);
  const started = useRef(false);
  const reduce = useRef(false);
  const pause = useCallback(() => setPlaying(false), []);
  const interact = useCallback((event?: SyntheticEvent) => {
    interacted.current = true;
    // Playback controls own their clock. A capture handler must not pause it
    // before the Pause button receives its click and changes into Resume.
    if ((event?.target as Element | undefined)?.closest('.snow-demo-playback'))
      return;
    window.dispatchEvent(
      new CustomEvent('snow-demo-claim', { detail: containerRef.current }),
    );
    setPlaying(false);
  }, []);
  const play = useCallback(() => {
    started.current = true;
    elapsed.current = 0;
    window.dispatchEvent(new CustomEvent('snow-demo-play', { detail: id }));
    setProgress(reduce.current ? 1 : 0);
    setPlaying(!reduce.current);
  }, [id]);
  const resume = useCallback(() => {
    window.dispatchEvent(new CustomEvent('snow-demo-play', { detail: id }));
    setPlaying(!reduce.current && elapsed.current < duration);
  }, [duration, id]);
  const reset = useCallback(() => {
    interacted.current = true;
    elapsed.current = 0;
    setProgress(0);
    setPlaying(false);
  }, []);

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => {
      reduce.current = media.matches;
      setReducedMotion(media.matches);
      if (media.matches) setPlaying(false);
    };
    update();
    media.addEventListener('change', update);
    let inView = false;
    let enoughForAutoplay = false;
    const visibility = () => {
      const next = inView && !document.hidden;
      setVisible(next);
      if (!next) setPlaying(false);
      else if (
        autoplay &&
        enoughForAutoplay &&
        !started.current &&
        !interacted.current &&
        !reduce.current
      )
        play();
    };
    const observer = new IntersectionObserver(
      ([entry]) => {
        // A stacked mobile panel can be taller than the viewport. Keep manual
        // work active while any part is visible; use a larger area for autoplay.
        inView = entry.isIntersecting;
        enoughForAutoplay =
          entry.intersectionRect.height >=
          Math.min(
            entry.boundingClientRect.height * 0.5,
            (entry.rootBounds?.height ?? window.innerHeight) * 0.45,
          );
        visibility();
      },
      { threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1] },
    );
    if (containerRef.current) observer.observe(containerRef.current);
    document.addEventListener('visibilitychange', visibility);
    const otherDemo = (event: Event) => {
      if ((event as CustomEvent<string>).detail !== id) setPlaying(false);
    };
    const otherInteraction = (event: Event) => {
      if ((event as CustomEvent<HTMLElement>).detail !== containerRef.current)
        setPlaying(false);
    };
    window.addEventListener('snow-demo-play', otherDemo);
    window.addEventListener('snow-demo-claim', otherInteraction);
    return () => {
      observer.disconnect();
      media.removeEventListener('change', update);
      document.removeEventListener('visibilitychange', visibility);
      window.removeEventListener('snow-demo-play', otherDemo);
      window.removeEventListener('snow-demo-claim', otherInteraction);
    };
  }, [autoplay, id, play]);

  useEffect(() => {
    if (!playing) return;
    let previous = performance.now();
    const timer = window.setInterval(() => {
      const now = performance.now();
      elapsed.current = Math.min(duration, elapsed.current + now - previous);
      previous = now;
      setProgress(elapsed.current / duration);
      if (elapsed.current >= duration) setPlaying(false);
    }, 40);
    return () => window.clearInterval(timer);
  }, [duration, playing]);

  return {
    containerRef,
    progress,
    playing,
    visible,
    reducedMotion,
    play,
    pause,
    resume,
    interact,
    reset,
  };
}

export type DemoController = ReturnType<typeof useDemo>;

export function Playback({
  demo,
  isZh,
  onReplay = demo.play,
  active = true,
}: {
  demo: DemoController;
  isZh: boolean;
  onReplay?: () => void;
  active?: boolean;
}) {
  return (
    <div className="snow-demo-playback">
      <button type="button" className="snow-demo-button" onClick={onReplay}>
        <ReloadIcon />
        {isZh ? '重播演示' : 'Replay demo'}
      </button>
      {active &&
        !demo.reducedMotion &&
        demo.progress > 0 &&
        demo.progress < 1 && (
          <button
            type="button"
            className="snow-demo-button"
            onClick={demo.playing ? demo.pause : demo.resume}
          >
            {demo.playing
              ? isZh
                ? '暂停演示'
                : 'Pause demo'
              : isZh
                ? '继续演示'
                : 'Resume demo'}
          </button>
        )}
    </div>
  );
}

export function CopyButton({
  value,
  isZh,
  disabled = false,
}: {
  value: string;
  isZh: boolean;
  disabled?: boolean;
}) {
  const [status, setStatus] = useState<
    'idle' | 'copying' | 'success' | 'error'
  >('idle');
  const request = useRef(0);
  const previous = useRef(value);
  useEffect(() => {
    return () => {
      request.current += 1;
    };
  }, []);
  // A new recognition run or mode must not inherit earlier success feedback.
  useEffect(() => {
    if (disabled || previous.current !== value) {
      request.current += 1;
      setStatus('idle');
    }
    previous.current = value;
  }, [disabled, value]);
  async function copy() {
    const ticket = ++request.current;
    setStatus('copying');
    try {
      if (!navigator.clipboard?.writeText)
        throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(value);
      if (ticket === request.current) setStatus('success');
    } catch {
      if (ticket === request.current) setStatus('error');
    }
  }
  return (
    <div className="snow-demo-copy">
      <button
        type="button"
        className="snow-demo-button"
        onClick={copy}
        disabled={disabled || status === 'copying'}
      >
        <ScreenshotCopyIcon />
        {status === 'success'
          ? isZh
            ? '已复制'
            : 'Copied'
          : status === 'copying'
            ? isZh
              ? '正在复制'
              : 'Copying'
            : isZh
              ? '复制结果'
              : 'Copy result'}
      </button>
      <span role="status">
        {status === 'error'
          ? isZh
            ? '复制失败，请选中文字手动复制。'
            : 'Copy failed. Select the text to copy manually.'
          : status === 'success'
            ? isZh
              ? '结果已写入剪贴板。'
              : 'Result copied to clipboard.'
            : ''}
      </span>
    </div>
  );
}

export function SampleNote({
  isZh,
  compact = false,
}: {
  isZh: boolean;
  compact?: boolean;
}) {
  return (
    <div
      className={`snow-demo-note${compact ? ' snow-demo-note--compact' : ''}`}
    >
      <div className="snow-demo-note__label">
        SNOW SHOT / {isZh ? '发布检查清单' : 'RELEASE CHECKLIST'}
      </div>
      <h4>{isZh ? '把想法，讲清楚。' : 'Make your point clear.'}</h4>
      <p>
        {isZh
          ? '一张截图，让沟通少一点来回。'
          : 'A screenshot keeps everyone on the same page.'}
      </p>
      <ul>
        <li>
          {isZh ? '截取需要讨论的区域' : 'Capture the part worth discussing'}
        </li>
        <li>
          {isZh
            ? '用箭头指明需要修改的位置'
            : 'Point to the change with an arrow'}
        </li>
        <li>
          {isZh ? '复制结果，发给协作伙伴' : 'Copy the result and share it'}
        </li>
      </ul>
      <div className="snow-demo-note__bottom">
        <span>{isZh ? '设计评审' : 'Design review'}</span>
        <strong>{isZh ? '准备分享' : 'Ready to share'}</strong>
      </div>
    </div>
  );
}
