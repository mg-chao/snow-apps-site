import { useEffect, useState } from 'react';
import { useLang } from '@rspress/core/runtime';
import './GuideRecordingDemo.css';

const captureStepsZh = [
  ['调整录制区域', '开始前拖边框改大小，拖右下角移动控件改位置。'],
  ['开始录制', '点击开始后，按钮变为录制中的控制项。'],
  ['暂停录制', '点击暂停，整理桌面后再继续。'],
  ['继续录制', '点击继续，接着录制后续操作。'],
  ['停止录制', '点击停止，等待处理并取得输出文件。'],
];
const trimStepsZh = [
  ['进入裁剪预览', '录制中或暂停时点击裁剪，结束采集并准备时间轴。'],
  ['向右拖动起点', '去掉开头等待，画面切换到新的起始帧。'],
  ['向左拖动终点', '去掉结尾多余内容，保留区间至少一帧。'],
  ['选择播放和导出速度', '例如选择 1.5x，同时改变预览和导出的速度。'],
  ['播放检查并导出', '重播保留区间，确认后保存或复制录制文件。'],
];

export default function GuideRecordingDemo({
  mode = 'capture',
}: {
  mode?: 'capture' | 'trim';
}) {
  const en = useLang() !== 'zh';
  const t = (zh: string, english: string) => (en ? english : zh);
  const captureSteps = en
    ? [
        [
          'Adjust the recording region',
          'Before starting, resize by the border or move with the lower-right control.',
        ],
        [
          'Start recording',
          'Click Start; the controls change to the recording state.',
        ],
        ['Pause recording', 'Click Pause to prepare the next action.'],
        ['Resume recording', 'Click Resume and continue your walkthrough.'],
        [
          'Stop recording',
          'Click Stop, then wait for processing and the output file.',
        ],
      ]
    : captureStepsZh;
  const trimSteps = en
    ? [
        [
          'Open the trim preview',
          'Click Trim while recording or paused to end capture and prepare the timeline.',
        ],
        [
          'Drag the start to the right',
          'Remove the initial wait. The preview shows the new first frame.',
        ],
        [
          'Drag the end to the left',
          'Remove the unwanted ending, retaining at least one frame.',
        ],
        [
          'Set playback and export speed',
          'For example, choose 1.5x to change both preview and export speed.',
        ],
        [
          'Review and export',
          'Replay the retained interval, then save or copy the recording file.',
        ],
      ]
    : trimStepsZh;
  const steps = mode === 'trim' ? trimSteps : captureSteps;
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => {
      setStep((value) => {
        if (value >= steps.length - 1) {
          setPlaying(false);
          return value;
        }
        return value + 1;
      });
    }, 2200);
    return () => window.clearInterval(timer);
  }, [playing, steps.length]);
  useEffect(() => {
    const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    const stop = () => {
      if (preference.matches) setPlaying(false);
    };
    preference.addEventListener('change', stop);
    return () => preference.removeEventListener('change', stop);
  }, []);
  const trim = mode === 'trim';
  const first = trim && step >= 1 ? 25 : 5;
  const end = trim && step >= 2 ? 80 : 95;
  return (
    <figure className="guide-recording-demo">
      <div className="guide-recording-demo__label">
        {t('操作示意', 'Instructional illustration')}
      </div>
      <div className="guide-recording-demo__stage">
        <div className="guide-recording-demo__region">
          <span>
            {trim
              ? t('录制预览', 'Recording preview')
              : t('录制区域', 'Recording region')}
          </span>
          <div className="guide-recording-demo__content">
            {trim ? (
              <>
                <span>{t('保留区间', 'Retained interval')}</span>
                <strong>{step >= 3 ? '1.5x' : '1.0x'}</strong>
              </>
            ) : (
              <>
                <span>
                  {t(
                    '准备 → 操作 → 取得结果',
                    'Prepare → Act → Obtain the result',
                  )}
                </span>
                <strong>
                  {
                    (en
                      ? [
                          'Ready',
                          'Recording',
                          'Paused',
                          'Recording',
                          'Processing → File',
                        ]
                      : [
                          '待开始',
                          '录制中',
                          '已暂停',
                          '录制中',
                          '处理中 → 文件',
                        ])[step]
                  }
                </strong>
              </>
            )}
          </div>
        </div>
        {trim ? (
          <div className="guide-recording-demo__timeline">
            <div
              className="guide-recording-demo__selection"
              style={{ left: `${first}%`, right: `${100 - end}%` }}
            >
              <span>{t('起点', 'Start')}</span>
              <span>{t('终点', 'End')}</span>
            </div>
          </div>
        ) : (
          <div className="guide-recording-demo__states">
            {captureSteps.map(([label], index) => (
              <span key={label} data-current={index === step}>
                {index + 1}. {label}
              </span>
            ))}
          </div>
        )}
      </div>
      <p aria-live="polite">
        <strong>
          {step + 1}. {steps[step][0]}
        </strong>{' '}
        · {steps[step][1]}
      </p>
      <div className="guide-recording-demo__controls">
        <button
          type="button"
          onClick={() => {
            if (step === steps.length - 1) setStep(0);
            setPlaying(!playing);
          }}
        >
          {playing ? t('暂停演示', 'Pause demo') : t('播放演示', 'Play demo')}
        </button>
        <button
          type="button"
          onClick={() => {
            setPlaying(false);
            setStep((step + 1) % steps.length);
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
      </div>
      <figcaption>
        {t(
          '播放或逐步查看录制状态的变化。',
          'Play the sequence or inspect each recording state.',
        )}
      </figcaption>
    </figure>
  );
}
