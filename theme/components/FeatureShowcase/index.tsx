import { AnnotationDemo, RegionSelectionDemo } from './CaptureDemos';
import { HistoryDemo, PinDemo } from './LibraryDemos';
import {
  DocumentRecognitionDemo,
  TextRecognitionDemo,
} from './RecognitionDemos';
import { ScreenRecordingDemo } from './RecordingDemo';
import './style.css';

const features = [
  { id: 'capture', zh: '区域截图', en: 'Region capture' },
  { id: 'annotate', zh: '截图标注', en: 'Annotation' },
  { id: 'text', zh: '文本识别', en: 'Text recognition' },
  { id: 'documents', zh: '文档识别', en: 'Documents' },
  { id: 'pin', zh: '桌面贴图', en: 'Pin to screen' },
  { id: 'record', zh: '屏幕录制', en: 'Recording' },
  { id: 'history', zh: '截图历史', en: 'History' },
] as const;

function FeatureCopy({
  label,
  title,
  description,
  guide,
  isZh,
}: {
  label: string;
  title: string;
  description: string;
  guide: string;
  isZh: boolean;
}) {
  return (
    <div className="snow-showcase-copy">
      <p className="snow-eyebrow">{label}</p>
      <h3>{title}</h3>
      <p>{description}</p>
      <a
        className="snow-text-link"
        href={`${isZh ? '/zh' : ''}/guides/${guide}.html`}
      >
        {isZh ? '阅读官方使用指南' : 'Read the official guide'}
        <span aria-hidden="true">↗</span>
      </a>
    </div>
  );
}

export function FeatureShowcase({ isZh }: { isZh: boolean }) {
  return (
    <section
      className="snow-showcase section-shell"
      id="features"
      aria-labelledby="features-title"
    >
      <div className="snow-section-heading">
        <p className="snow-eyebrow">
          {isZh ? 'SNOW SHOT / 动手试一试' : 'SNOW SHOT / TRY IT YOURSELF'}
        </p>
        <h2 id="features-title">
          {isZh
            ? '从截取画面，\n到清晰表达。'
            : 'From a capture\nto a clear idea.'}
        </h2>
        <p>
          {isZh
            ? '框选、标注、识别、分享。看看每一步如何发生，也亲手试一试。以下使用固定样例演示，不会操作你的桌面。'
            : 'Capture, annotate, recognize and share. Watch each workflow, then make it your own. These fixed-sample demos stay inside this page.'}
        </p>
      </div>
      <nav
        className="snow-showcase-nav"
        aria-label={isZh ? '功能演示导航' : 'Feature demo navigation'}
      >
        {features.map((feature) => (
          <a key={feature.id} href={`#demo-${feature.id}`}>
            {isZh ? feature.zh : feature.en}
          </a>
        ))}
      </nav>

      <article
        className="snow-showcase-feature snow-showcase-feature--split snow-showcase-feature--capture"
        id="demo-capture"
      >
        <FeatureCopy
          isZh={isZh}
          label={isZh ? '区域截图' : 'REGION CAPTURE'}
          title={
            isZh ? '只留下，\n你想说的部分。' : 'Just the part\nthat matters.'
          }
          description={
            isZh
              ? '拖出一个选区，调整边界，工具栏随之出现。画面之外淡去，重点自然留下。'
              : 'Draw a selection, fine-tune its edges, and bring up your tools. The rest fades away so your subject stands out.'
          }
          guide="capture/basics"
        />
        <RegionSelectionDemo isZh={isZh} />
      </article>
      <article
        className="snow-showcase-feature snow-showcase-feature--split snow-showcase-feature--reverse snow-showcase-feature--annotate"
        id="demo-annotate"
      >
        <FeatureCopy
          isZh={isZh}
          label={isZh ? '截图标注' : 'ANNOTATION'}
          title={
            isZh
              ? '少解释几句，\n多画一笔。'
              : 'Less explaining.\nMore showing.'
          }
          description={
            isZh
              ? '用箭头指向问题，用矩形框出范围，用高亮留下重点。选一个工具，在截图上画出来。'
              : 'Point with an arrow, frame a detail, or highlight a line. Pick a tool and draw directly on the capture.'
          }
          guide="annotations/basics"
        />
        <AnnotationDemo isZh={isZh} />
      </article>
      <article
        className="snow-showcase-feature snow-showcase-feature--wide snow-showcase-feature--text"
        id="demo-text"
      >
        <FeatureCopy
          isZh={isZh}
          label={isZh ? '文本识别' : 'TEXT RECOGNITION'}
          title={
            isZh
              ? '图片里的文字，接着用。'
              : 'The text in your image. Ready to use.'
          }
          description={
            isZh
              ? '从定位文字到逐行识别，原图与结果并排呈现。识别出的文字可选取、可复制。Snow Shot 支持本地文本识别。'
              : 'Locate the text, recognize each line, and compare it with the original. Select or copy the result. Snow Shot supports local text recognition.'
          }
          guide="recognition/text"
        />
        <TextRecognitionDemo isZh={isZh} />
      </article>
      <article
        className="snow-showcase-feature snow-showcase-feature--wide snow-showcase-feature--documents"
        id="demo-documents"
      >
        <FeatureCopy
          isZh={isZh}
          label={isZh ? '文档识别' : 'DOCUMENT RECOGNITION'}
          title={isZh ? '不止文字，还有结构。' : 'Keep the structure, too.'}
          description={
            isZh
              ? '表格保留行列，公式转为 LaTeX，二维码还原内容，文档变为 Markdown。切换样例，看见不同的输入与结果。'
              : 'Keep table rows and columns, turn formulas into LaTeX, decode QR codes, and convert documents to Markdown. Try each sample and inspect its output.'
          }
          guide="recognition/table"
        />
        <DocumentRecognitionDemo isZh={isZh} />
        <p className="snow-showcase-note">
          {isZh
            ? '表格与二维码识别适用于完整版；LaTeX、Markdown 转换的服务配置以应用内为准。'
            : 'Table and QR recognition are available in the full edition. LaTeX and Markdown conversion use the services configured in the app.'}
        </p>
      </article>
      <div className="snow-showcase-pair">
        <article
          className="snow-showcase-feature snow-showcase-feature--pin"
          id="demo-pin"
        >
          <FeatureCopy
            isZh={isZh}
            label={isZh ? '桌面贴图' : 'PIN TO SCREEN'}
            title={isZh ? '参考图，就在手边。' : 'Your reference, in reach.'}
            description={
              isZh
                ? '把截图固定在窗口之上，一边参考，一边工作。拖动它，或调整透明度，让视线留在重要的地方。'
                : 'Float a capture above your windows while you work. Move it or adjust its opacity to keep your reference close.'
            }
            guide="pinning/image"
          />
          <PinDemo isZh={isZh} />
        </article>
        <article
          className="snow-showcase-feature snow-showcase-feature--record"
          id="demo-record"
        >
          <FeatureCopy
            isZh={isZh}
            label={isZh ? '屏幕录制' : 'SCREEN RECORDING'}
            title={isZh ? '把过程，也讲清楚。' : 'Show how it happens.'}
            description={
              isZh
                ? '选择范围，开始录制。暂停时画面与计时一起停下，结束后回看刚才录下的过程。'
                : 'Choose a region and start recording. Pause the scene and timer together, then stop and review what you captured.'
            }
            guide="recording/start"
          />
          <ScreenRecordingDemo isZh={isZh} />
        </article>
      </div>
      <article
        className="snow-showcase-feature snow-showcase-feature--wide snow-showcase-feature--history"
        id="demo-history"
      >
        <FeatureCopy
          isZh={isZh}
          label={isZh ? '截图历史' : 'SCREENSHOT HISTORY'}
          title={
            isZh
              ? '用过的画面，不用重新截。'
              : 'Find it again. Keep the context.'
          }
          description={
            isZh
              ? '刚才的评审截图、表格与文字素材都在这里。按来源筛选，选中缩略图，打开大图继续查看。'
              : 'Your review capture, table and text sample are here. Filter by source, select a thumbnail and open it for a closer look.'
          }
          guide="output/history"
        />
        <HistoryDemo isZh={isZh} />
      </article>
    </section>
  );
}
