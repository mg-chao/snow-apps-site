import './style.css';
import { PageBreadcrumbs } from '../PageBreadcrumbs';

type Locale = 'en' | 'zh';

const copy = {
  zh: {
    title: '每一笔积分，都有清楚的去向。',
    intro:
      '用 Snow Shot 账户积分支付云端服务。免费次数优先使用，之后按实际用量结算。',
    exchangeLabel: '充值换算',
    exchangeUnit: '积分',
    exchangeNote: '按服务用量扣除',
    monthlyLabel: '每月包含',
    monthlyTitle: '先使用免费次数',
    monthlyIntro:
      '快速模型每个 IP 地址每月可用 5 次，文字与图片请求共用。表格专用模型和 LaTeX 专用模型分别计算免费次数。',
    monthly: [
      {
        count: '5',
        unit: '次 / IP / 月',
        name: '快速模型',
        detail: '文字与图片请求共用',
      },
      {
        count: '10',
        unit: '次 / 月',
        name: '表格专用模型',
        detail: '每次识别计 1 次',
      },
      {
        count: '10',
        unit: '次 / 月',
        name: 'LaTeX 专用模型',
        detail: '每次识别计 1 次',
      },
    ],
    includedNote: '免费次数每月自动刷新。用完后，继续使用会扣除账户积分。',
    ratesLabel: '统一使用积分计费',
    ratesTitle: '服务费率',
    translationHeading: '翻译',
    freeTranslation: '免费翻译',
    freeTranslationRate: '不扣账户积分',
    freeTranslationDetail: '选择「免费翻译」即可使用。',
    fastTranslation: '快速翻译',
    fastTranslationRate: '4.8 积分 / 千字符',
    fastTranslationDetail:
      '常见中文互译语言方向；其他语言组合为 10 积分 / 千字符。按原文字符数计费。',
    modelHeading: '模型',
    modelEstimate: '每 1,000 积分预计可用',
    fastModel: '快速模型',
    expertModel: '专家模型',
    screenshotTranslation: '截图翻译',
    tableRecognition: '表格识别',
    formulaRecognition: '公式识别',
    topupsLabel: '一次充值，累计计入',
    topupsTitle: '充值档位',
    topupsIntro: '每 ¥1 充值到账 100 积分。多次充值会累计计算。',
    topups: [
      { amount: '¥9.90', credits: '990' },
      { amount: '¥29.90', credits: '2,990' },
      { amount: '¥88.80', credits: '8,880' },
      { amount: '¥188', credits: '18,800', highlight: true },
      { amount: '¥999', credits: '99,900' },
    ],
    benefit:
      '累计净充值达到 18,800 积分后，可免费使用表格专用模型和 LaTeX 专用模型，不占每月免费次数。该权益没有期限，消费积分不会减少累计充值积分。',
    refund: '成功退款会减少累计充值积分，可能改变当前权益档位。',
    accountNoteTitle: '查看账户记录',
    accountNote:
      '客户端「账户」页会显示可用积分、累计充值积分，以及充值、使用和退款记录。',
    otherServices:
      '你自行配置的翻译服务和自定义 AI 模型，按对应服务商的规则计费，不扣 Snow Shot 账户积分。',
  },
  en: {
    title: 'Know where every credit goes.',
    intro:
      'Use Snow Shot account credits for cloud services. Included requests are used first; then you pay for what you use.',
    exchangeLabel: 'TOP-UP VALUE',
    exchangeUnit: 'credits',
    exchangeNote: 'Deducted by actual usage',
    monthlyLabel: 'INCLUDED EACH MONTH',
    monthlyTitle: 'Start with free requests',
    monthlyIntro:
      'Each IP gets 5 Fast Model requests per month, shared by text and image. The Table-specific model and LaTeX-specific model each have their own allowance.',
    monthly: [
      {
        count: '5',
        unit: 'requests / IP / month',
        name: 'Fast Model',
        detail: 'Shared by text and image requests',
      },
      {
        count: '10',
        unit: 'requests / month',
        name: 'Table-specific model',
        detail: 'One request per recognition',
      },
      {
        count: '10',
        unit: 'requests / month',
        name: 'LaTeX-specific model',
        detail: 'One request per recognition',
      },
    ],
    includedNote:
      'Allowances refresh monthly. Further requests use account credits once the allowance is used up.',
    ratesLabel: 'ALL SERVICE RATES IN CREDITS',
    ratesTitle: 'Service rates',
    translationHeading: 'Translation',
    freeTranslation: 'Free translation',
    freeTranslationRate: 'No account credits',
    freeTranslationDetail: 'Choose Free translation to use it.',
    fastTranslation: 'Fast Translation',
    fastTranslationRate: '4.8 credits / 1,000 characters',
    fastTranslationDetail:
      'For common language pairs involving Chinese; other pairs are 10 credits / 1,000 characters. Charged by source text length.',
    modelHeading: 'Models',
    modelEstimate: 'Estimated requests per 1,000 credits',
    fastModel: 'Fast Model',
    expertModel: 'Expert Model',
    screenshotTranslation: 'Screenshot translation',
    tableRecognition: 'Table recognition',
    formulaRecognition: 'Formula recognition',
    topupsLabel: 'ONE-TIME TOP-UPS, COUNTED TOGETHER',
    topupsTitle: 'Top-up packages',
    topupsIntro:
      'Each ¥1 adds 100 credits. Top-ups accumulate toward your total.',
    topups: [
      { amount: '¥9.90', credits: '990' },
      { amount: '¥29.90', credits: '2,990' },
      { amount: '¥88.80', credits: '8,880' },
      { amount: '¥188', credits: '18,800', highlight: true },
      { amount: '¥999', credits: '99,900' },
    ],
    benefit:
      'At 18,800 cumulative net top-up credits, the Table-specific model and LaTeX-specific model are free and do not use the monthly allowance. This benefit does not expire. Spending credits does not reduce your cumulative top-up credits.',
    refund:
      'A completed refund reduces your cumulative top-up credits and may change your current benefit tier.',
    accountNoteTitle: 'Your account record',
    accountNote:
      'The Account page in the client shows available credits, cumulative top-up credits, and top-up, usage, and refund transactions.',
    otherServices:
      'Translation services and custom AI models that you configure are billed by their providers and do not use Snow Shot account credits.',
  },
} as const;

const models = ['fastModel', 'expertModel'] as const;

const estimates = [
  {
    task: 'screenshotTranslation',
    fastModel: '3,000–5,000',
    expertModel: '600–1,000',
  },
  {
    task: 'tableRecognition',
    fastModel: '4,000–6,000',
    expertModel: '800–1,200',
  },
  {
    task: 'formulaRecognition',
    fastModel: '6,000–8,000',
    expertModel: '1,200–1,600',
  },
] as const;

export function PricingPage({ locale }: { locale: Locale }) {
  const t = copy[locale];
  const isZh = locale === 'zh';

  return (
    <main className="snow-pricing" lang={locale}>
      <div className="snow-pricing__hero-surface">
        <header className="snow-pricing__hero snow-pricing__shell">
          <div className="snow-pricing__hero-copy">
            <PageBreadcrumbs placement="content" />
            <h1>{t.title}</h1>
            <p className="snow-pricing__intro">{t.intro}</p>
          </div>
          <aside
            className="snow-pricing__exchange"
            aria-label={t.exchangeLabel}
          >
            <span className="snow-pricing__exchange-label">
              {t.exchangeLabel}
            </span>
            <div className="snow-pricing__exchange-value">
              <span>¥1</span>
              <span aria-hidden="true">→</span>
              <strong>100</strong>
              <span className="snow-pricing__exchange-unit">
                {t.exchangeUnit}
              </span>
            </div>
            <span className="snow-pricing__exchange-note">
              {t.exchangeNote}
            </span>
          </aside>
        </header>
      </div>

      <div className="snow-pricing__shell snow-pricing__content">
        <section
          className="snow-pricing__section"
          aria-labelledby="monthly-title"
        >
          <div className="snow-pricing__section-heading">
            <p className="snow-pricing__eyebrow">{t.monthlyLabel}</p>
            <h2 id="monthly-title">{t.monthlyTitle}</h2>
            <p>{t.monthlyIntro}</p>
          </div>
          <div className="snow-pricing__monthly-grid">
            {t.monthly.map((item) => (
              <article className="snow-pricing__monthly-card" key={item.name}>
                <div className="snow-pricing__monthly-count">
                  <strong>{item.count}</strong>
                  <span>{item.unit}</span>
                </div>
                <h3>{item.name}</h3>
                <p>{item.detail}</p>
              </article>
            ))}
          </div>
          <p className="snow-pricing__fineprint">{t.includedNote}</p>
        </section>

        <section
          className="snow-pricing__section"
          aria-labelledby="rates-title"
        >
          <div className="snow-pricing__section-heading">
            <p className="snow-pricing__eyebrow">{t.ratesLabel}</p>
            <h2 id="rates-title">{t.ratesTitle}</h2>
          </div>

          <div className="snow-pricing__subsection">
            <div className="snow-pricing__model-heading">
              <h3 className="snow-pricing__subheading">{t.modelHeading}</h3>
              <p>{t.modelEstimate}</p>
            </div>
            <div className="snow-pricing__model-grid">
              {models.map((model) => (
                <article
                  className={`snow-pricing__model-card${model === 'expertModel' ? ' snow-pricing__model-card--expert' : ''}`}
                  key={model}
                >
                  <h4>{t[model]}</h4>
                  <dl>
                    {estimates.map((estimate) => (
                      <div
                        className="snow-pricing__estimate"
                        key={estimate.task}
                      >
                        <dt>{t[estimate.task]}</dt>
                        <dd>
                          {estimate[model]}
                          {isZh && <small>次</small>}
                        </dd>
                      </div>
                    ))}
                  </dl>
                </article>
              ))}
            </div>
          </div>

          <div className="snow-pricing__subsection">
            <h3 className="snow-pricing__subheading">{t.translationHeading}</h3>
            <div className="snow-pricing__translation-grid">
              <article className="snow-pricing__rate-card snow-pricing__rate-card--free">
                <span className="snow-pricing__service-name">
                  {t.freeTranslation}
                </span>
                <strong>{t.freeTranslationRate}</strong>
                <p>{t.freeTranslationDetail}</p>
              </article>
              <article className="snow-pricing__rate-card">
                <span className="snow-pricing__service-name">
                  {t.fastTranslation}
                </span>
                <strong>{t.fastTranslationRate}</strong>
                <p>{t.fastTranslationDetail}</p>
              </article>
            </div>
          </div>
        </section>

        <section
          className="snow-pricing__section"
          aria-labelledby="topups-title"
        >
          <div className="snow-pricing__section-heading">
            <p className="snow-pricing__eyebrow">{t.topupsLabel}</p>
            <h2 id="topups-title">{t.topupsTitle}</h2>
            <p>{t.topupsIntro}</p>
          </div>
          <div className="snow-pricing__topup-grid">
            {t.topups.map((item) => (
              <article
                className={`snow-pricing__topup-card${'highlight' in item && item.highlight ? ' snow-pricing__topup-card--highlight' : ''}`}
                key={item.amount}
              >
                <span>{isZh ? '充值金额' : 'TOP-UP'}</span>
                <strong>{item.amount}</strong>
                <p>
                  <b>{item.credits}</b> {t.exchangeUnit}
                </p>
                {'highlight' in item && item.highlight ? (
                  <small>
                    {isZh ? '解锁免费识别权益' : 'Free recognition benefit'}
                  </small>
                ) : null}
              </article>
            ))}
          </div>
          <div className="snow-pricing__cumulative-note">
            <div>
              <strong>
                {isZh
                  ? '18,800 积分累计充值权益'
                  : 'Benefit at 18,800 cumulative top-up credits'}
              </strong>
              <p>{t.benefit}</p>
              <p className="snow-pricing__refund-note">{t.refund}</p>
            </div>
            <span className="snow-pricing__cumulative-mark" aria-hidden="true">
              18.8K
            </span>
          </div>
        </section>

        <footer className="snow-pricing__footer">
          <div>
            <strong>{t.accountNoteTitle}</strong>
            <p>{t.accountNote}</p>
          </div>
          <p className="snow-pricing__other-services">{t.otherServices}</p>
        </footer>
      </div>
    </main>
  );
}
