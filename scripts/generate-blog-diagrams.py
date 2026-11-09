"""Regenerate the small bilingual blog decision diagrams (standard library only)."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'docs/public/images/blog'
DIAGRAMS = {
    'permissions-check': {
        'zh': ('权限修改后的检查顺序', [('确认运行副本', '核对应用路径和系统权限项目'), ('按提示重新打开应用', '先结束编辑或录制，再重启'), ('执行一个小测试', '看状态，也检查实际图像或声音')]),
        'en': ('After changing a permission', [('Confirm the running copy', 'Match the app path and permission'), ('Reopen when requested', 'Finish editing or recording first'), ('Run a small task', 'Check status and the actual output')]),
    },
    'installer-choice': {
        'zh': ('先看系统，再选安装包', [('Windows：查看系统类型', 'x64 与 ARM64 选择对应包'), ('Mac：查看芯片和系统', 'Apple 芯片 arm64；Intel x86_64'), ('再选择应用类型', 'Intel Mac 仅 Full；Mac 需 15+')]),
        'en': ('Match the package to the computer', [('Windows: check system type', 'Choose the matching x64 or ARM64'), ('Mac: check chip and OS', 'Apple silicon: arm64; Intel: x86_64'), ('Then choose the edition', 'Intel Mac: Full only; macOS 15+')]),
    },
    'offline-check': {
        'zh': ('离线前，分别确认三件事', [('安装完成', '确认应用能够正常启动'), ('组件准备完成', '切到所需模型，完成一次识别'), ('断网重复同一任务', '核对文字，并在目标应用粘贴')]),
        'en': ('Three checks before going offline', [('Finish installation', 'Confirm the app starts normally'), ('Prepare the components', 'Use the required model for a test'), ('Repeat the task offline', 'Check the text and paste it')]),
    },
}


def diagram(title, steps):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 620" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><rect width="640" height="620" rx="24" fill="#f3f1fb"/><g font-family="system-ui, sans-serif"><text x="32" y="52" font-size="28" font-weight="700" fill="#25263a">{escape(title)}</text>']
    for index, (heading, detail) in enumerate(steps):
        y = 88 + index * 174
        parts.append(f'<rect x="28" y="{y}" width="584" height="140" rx="16" fill="white" stroke="#c9c3df"/><circle cx="62" cy="{y+38}" r="18" fill="#6d55bd"/><text x="62" y="{y+46}" text-anchor="middle" font-size="24" fill="white">{index+1}</text><text x="94" y="{y+47}" font-size="27" font-weight="600" fill="#282738">{escape(heading)}</text><text x="48" y="{y+102}" font-size="25" fill="#4c4b62">{escape(detail)}</text>')
        if index < 2:
            parts.append(f'<path d="M320 {y+146}v20m-8-8 8 8 8-8" stroke="#6d55bd" stroke-width="3" fill="none"/>')
    return ''.join(parts) + '</g></svg>\n'


if __name__ == '__main__':
    for name, locales in DIAGRAMS.items():
        for locale, (title, steps) in locales.items():
            target = ROOT / locale / f'{name}.svg'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(diagram(title, steps), encoding='utf-8')
