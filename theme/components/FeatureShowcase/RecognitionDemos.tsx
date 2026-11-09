import {
  type CSSProperties,
  type KeyboardEvent,
  useId,
  useRef,
  useState,
} from 'react';
import { RecognizeTextIcon } from '../HomeLayout/icons';
import { CopyButton, Playback, useDemo } from './shared';
import './RecognitionDemos.css';

const repository = 'https://github.com/mg-chao/snow-shot';
const latex = String.raw`\int_0^1 x^2\,dx = \frac{1}{3}`;

function phase(progress: number) {
  return progress === 0 ? 0 : progress < 0.26 ? 1 : progress < 0.62 ? 2 : 3;
}

function RecognitionStatus({
  progress,
  isZh,
  mode = 'text',
}: {
  progress: number;
  isZh: boolean;
  mode?: string;
}) {
  const stage = phase(progress);
  const stages = isZh
    ? [
        '等待识别',
        '检测内容区域',
        mode === 'qr'
          ? '解码二维码'
          : mode === 'table'
            ? '重建行与列'
            : mode === 'latex'
              ? '解析数学结构'
              : mode === 'markdown'
                ? '整理标题与列表'
                : '识别文字',
        '识别完成',
      ]
    : [
        'Ready to recognize',
        'Detecting regions',
        mode === 'qr'
          ? 'Decoding the QR code'
          : mode === 'table'
            ? 'Rebuilding rows & columns'
            : mode === 'latex'
              ? 'Parsing the formula'
              : mode === 'markdown'
                ? 'Structuring the document'
                : 'Recognizing text',
        'Recognition complete',
      ];
  return (
    <div className="snow-recognition__status">
      <span
        className={`snow-recognition__status-dot ${stage === 3 ? 'is-complete' : ''}`}
      />
      <span role="status">{stages[stage]}</span>
      <span className="snow-recognition__step">
        {stage === 0 ? '00' : `0${stage}`} / 03
      </span>
      <progress
        max={1}
        value={Math.min(1, progress / 0.62)}
        aria-label={isZh ? '识别进度' : 'Recognition progress'}
      />
    </div>
  );
}

function SourceImage({
  src,
  alt,
  progress,
  isZh,
  mode,
}: {
  src: string;
  alt: string;
  progress: number;
  isZh: boolean;
  mode: string;
}) {
  const stage = phase(progress);
  const scanning = stage === 1 || stage === 2;
  return (
    <div
      className={`snow-recognition__source snow-recognition__source--${mode}`}
      data-scanning={scanning}
      data-detected={stage > 0}
    >
      <span className="snow-recognition__panel-label">
        {isZh ? '原始图片' : 'SOURCE IMAGE'}
      </span>
      <div className="snow-recognition__image">
        <img src={src} alt={alt} width={560} height={370} draggable={false} />
        <div className="snow-recognition__regions" aria-hidden="true">
          <i />
          <i />
          <i />
          <i />
        </div>
        <div
          className="snow-recognition__scan"
          aria-hidden="true"
          style={
            {
              '--scan-position': `${Math.max(0, Math.min(1, (progress - 0.05) / 0.57)) * 100}%`,
            } as CSSProperties
          }
        />
      </div>
      <span className="snow-recognition__image-note">
        {isZh ? '示例图片' : 'Sample image'} · 560 × 370
      </span>
    </div>
  );
}

function RecognitionHeader({
  title,
  isZh,
  onRecognize,
}: {
  title: string;
  isZh: boolean;
  onRecognize: () => void;
}) {
  return (
    <div className="snow-recognition__header">
      <div className="snow-recognition__brand">
        <img src="/images/app-icon.webp" alt="" width={22} height={22} />
        <span>
          Snow Shot{' '}
          <span className="snow-recognition__brand-detail"> / {title}</span>
        </span>
      </div>
      <button
        type="button"
        className="snow-recognition__action"
        onClick={onRecognize}
      >
        <RecognizeTextIcon />
        {isZh ? '识别' : 'Recognize'}
      </button>
    </div>
  );
}

export function TextRecognitionDemo({ isZh }: { isZh: boolean }) {
  const demo = useDemo({ duration: 7600 / 6 });
  const ready = phase(demo.progress) === 3;
  const text = isZh
    ? '每一次截图，都有用\n周五 14:00 · 产品评审\n准备：截图、标注与分享。'
    : 'Every capture, ready to use.\nFriday 14:00 · Product review\nPrepare: capture, annotate, share.';
  return (
    <div
      className="snow-demo snow-recognition"
      ref={demo.containerRef}
      onPointerDownCapture={demo.interact}
      onKeyDownCapture={demo.interact}
      data-demo="text-recognition"
    >
      <RecognitionHeader
        title={isZh ? '文本识别' : 'Text recognition'}
        isZh={isZh}
        onRecognize={demo.play}
      />
      <div className="snow-recognition__workbench">
        <SourceImage
          src={`/images/demos/recognition-text-${isZh ? 'zh' : 'en'}.svg`}
          alt={text}
          progress={demo.progress}
          isZh={isZh}
          mode="text"
        />
        <div className="snow-recognition__output" data-ready={ready}>
          <div className="snow-recognition__output-heading">
            <span className="snow-recognition__panel-label">
              {isZh ? '识别文本' : 'RECOGNIZED TEXT'}
            </span>
            <CopyButton value={text} isZh={isZh} disabled={!ready} />
          </div>
          <div className="snow-recognition__result-space">
            {!ready && (
              <div className="snow-recognition__waiting">
                <RecognizeTextIcon />
                <p>
                  {isZh ? '从图片中提取文字' : 'Your image, as editable text.'}
                </p>
                <span>
                  {isZh
                    ? '点击「识别」查看过程'
                    : 'Choose Recognize to see the process.'}
                </span>
              </div>
            )}
            <div className="snow-recognition__text-result" aria-hidden={!ready}>
              {text.split('\n').map((line, index) => (
                <p
                  key={line}
                  style={{ '--result-order': index } as CSSProperties}
                >
                  {line}
                </p>
              ))}
              <span className="snow-recognition__select-hint">
                {isZh
                  ? '可选中、复制，直接用于下一步工作。'
                  : 'Select it. Copy it. Make it part of your work.'}
              </span>
            </div>
          </div>
        </div>
      </div>
      <RecognitionStatus progress={demo.progress} isZh={isZh} />
      <div className="snow-recognition__footer">
        <span>
          {isZh
            ? '交互演示 · 使用固定样例模拟本地文本识别'
            : 'Interactive demo · simulated local text recognition with a fixed sample'}
        </span>
        <Playback demo={demo} isZh={isZh} />
      </div>
    </div>
  );
}

const modes = ['table', 'latex', 'qr', 'markdown'] as const;
type Mode = (typeof modes)[number];

function tableRows(isZh: boolean) {
  return isZh
    ? [
        ['任务', '负责人', '状态'],
        ['界面评审', '林', '已完成'],
        ['截图说明', '陈', '进行中'],
        ['使用指南', '周', '待开始'],
      ]
    : [
        ['Task', 'Owner', 'Status'],
        ['Interface review', 'Lin', 'Done'],
        ['Screenshot notes', 'Chen', 'In progress'],
        ['User guide', 'Zhou', 'Next'],
      ];
}

function markdownContent(isZh: boolean) {
  return isZh
    ? '# SnowShot 工作流\n\n把想法清楚地分享出去。\n\n- 截取关键区域\n- 标注需要关注的细节\n- 复制并分享'
    : '# SnowShot workflow\n\nShare your ideas clearly.\n\n- Capture a focused region\n- Annotate the important details\n- Copy and share';
}

function Formula({ isZh }: { isZh: boolean }) {
  return (
    <div
      className="snow-recognition__formula"
      role="img"
      aria-label={
        isZh
          ? '从零到一对 x 的平方积分，结果等于三分之一'
          : 'Integral from zero to one of x squared dx equals one third'
      }
    >
      <span className="snow-recognition__integral">
        <sup>1</sup>
        <span>∫</span>
        <sub>0</sub>
      </span>
      <span>
        x<sup className="snow-recognition__power">2</sup> dx =
      </span>
      <span className="snow-recognition__fraction">
        <span>1</span>
        <span>3</span>
      </span>
    </div>
  );
}

function DocumentOutput({
  mode,
  isZh,
  progress,
}: {
  mode: Mode;
  isZh: boolean;
  progress: number;
}) {
  const ready = phase(progress) === 3;
  const rows = tableRows(isZh);
  const markdown = markdownContent(isZh);
  const value =
    mode === 'table'
      ? rows.map((row) => row.join('\t')).join('\n')
      : mode === 'latex'
        ? latex
        : mode === 'qr'
          ? repository
          : markdown;
  const label =
    mode === 'table'
      ? isZh
        ? '结构化表格 · 复制为 TSV'
        : 'STRUCTURED TABLE · COPY AS TSV'
      : mode === 'latex'
        ? 'LATEX'
        : mode === 'qr'
          ? isZh
            ? '解码结果'
            : 'DECODED RESULT'
          : 'MARKDOWN';
  const waiting = isZh
    ? {
        table: '保留每一行、每一列',
        latex: '把公式变成可编辑的 LaTeX',
        qr: '读取二维码里的链接',
        markdown: '还原标题、段落与列表',
      }
    : {
        table: 'Every row and column, preserved.',
        latex: 'From an image to editable LaTeX.',
        qr: 'Read the link inside the code.',
        markdown: 'Headings, paragraphs and lists.',
      };
  return (
    <div
      className={`snow-recognition__output snow-recognition__output--${mode}`}
      data-ready={ready}
    >
      <div className="snow-recognition__output-heading">
        <span className="snow-recognition__panel-label">{label}</span>
        <CopyButton value={value} isZh={isZh} disabled={!ready} />
      </div>
      <div className="snow-recognition__result-space">
        {!ready && (
          <div className="snow-recognition__waiting">
            <RecognizeTextIcon />
            <p>{waiting[mode]}</p>
            <span>
              {isZh
                ? '点击「识别」查看对应结果'
                : 'Choose Recognize to reveal the result.'}
            </span>
          </div>
        )}
        <div className="snow-recognition__document-result" aria-hidden={!ready}>
          {mode === 'table' && (
            <div className="snow-recognition__table-scroll">
              <table>
                <thead>
                  <tr>
                    {rows[0].map((cell) => (
                      <th key={cell}>{cell}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.slice(1).map((row, index) => (
                    <tr
                      key={row[0]}
                      style={{ '--result-order': index } as CSSProperties}
                    >
                      {row.map((cell) => (
                        <td key={cell}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="snow-recognition__result-note">
                {isZh
                  ? '3 行数据 × 3 列 · 制表符分隔，可粘贴到表格应用'
                  : '3 data rows × 3 columns · tab-separated for spreadsheets'}
              </p>
            </div>
          )}
          {mode === 'latex' && (
            <>
              <pre className="snow-recognition__code">{latex}</pre>
              <span className="snow-recognition__preview-label">
                {isZh ? '公式预览' : 'RENDERED FORMULA'}
              </span>
              <Formula isZh={isZh} />
            </>
          )}
          {mode === 'qr' && (
            <div className="snow-recognition__qr-result">
              <span className="snow-recognition__url-type">URL</span>
              <p>{repository}</p>
              <span className="snow-recognition__result-note">
                {isZh
                  ? 'SnowShot 官方开源仓库'
                  : 'The official SnowShot source repository'}
              </span>
            </div>
          )}
          {mode === 'markdown' && (
            <>
              <pre className="snow-recognition__code snow-recognition__markdown-code">
                {markdown}
              </pre>
              <div className="snow-recognition__markdown-preview">
                <span className="snow-recognition__preview-label">
                  {isZh ? '渲染预览' : 'RENDERED PREVIEW'}
                </span>
                <h4>{isZh ? 'SnowShot 工作流' : 'SnowShot workflow'}</h4>
                <p>
                  {isZh
                    ? '把想法清楚地分享出去。'
                    : 'Share your ideas clearly.'}
                </p>
                <ul>
                  {markdown
                    .split('\n')
                    .filter((line) => line.startsWith('- '))
                    .map((line) => (
                      <li key={line}>{line.slice(2)}</li>
                    ))}
                </ul>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export function DocumentRecognitionDemo({ isZh }: { isZh: boolean }) {
  const [mode, setMode] = useState<Mode>('table');
  const demo = useDemo({ duration: 8200 / 6 });
  const tabId = useId();
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const labels: Record<Mode, string> = isZh
    ? { table: '表格', latex: 'LaTeX 公式', qr: '二维码', markdown: 'Markdown' }
    : { table: 'Tables', latex: 'LaTeX', qr: 'QR codes', markdown: 'Markdown' };
  const source =
    mode === 'table' || mode === 'markdown'
      ? `${mode}-${isZh ? 'zh' : 'en'}`
      : mode;
  const select = (next: Mode) => {
    demo.reset();
    setMode(next);
  };
  const keyDown = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    const next =
      event.key === 'ArrowRight'
        ? (index + 1) % modes.length
        : event.key === 'ArrowLeft'
          ? (index + modes.length - 1) % modes.length
          : event.key === 'Home'
            ? 0
            : event.key === 'End'
              ? modes.length - 1
              : null;
    if (next !== null) {
      event.preventDefault();
      select(modes[next]);
      tabRefs.current[next]?.focus();
    }
  };
  return (
    <div
      className="snow-demo snow-recognition snow-recognition--document"
      ref={demo.containerRef}
      onPointerDownCapture={demo.interact}
      onKeyDownCapture={demo.interact}
      data-demo="document-recognition"
      data-mode={mode}
    >
      <RecognitionHeader
        title={isZh ? '文档识别' : 'Document recognition'}
        isZh={isZh}
        onRecognize={demo.play}
      />
      <div
        className="snow-recognition__tabs"
        role="tablist"
        aria-label={isZh ? '文档识别模式' : 'Document recognition mode'}
      >
        {modes.map((item, index) => (
          <button
            ref={(element) => {
              tabRefs.current[index] = element;
            }}
            type="button"
            key={item}
            id={`${tabId}-${item}`}
            role="tab"
            aria-selected={mode === item}
            aria-controls={`${tabId}-panel`}
            tabIndex={mode === item ? 0 : -1}
            onClick={() => select(item)}
            onKeyDown={(event) => keyDown(event, index)}
          >
            <span className="snow-recognition__mode-index">0{index + 1}</span>
            {labels[item]}
          </button>
        ))}
      </div>
      <div
        className="snow-recognition__workbench"
        role="tabpanel"
        id={`${tabId}-panel`}
        aria-labelledby={`${tabId}-${mode}`}
        key={`${mode}-${isZh}`}
      >
        <SourceImage
          src={`/images/demos/recognition-${source}.svg`}
          alt={`${labels[mode]} ${isZh ? '识别输入样例' : 'recognition input sample'}`}
          progress={demo.progress}
          isZh={isZh}
          mode={mode}
        />
        <DocumentOutput mode={mode} isZh={isZh} progress={demo.progress} />
      </div>
      <RecognitionStatus progress={demo.progress} isZh={isZh} mode={mode} />
      <div className="snow-recognition__footer">
        <span>
          {isZh
            ? '交互演示 · 固定样例展示输入与输出'
            : 'Interactive demo · fixed samples show matching inputs and outputs'}
        </span>
        <Playback demo={demo} isZh={isZh} />
      </div>
    </div>
  );
}
