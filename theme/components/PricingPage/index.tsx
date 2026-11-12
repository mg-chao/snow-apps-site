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
      '快速模型每个 IP 地址每月可用 5 次，文字与图片请求共用；表格和公式识别次数分别计算。',
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
        name: '表格识别',
        detail: '每次识别计 1 次',
      },
      {
        count: '10',
        unit: '次 / 月',
        name: 'LaTeX 公式识别',
        detail: '每次识别计 1 次',
      },
    ],
    includedNote:
      '免费次数用完后，继续使用会按下方费率扣除账户积分。每月自动刷新。',
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
    tokenUnit: '单位：积分 / 每 100 万 tokens',
    modelName: '模型',
    modelInput: '输入',
    modelOutput: '输出',
    cachedInput: '缓存输入',
    fastModel: '快速模型',
    fastModelDetail:
      '用于翻译等功能时也按模型费率结算。文本使用 Qwen3.7 Flash，图片使用 Qwen3.8 Flash；Qwen3.7 Flash 按输入长度选择费率档位。',
    expertModel: '专家模型',
    expertModelDetail: '使用 Qwen3.8 Max，不包含每月免费次数。',
    tableRate: '3 积分 / 次',
    latexRate: '1.5 积分 / 次',
    recognitionHeading: '识别',
    recognitionNote:
      '累计净充值达到 18,800 积分后，表格识别与 LaTeX 公式识别免费，不占每月免费次数。',
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
      '累计净充值达到 18,800 积分后，表格识别和 LaTeX 公式识别免费使用。该权益没有期限；消费积分不会减少累计充值积分。',
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
      'Each IP gets 5 Fast Model requests per month, shared by text and image. Table and formula recognition have separate allowances.',
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
        name: 'Table recognition',
        detail: 'One request per recognition',
      },
      {
        count: '10',
        unit: 'requests / month',
        name: 'LaTeX formula recognition',
        detail: 'One request per recognition',
      },
    ],
    includedNote:
      'After an allowance is used, further requests are charged at the rates below. Allowances refresh monthly.',
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
    tokenUnit: 'UNIT: CREDITS PER 1M TOKENS',
    modelName: 'MODEL',
    modelInput: 'INPUT',
    modelOutput: 'OUTPUT',
    cachedInput: 'CACHED INPUT',
    fastModel: 'Fast Model',
    fastModelDetail:
      'The same model rates apply when translating. Qwen3.7 Flash is used for text and Qwen3.8 Flash for images; Qwen3.7 Flash rates depend on input length.',
    expertModel: 'Expert Model',
    expertModelDetail: 'Powered by Qwen3.8 Max; each request uses credits.',
    tableRate: '3 credits / request',
    latexRate: '1.5 credits / request',
    recognitionHeading: 'Recognition',
    recognitionNote:
      'At 18,800 cumulative net top-up credits, table and LaTeX formula recognition become free and no longer use the monthly allowance.',
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
      'At 18,800 cumulative net top-up credits, table and LaTeX formula recognition are free. This benefit does not expire; spending credits does not reduce your cumulative top-up credits.',
    refund:
      'A completed refund reduces your cumulative top-up credits and may change your current benefit tier.',
    accountNoteTitle: 'Your account record',
    accountNote:
      'The Account page in the client shows available credits, cumulative top-up credits, and top-up, usage, and refund transactions.',
    otherServices:
      'Translation services and custom AI models that you configure are billed by their providers and do not use Snow Shot account credits.',
  },
} as const;

const modelRates = {
  zh: [
    {
      name: 'Qwen3.7 Flash · ≤32K 输入',
      input: '20',
      output: '80',
      cached: '4',
    },
    {
      name: 'Qwen3.7 Flash · ≤256K 输入',
      input: '60',
      output: '240',
      cached: '12',
    },
    {
      name: 'Qwen3.7 Flash · >256K 输入',
      input: '120',
      output: '480',
      cached: '24',
    },
    { name: 'Qwen3.8 Flash', input: '80', output: '270', cached: '10' },
    { name: 'Qwen3.8 Max', input: '1,200', output: '3,600', cached: '150' },
  ],
  en: [
    {
      name: 'Qwen3.7 Flash · ≤32K input',
      input: '20',
      output: '80',
      cached: '4',
    },
    {
      name: 'Qwen3.7 Flash · ≤256K input',
      input: '60',
      output: '240',
      cached: '12',
    },
    {
      name: 'Qwen3.7 Flash · >256K input',
      input: '120',
      output: '480',
      cached: '24',
    },
    { name: 'Qwen3.8 Flash', input: '80', output: '270', cached: '10' },
    { name: 'Qwen3.8 Max', input: '1,200', output: '3,600', cached: '150' },
  ],
} as const;

export function PricingPage({ locale }: { locale: Locale }) {
  const t = copy[locale];
  const rates = modelRates[locale];
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

          <div className="snow-pricing__subsection">
            <h3 className="snow-pricing__subheading">{t.modelHeading}</h3>
            <div className="snow-pricing__model-intro">
              <div>
                <strong>{t.fastModel}</strong>
                <p>{t.fastModelDetail}</p>
              </div>
              <div>
                <strong>{t.expertModel}</strong>
                <p>{t.expertModelDetail}</p>
              </div>
            </div>
            <div className="snow-pricing__model-table">
              <table aria-label={t.modelHeading}>
                <caption>{t.tokenUnit}</caption>
                <thead>
                  <tr>
                    <th scope="col">{t.modelName}</th>
                    <th scope="col">{t.modelInput}</th>
                    <th scope="col">{t.modelOutput}</th>
                    <th scope="col">{t.cachedInput}</th>
                  </tr>
                </thead>
                <tbody>
                  {rates.map((rate) => (
                    <tr key={rate.name}>
                      <td>{rate.name}</td>
                      <td>{rate.input}</td>
                      <td>{rate.output}</td>
                      <td>{rate.cached}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="snow-pricing__subsection">
            <h3 className="snow-pricing__subheading">{t.recognitionHeading}</h3>
            <div className="snow-pricing__recognition-grid">
              <article className="snow-pricing__recognition-rate">
                <span>{isZh ? '表格识别' : 'Table recognition'}</span>
                <strong>{t.tableRate}</strong>
                <small>
                  {isZh
                    ? '每月前 10 次免费'
                    : 'First 10 requests each month are free'}
                </small>
              </article>
              <article className="snow-pricing__recognition-rate">
                <span>
                  {isZh ? 'LaTeX 公式识别' : 'LaTeX formula recognition'}
                </span>
                <strong>{t.latexRate}</strong>
                <small>
                  {isZh
                    ? '每月前 10 次免费'
                    : 'First 10 requests each month are free'}
                </small>
              </article>
            </div>
            <p className="snow-pricing__benefit-note">
              <span aria-hidden="true">✳</span>
              {t.recognitionNote}
            </p>
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
