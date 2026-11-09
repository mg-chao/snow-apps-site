import { useEffect, useId, useState } from 'react';
import { useLang } from '@rspress/core/runtime';
import './style.css';

export type GuideFrame = {
  src: string;
  alt: string;
  label: string;
  caption: string;
};

/** Source-backed instructional frames. Never presented as an app recording. */
export function GuideSteps({
  title,
  frames,
  sourceLabel,
}: {
  title: string;
  frames: GuideFrame[];
  sourceLabel?: string;
}) {
  const en = useLang() !== 'zh';
  const t = (zh: string, english: string) => (en ? english : zh);
  const id = useId();
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => {
      setStep((current) => {
        if (current === frames.length - 1) {
          setPlaying(false);
          return current;
        }
        return current + 1;
      });
    }, 2200);
    return () => window.clearInterval(timer);
  }, [playing, frames.length]);
  if (frames.length === 0) return null;
  const current = frames[step];
  return (
    <figure className="snow-guide-steps" aria-labelledby={id}>
      <figcaption id={id}>
        <strong>{title}</strong>
        <span>
          {sourceLabel ?? t('操作示意', 'Instructional illustration')}
        </span>
      </figcaption>
      <img src={current.src} alt={current.alt} width="960" height="480" />
      <p aria-live="polite">
        <strong>
          {step + 1}. {current.label}
        </strong>
        {current.caption !== current.label && <> — {current.caption}</>}
      </p>
      <div className="snow-guide-steps__controls">
        <button
          type="button"
          aria-pressed={playing}
          onClick={() => {
            if (step === frames.length - 1) setStep(0);
            setPlaying(!playing);
          }}
        >
          {playing ? t('暂停', 'Pause') : t('播放步骤', 'Play steps')}
        </button>
        <button
          type="button"
          disabled={step === 0}
          onClick={() => {
            setPlaying(false);
            setStep(step - 1);
          }}
        >
          {t('上一步', 'Previous')}
        </button>
        <button
          type="button"
          disabled={step === frames.length - 1}
          onClick={() => {
            setPlaying(false);
            setStep(step + 1);
          }}
        >
          {t('下一步', 'Next')}
        </button>
        <button
          type="button"
          onClick={() => {
            setPlaying(false);
            setStep(0);
          }}
        >
          {t('重置', 'Reset')}
        </button>
        <span>
          {step + 1} / {frames.length}
        </span>
        <a href={current.src} target="_blank" rel="noreferrer">
          {t('放大查看当前图示', 'Open full-size illustration')}
        </a>
      </div>
      <ol className="snow-guide-steps__transcript">
        {frames.map((frame, index) => (
          <li key={frame.label}>
            <button
              type="button"
              aria-current={step === index ? 'step' : undefined}
              onClick={() => {
                setPlaying(false);
                setStep(index);
              }}
            >
              {frame.label}
            </button>
            {frame.caption !== frame.label && <> — {frame.caption}</>}
          </li>
        ))}
      </ol>
    </figure>
  );
}
