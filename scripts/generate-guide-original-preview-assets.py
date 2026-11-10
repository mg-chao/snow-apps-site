"""Draw original-image comparison states; these are illustrations, not application captures."""
from pathlib import Path
from html import escape
import csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/public/images/guides'
EYE = 'M942.2 486.2C847.4 286.5 704.1 186 512 186c-192.2 0-335.4 100.5-430.2 300.3a60.3 60.3 0 0 0 0 51.5C176.6 737.5 319.9 838 512 838c192.2 0 335.4-100.5 430.2-300.3 7.7-16.2 7.7-35 0-51.5zM512 766c-161.3 0-279.4-81.8-362.7-254C232.6 339.8 350.7 258 512 258c161.3 0 279.4 81.8 362.7 254C791.5 684.2 673.4 766 512 766zm-4-430c-97.2 0-176 78.8-176 176s78.8 176 176 176 176-78.8 176-176-78.8-176-176-176zm0 288c-61.9 0-112-50.1-112-112s50.1-112 112-112 112 50.1 112 112-50.1 112-112 112z'


def txt(x, y, value, size=20, color='#26364e', weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'


def original():
    return ('<rect width="300" height="200" fill="#e7f1ff"/>'
            '<rect x="12" y="12" width="276" height="176" fill="none" stroke="#6694cc" stroke-width="3"/>'
            + txt(24, 48, 'TOP', 28, '#255fa5', 700)
            + '<path d="M238 68V30m-15 16 15-16 15 16" fill="none" stroke="#255fa5" stroke-width="5"/>'
            + '<circle cx="85" cy="130" r="34" fill="#f5c573"/>' + txt(74, 141, 'A', 31, '#5d4019', 700)
            + '<rect x="172" y="98" width="72" height="64" rx="8" fill="#b7d8be"/>'
            + txt(196, 141, 'B', 31, '#245b31', 700))


rows = []
for locale in ('zh', 'en'):
    en = locale == 'en'
    titles = (['Check the selected layout', 'Compare the original', 'Return to the layout'] if en
              else ['查看已选图片的当前排版', '对照未变换的原始图像', '关闭查看器，返回排版'])
    labels = (['The layout shows a rotated crop.', 'The viewer shows the full source.', 'The same crop and rotation remain.'] if en
              else ['排版中：图片已旋转，并被裁切。', '原图查看器：完整原图，方向不变。', '回到排版：原有裁切和旋转保留。'])
    actions = ([['Select the image, then use the eye icon.', 'Check the source before changing the crop.'],
                ['Compare the top label and both shapes.', 'This view does not export the layout.'],
                ['Close the original-image viewer.', 'Continue editing or export from the layout.']] if en
               else [['选中目标图片，再点击眼睛图标。', '调整裁切前，先确认原图是否完整。'],
                     ['检查原图的朝向、边缘和完整内容。', '这里显示原图，不会导出当前排版。'],
                     ['关闭原图查看器，返回原来的排版。', '继续调整，或从排版窗口执行导出。']])
    for index in range(1, 4):
        body = txt(24, 46, titles[index-1], 25, weight=700) + txt(24, 91, labels[index-1], 19)
        if index == 2:
            body += '<rect x="48" y="153" width="344" height="254" rx="10" fill="white" stroke="#becada"/>'
            body += '<g transform="translate(70 180)">' + original() + '</g>'
            body += txt(70, 438, '300 × 200', 20, '#53627d')
        else:
            body += ('<defs><clipPath id="cell"><rect x="30" y="170" width="380" height="260"/></clipPath></defs>'
                     '<rect x="30" y="170" width="380" height="260" fill="white"/>'
                     '<g clip-path="url(#cell)"><g transform="translate(220 300) rotate(90) scale(1.6) translate(-150 -100)">'
                     + original() + '</g></g>'
                     '<rect x="30" y="170" width="380" height="260" fill="none" stroke="#397bd2" stroke-width="3"/>'
                     f'<g transform="translate(358 120) scale(.034)" fill="#397bd2"><path d="{EYE}"/></g>')
            body += txt(24, 142, 'Preview original image →' if en else '预览原图 →', 19, '#255fa5')
        body += txt(24, 487, actions[index-1][0], 19) + txt(24, 518, actions[index-1][1], 19)
        body += txt(24, 565, 'Instructional illustration' if en else '操作示意', 17, '#53627d')
        body += txt(365, 565, f'{index} / 3', 17, '#53627d')
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 590" role="img" aria-labelledby="title desc">'
               f'<title id="title">{escape(titles[index-1])}</title><desc id="desc">{escape(labels[index-1])}</desc>'
               '<rect width="440" height="590" rx="20" fill="#f5f7fc"/>'
               '<g font-family="system-ui,-apple-system,PingFang SC,Microsoft YaHei,sans-serif">' + body + '</g></svg>')
        path = OUT / ('en' if en else '') / f'img-original-preview-{index}.svg'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg)
        docs = [f'docs/{locale}/guides/image-editing/{topic}.mdx' for topic in ('collage', 'pdf')]
        rows.append({'Asset': path.relative_to(ROOT).as_posix(), 'Feature IDs': 'IMG-045',
                     'Teaching purpose': titles[index-1], 'Documentation path': ';'.join(docs),
                     'Associated step': f'{index}/3: ' + ' '.join(actions[index-1]),
                     'Source': 'f02f50e:collageeditorwidget.cpp:996-1029,1794-1799;collageoriginalpreview_p.h:15-32,55-108;collagepdfpagegrid.cpp:1204-1215;collagepdftemplatewidget.cpp:1262-1271;ant_design_qt/packages/ant_design_icons_qt/resources/icons/outlined/eye.svg;artifacts/operation-candidates-image-review-20261110.json',
                     'Production method': 'Original vector comparison of one synthetic300x200 image, its rotated/scaled layout crop, unmodified original and unchanged return state. Product Eye icon geometry is reused. Not application UI or runtime proof.',
                     'Status': 'Produced; render, content and website review pending',
                     'Capture prerequisites and next action': 'Verify selected-image eye action, full original and unchanged return separately in static collage, PDF page and PDF template hosts. No native pass from this illustration.'})
with (ROOT / 'artifacts/assets-original-preview-20261110.csv').open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(f'Produced {len(rows)} bilingual original-preview illustration states')
