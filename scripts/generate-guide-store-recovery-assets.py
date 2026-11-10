"""Draw a source-backed Store recording-recovery flow; never synthesize app chrome."""
from pathlib import Path
from html import escape
import csv

ROOT = Path(__file__).resolve().parents[1]
COLORS = {'bg': '#f4f5fc', 'ink': '#243047', 'muted': '#536174',
          'purple': '#7050c8', 'line': '#cbd2df', 'soft': '#f6f4fe'}
COPY = {
 'zh': {
  'title': '中断录屏的恢复路径',
  'subtitle': 'Microsoft Store 安装的 Snow Shot · Windows',
  'desc': '会话中断后重新打开应用，有保留数据才可能出现恢复提示。有可恢复源时恢复到裁剪预览，再保存并回放；打开文件夹仅查看数据。',
  'one': '会话结束后重新打开',
  'one_body': ['Windows 结束会话时录制被打断，', '重新打开 Snow Shot。', '若找到保留数据，才可能出现', '“屏幕录制恢复”提示。'],
  'two': '有可恢复源时选择“恢复”',
  'two_body': ['仍有可恢复的 .snowrec 源文件时，', '点击“恢复”，进入裁剪预览。', '先检查画面，再按需要调整范围。'],
  'branch': '另一选择：打开文件夹',
  'branch_body': ['只在文件管理器中定位保留数据。', '不会进入裁剪，也不会导出成片。', '没有“恢复”按钮时，先检查保留文件。'],
  'three': '另存文件，等待完成再回放',
  'three_body': ['在裁剪预览点击“保存到文件”。', '选择输出位置并保存。', '等待导出完成，再打开输出文件。', '回放检查画面与声音。'],
  'footer': '操作示意',
 },
 'en': {
  'title': 'Recover an interrupted recording',
  'subtitle': 'Snow Shot from Microsoft Store · Windows',
  'desc': 'Reopen after a session interruption. A prompt requires retained data. With a recoverable source, Recover opens trim preview; save and check playback. Open folder only locates data.',
  'one': 'Reopen after an interruption',
  'one_body': ['Windows ended the session during recording.', 'Open Snow Shot again.', 'A recovery prompt appears only if', 'retained data is still found.'],
  'two': 'Recover into the trim preview',
  'two_body': ['With a recoverable .snowrec source file,', 'choose Recover to open the trim preview.', 'Check the video; adjust the range if needed.'],
  'branch': 'Other choice: Open folder',
  'branch_body': ['Only locates data in the file manager.', 'Does not open trim or export a video.', 'If Recover is absent, inspect the saved files.'],
  'three': 'Save, then check playback',
  'three_body': ['Choose Save to file in the trim preview.', 'Select a destination and save.', 'Wait for export to finish, then open the file.', 'Check both the picture and sound.'],
  'footer': 'Instructional illustration',
 },
}

def text(parts, x, y, value, size=16, weight=400, color='ink'):
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{COLORS[color]}">{escape(value)}</text>')

def arrow(parts, top, bottom):
    parts.append(f'<path d="M220 {top}V{bottom}m-6-6 6 6 6-6" fill="none" stroke="#8b7db3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')

def card(parts, y, height, number, title, lines):
    parts.append(f'<rect x="18" y="{y}" width="404" height="{height}" rx="10" fill="#fff" stroke="{COLORS["line"]}"/>')
    parts.append(f'<circle cx="39" cy="{y+24}" r="13" fill="{COLORS["purple"]}"/>')
    text(parts, 39, y+29, str(number), 16, 600, 'bg')
    parts[-1] = parts[-1].replace(' x="39"', ' x="39" text-anchor="middle"').replace(f'fill="{COLORS["bg"]}"', 'fill="#fff"')
    text(parts, 62, y+30, title, 18, 600)
    for i, line in enumerate(lines):
        text(parts, 35, y+62+i*25, line)


def svg(lang):
    c = COPY[lang]
    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="440" height="884" viewBox="0 0 440 884" role="img">',
         f'<title>{escape(c["title"])}</title>', f'<desc>{escape(c["desc"])}</desc>',
         '<style>text{font-family:Arial,"PingFang SC",sans-serif}</style>',
         f'<rect width="440" height="884" rx="16" fill="{COLORS["bg"]}"/>']
    text(p, 22, 34, c['title'], 23, 600)
    text(p, 22, 62, c['subtitle'], 15, 400, 'muted')
    card(p, 86, 165, 1, c['one'], c['one_body'])
    arrow(p, 257, 276)
    card(p, 286, 324, 2, c['two'], c['two_body'])
    # This inset is a semantic branch, not a recreation of a native dialog.
    p.append(f'<rect x="35" y="428" width="370" height="159" rx="8" fill="{COLORS["soft"]}" stroke="#c6b9e9"/>')
    p.append('<path d="M47 449h10m-4-4 4 4-4 4" fill="none" stroke="#7050c8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    text(p, 65, 454, c['branch'], 17, 600)
    for i, line in enumerate(c['branch_body']):
        text(p, 49, 483+i*28, line, 16, 400, 'muted')
    arrow(p, 616, 635)
    card(p, 645, 184, 3, c['three'], c['three_body'])
    text(p, 22, 861, c['footer'], 13, 400, 'muted')
    p.append('</svg>')
    return '\n'.join(p)+'\n'


def main():
    asset_rows = []
    source = ('Fixed f02f50e5c6b132335247079398944b6fc9f7e6d6: '
              'snow_shot/src/app/applicationcontroller.cpp:1579-1583; '
              'snow_shot/src/presentation/recording/screenrecordingcontroller.cpp:1787-1864; '
              'snow_shot/include/snow_shot/app/distribution.h:49-57; '
              'snow_shot/src/presentation/recording/recordingtrimsession.cpp:100-127,209-228,303-335; '
              'CMakeLists.txt:38-43,85-88; '
              'snow_shot/i18n/recording/snow_shot_recording_zh_CN.ts:245-270')
    for lang in ['zh', 'en']:
        relative = Path('docs/public/images/guides') / ('en' if lang == 'en' else '') / 'rec-store-recovery.svg'
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(svg(lang))
        asset_rows.append({
          'Asset': str(relative), 'Feature IDs': 'REC-028',
          'Teaching purpose': ('区分Store启动恢复、裁剪导出与仅打开数据文件夹。' if lang == 'zh' else 'Distinguish Store launch recovery, trim/export, and folder-only inspection.'),
          'Documentation path': f'docs/{lang}/guides/recording/start.mdx',
          'Associated step': ('会话中断后重开→有源时恢复到裁剪预览→保存/等待/回放；打开文件夹是独立查看分支。' if lang == 'zh' else 'Reopen after interruption → recoverable source → trim preview → save/wait/playback; Open folder is a separate inspection branch.'),
          'Source': source,
          'Production method': 'Original 440px-wide source-backed SVG flow cards; explicit instructional label; no invented window/toolbar chrome. Dedicated generator; not native UI evidence.',
          'Status': 'Produced; staged only. XML and author 440/350px render review passed; independent review, website and native acceptance remain pending.',
          'Capture prerequisites and next action': 'Store-managed Windows x64 Full; a Windows session interruption with retained recovery marker/source. Verify startup prompt, conditional Recover, trim preview, save completion/playback, and Open folder separately. Root integrates asset and runs website QA.',
        })
    target = ROOT / 'artifacts/assets-store-recovery-20261110d.csv'
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Asset','Feature IDs','Teaching purpose','Documentation path','Associated step','Source','Production method','Status','Capture prerequisites and next action'])
        writer.writeheader(); writer.writerows(asset_rows)

if __name__ == '__main__':
    main()
