"""Render a focused, bilingual update-entry illustration; not an application screenshot."""
from pathlib import Path
from html import escape
import argparse


def render(en):
    def tr(zh, english):
        return english if en else zh

    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="440" height="650" viewBox="0 0 440 650">',
             '<title>' + tr('从关于页检查更新', 'Check for updates from About') + '</title>',
             '<desc>' + tr('定位检查更新按钮，等待检查，再按结果和安装渠道继续。',
                          'Locate Check for updates, wait for its result, then follow the update channel.') + '</desc>',
             '<style>text{font-family:Arial,"PingFang SC",sans-serif;fill:#243047} .muted{fill:#536174} .button{font-size:15px;font-weight:600}</style>',
             '<rect width="440" height="650" rx="16" fill="#f4f5fc"/>']

    def text(x, y, value, size=17, cls=''):
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}">{escape(value)}</text>')

    def box(x, y, width, height, color='#fff', stroke='#cbd2df'):
        parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="10" fill="{color}" stroke="{stroke}"/>')

    def step(n, y, title):
        parts.append(f'<circle cx="39" cy="{y-6}" r="13" fill="#7050c8"/>')
        parts.append(f'<text x="39" y="{y-1}" text-anchor="middle" font-size="16" style="fill:#fff">{n}</text>')
        text(62, y, title, 17)

    def button(x, y, width, label):
        box(x, y, width, 36, '#f6f4fe', '#8770cc')
        text(x + 10, y + 24, label, 15, 'button')

    text(22, 34, tr('主动检查更新', 'Check for updates'), 24)
    text(22, 62, tr('主窗口侧栏 → 关于', 'Main-window sidebar → About'), 16, 'muted')

    box(18, 83, 404, 126)
    step(1, 111, tr('在关于页开始检查', 'Start from About'))
    text(35, 146, tr('更新区域', 'Update area'), 17)
    button(244, 152, 155, tr('检查更新', 'Check for updates'))
    text(35, 188, tr('单击按钮，等待检查。', 'Click once and wait.'), 15, 'muted')

    parts.append('<path d="M220 213v19m-6-6 6 6 6-6" fill="none" stroke="#8b7db3" stroke-width="2"/>')
    box(18, 238, 404, 112)
    step(2, 267, tr('查看检查状态', 'Watch the check status'))
    text(35, 303, tr('正在检查更新…', 'Checking for updates…'), 18)
    text(35, 330, tr('检查结束后再选择后续动作。', 'Wait for a result before continuing.'), 15, 'muted')

    parts.append('<path d="M220 355v19m-6-6 6 6 6-6" fill="none" stroke="#8b7db3" stroke-width="2"/>')
    box(18, 381, 404, 217)
    step(3, 411, tr('按结果和安装渠道继续', 'Follow the result and channel'))
    text(35, 447, tr('没有更新：当前已是最新版本', 'No update: You are up to date'), 17)
    text(35, 477, tr('有更新时，官网下载版的操作：', 'When an update is available:'), 16, 'muted')
    text(35, 514, 'Windows', 16)
    button(158, 489, 241, tr('下载更新', 'Download update'))
    text(35, 561, 'macOS', 16)
    button(158, 536, 241, tr('从 GitHub 下载', 'Download from GitHub'))
    text(35, 585, tr('Mac 也可能显示“从 Gitee 下载”。', 'Mac may instead show Download from Gitee.'), 14, 'muted')

    text(22, 631, tr('操作示意', 'Instructional illustration'), 13, 'muted')
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'docs/public/images/guides')
    args = parser.parse_args()
    for language in ('zh', 'en'):
        directory = args.output / 'en' if language == 'en' else args.output
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'start-update-entry.svg').write_text(render(language == 'en'))
