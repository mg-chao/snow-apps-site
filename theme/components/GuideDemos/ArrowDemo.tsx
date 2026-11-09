import { useEffect, useId, useState } from 'react';
import { useLang } from '@rspress/core/runtime';
import './AnnotationDemos.css';

const stepsZh = [
  '初始：在标注工具条选择“箭头”，在样式条选择曲线箭头。',
  '创建：在起点按住左键，拖到目标位置后松开。',
  '选中：切换“选择元素”，点击箭头；端点与中间控制点出现。',
  '修改：拖动中间控制点，改变路径的弯曲方向与幅度。',
  '完成：点击空白处取消选中，再复制或保存整个截图。',
];

export function ArrowDemo() {
  const en = useLang() !== 'zh';
  const t = (zh: string, english: string) => (en ? english : zh);
  const steps = en
    ? [
        'Prepare: select Arrow in the annotation toolbar, then choose a curved arrow in its style bar.',
        'Create: hold the left button at the start, drag to the target and release.',
        'Select: switch to Select element and click the arrow. Endpoint and middle handles appear.',
        'Edit: drag the middle handle to adjust the direction and amount of curvature.',
        'Finish: click blank space to deselect, then copy or save the whole screenshot.',
      ]
    : stepsZh;
  const marker = useId().replace(/:/g, '');
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [kind, setKind] = useState('curve');
  const [bend, setBend] = useState(95);
  const [width, setWidth] = useState(5);
  const [both, setBoth] = useState(false);
  const currentStep =
    step === 2 && kind !== 'curve'
      ? t(
          kind === 'straight'
            ? '选中：切换“选择元素”，点击箭头；两端控制点出现。'
            : '选中：切换“选择元素”，点击箭头；端点与折线控制点出现。',
          kind === 'straight'
            ? 'Select: switch to Select elements and click the arrow to reveal its endpoint handles.'
            : 'Select: switch to Select elements and click the arrow to reveal endpoints and elbow handles.',
        )
      : step === 3 && kind !== 'curve'
        ? t(
            kind === 'straight'
              ? '修改：拖动端点改变方向；下方可比较线宽与双端箭头。'
              : '修改：调整折线控制段改变绕行；下方可比较线宽与双端箭头。',
            kind === 'straight'
              ? 'Edit: move an endpoint to change direction. Compare line width and arrowheads below.'
              : 'Edit: adjust the elbow segment to change routing. Compare line width and arrowheads below.',
          )
        : steps[step];
  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => {
      setStep((previous) => {
        if (previous >= steps.length - 1) {
          setPlaying(false);
          return previous;
        }
        return previous + 1;
      });
    }, 1800);
    return () => window.clearInterval(timer);
  }, [playing, steps.length]);
  const middleY = step >= 3 ? bend : 202.5;
  const path =
    kind === 'straight'
      ? 'M100 235 L470 170'
      : kind === 'elbow'
        ? 'M100 235 H280 V170 H470'
        : `M100 235 Q285 ${2 * middleY - 202.5} 470 170`;
  return (
    <figure className="guide-operation-demo">
      <div className="guide-operation-demo__label">
        {t(
          '箭头控制点 · 教学演示',
          'Arrow control points · Instructional demo',
        )}
      </div>
      <svg
        viewBox="0 0 580 310"
        role="img"
        aria-label={t(
          '箭头从左下指向右上，选中后显示端点和中间控制点；调节下方控件可比较路径和线宽',
          'An arrow points from lower left to upper right. Selection reveals endpoint and middle handles. Use the controls to compare paths and line widths.',
        )}
      >
        <defs>
          <marker
            id={`${marker}-end`}
            viewBox="0 0 12 12"
            refX="10"
            refY="6"
            markerWidth="4"
            markerHeight="4"
            orient="auto-start-reverse"
          >
            <path
              d="M1 1 L11 6 L1 11"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            />
          </marker>
        </defs>
        <rect
          x="25"
          y="30"
          width="530"
          height="255"
          rx="14"
          className="guide-operation-demo__paper"
        />
        <text x="52" y="70" className="guide-operation-demo__text">
          {t(
            '为图像中的一个细节添加指向说明',
            'Point out a detail in the image',
          )}
        </text>
        <rect
          x="420"
          y="125"
          width="85"
          height="70"
          rx="8"
          className="guide-operation-demo__target"
        />
        <text x="443" y="165" className="guide-operation-demo__text">
          {t('目标', 'Target')}
        </text>
        {step > 0 && (
          <path
            d={path}
            fill="none"
            stroke="currentColor"
            strokeWidth={width}
            strokeLinecap="round"
            markerEnd={`url(#${marker}-end)`}
            markerStart={both ? `url(#${marker}-end)` : undefined}
          />
        )}
        {step >= 2 && step < 4 && (
          <g>
            <circle
              cx="100"
              cy="235"
              r="7"
              className="guide-operation-demo__handle"
            />
            <circle
              cx="470"
              cy="170"
              r="7"
              className="guide-operation-demo__handle"
            />
            {kind === 'curve' && (
              <>
                <path
                  d={`M285 202.5 L285 ${middleY}`}
                  fill="none"
                  stroke="currentColor"
                  strokeDasharray="4 6"
                  opacity=".35"
                />
                <circle
                  cx="280"
                  cy={middleY}
                  r="8"
                  className="guide-operation-demo__handle"
                />
                <text
                  x="295"
                  y={middleY - 10}
                  className="guide-operation-demo__text"
                >
                  {t('中间控制点', 'Middle control point')}
                </text>
              </>
            )}
            {kind === 'elbow' && (
              <circle
                cx="280"
                cy="203"
                r="8"
                className="guide-operation-demo__handle"
              />
            )}
          </g>
        )}
        <circle
          cx="100"
          cy="235"
          r="18"
          fill="none"
          stroke="currentColor"
          strokeDasharray="3 3"
          opacity={step === 0 ? '.7' : '0'}
        />
      </svg>
      <p className="guide-operation-demo__status" aria-live="polite">
        {step + 1} / {steps.length}　{currentStep}
      </p>
      <div className="guide-operation-demo__controls">
        <button
          type="button"
          onClick={() => {
            if (step === 4) setStep(0);
            setPlaying(!playing);
          }}
        >
          {playing ? t('暂停演示', 'Pause demo') : t('播放演示', 'Play demo')}
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
          disabled={step === 4}
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
            setKind('curve');
            setBend(95);
            setWidth(5);
            setBoth(false);
          }}
        >
          {t('重置', 'Reset')}
        </button>
      </div>
      <div className="guide-operation-demo__controls">
        <label>
          {t('路径', 'Path')}{' '}
          <select
            value={kind}
            onChange={(event) => {
              setKind(event.target.value);
              setStep(3);
            }}
          >
            <option value="straight">{t('直线', 'Straight')}</option>
            <option value="curve">{t('曲线', 'Curved')}</option>
            <option value="elbow">{t('折线', 'Elbow')}</option>
          </select>
        </label>
        <label>
          {t('弯曲幅度', 'Curvature')}{' '}
          <input
            type="range"
            min="60"
            max="270"
            value={bend}
            disabled={kind !== 'curve'}
            onChange={(event) => {
              setBend(Number(event.target.value));
              setStep(3);
            }}
          />
        </label>
        <label>
          {t('线宽', 'Line width')}{' '}
          <input
            type="range"
            min="2"
            max="10"
            value={width}
            onChange={(event) => {
              setWidth(Number(event.target.value));
              setStep(Math.max(1, step));
            }}
          />
        </label>
        <label>
          <input
            type="checkbox"
            checked={both}
            onChange={(event) => {
              setBoth(event.target.checked);
              setStep(Math.max(1, step));
            }}
          />{' '}
          {t('双端箭头', 'Both ends')}
        </label>
      </div>
      <figcaption>
        {t(
          '拖动控制点或调整下方选项，比较箭头路径和线宽。',
          'Use the controls below to compare arrow paths and line widths.',
        )}
      </figcaption>
    </figure>
  );
}
