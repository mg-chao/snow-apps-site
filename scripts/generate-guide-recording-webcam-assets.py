# -*- coding: utf-8 -*-
"""Generate six focused webcam illustrations using released control geometry.

Reference: f02f50e recordingwebcamcontrol.cpp:60-74,106-151,166-235,252-302;
screenrecordingcontroller.cpp:660-685; recordingeffectpreview.cpp:491-514.
The four actual glyphs are embedded below; no surrounding app toolbar is invented.
"""
from pathlib import Path
from html import escape

GLYPH_SOURCES=['ant_design_qt/packages/ant_design_icons_qt/resources/icons/outlined/rotate-right.svg', 'ant_design_qt/packages/ant_design_icons_qt/resources/icons/outlined/rotate-left.svg', 'snow_shot/src/presentation/components/icons/resources/flip-horizontal.svg', 'snow_shot/src/presentation/components/icons/resources/flip-vertical.svg']
GLYPHS=['<path d="M480.5 251.2c13-1.6 25.9-2.4 38.8-2.5v63.9c0 6.5 7.5 10.1 12.6 6.1L660 217.6c4-3.2 4-9.2 0-12.3l-128-101c-5.1-4-12.6-0.4-12.6 6.1l-0.2 64c-118.6 0.5-235.8 53.4-314.6 154.2-69.6 89.2-95.7 198.6-81.1 302.4h74.9c-0.9-5.3-1.7-10.7-2.4-16.1-5.1-42.1-2.1-84.1 8.9-124.8 11.4-42.2 31-81.1 58.1-115.8 27.2-34.7 60.3-63.2 98.4-84.3 37-20.6 76.9-33.6 119.1-38.8z" p-id="10583"></path><path d="M880 418H352c-17.7 0-32 14.3-32 32v414c0 17.7 14.3 32 32 32h528c17.7 0 32-14.3 32-32V450c0-17.7-14.3-32-32-32z m-44 402H396V494h440v326z" p-id="10584"></path>', '<path d="M672 418H144c-17.7 0-32 14.3-32 32v414c0 17.7 14.3 32 32 32h528c17.7 0 32-14.3 32-32V450c0-17.7-14.3-32-32-32z m-44 402H188V494h440v326z" p-id="10464"></path><path d="M819.3 328.5c-78.8-100.7-196-153.6-314.6-154.2l-0.2-64c0-6.5-7.6-10.1-12.6-6.1l-128 101c-4 3.1-3.9 9.1 0 12.3L492 318.6c5.1 4 12.7 0.4 12.6-6.1v-63.9c12.9 0.1 25.9 0.9 38.8 2.5 42.1 5.2 82.1 18.2 119 38.7 38.1 21.2 71.2 49.7 98.4 84.3 27.1 34.7 46.7 73.7 58.1 115.8 11 40.7 14 82.7 8.9 124.8-0.7 5.4-1.4 10.8-2.4 16.1h74.9c14.8-103.6-11.3-213-81-302.3z" p-id="10465"></path>', '\n  <path d="M144 352L304 192h96v640H144V352zm736 0L720 192h-96v640h256V352z" fill="none" stroke="currentColor" stroke-width="72" stroke-linejoin="round" data-adqt-slot="primary"/>\n', '\n  <g transform="rotate(90 512 512)">\n    <path d="M144 352L304 192h96v640H144V352zm736 0L720 192h-96v640h256V352z" fill="none" stroke="currentColor" stroke-width="72" stroke-linejoin="round" data-adqt-slot="primary"/>\n  </g>\n']
STRINGS={"zh": {"title": "\u6444\u50cf\u5934\u79fb\u52a8\u4e0e\u7f29\u653e", "label": "\u64cd\u4f5c\u793a\u610f", "region": "\u5f55\u5236\u533a\u57df\uff08\u5f00\u59cb\u524d\uff09", "webcam": "\u6444\u50cf\u5934", "move": "\u62d6\u52a8\u4f4d\u7f6e", "resize": "\u62d6\u52a8\u63a7\u5236\u67c4\u7f29\u653e", "desc": ["\u5f00\u59cb\u524d\u786e\u8ba4\u6444\u50cf\u5934\u4f4d\u7f6e\u4e0e\u5c3a\u5bf8\u3002", "\u628a\u6444\u50cf\u5934\u79fb\u5230\u4e0d\u6321\u4f4f\u64cd\u4f5c\u7684\u4f4d\u7f6e\u3002", "\u518d\u7f29\u653e\u753b\u9762\uff0c\u68c0\u67e5\u662f\u5426\u906e\u4f4f\u91cd\u8981\u63a7\u4ef6\u3002"], "buttons": ["\u987a\u65f6\u9488\u65cb\u8f6c", "\u9006\u65f6\u9488\u65cb\u8f6c", "\u6c34\u5e73\u7ffb\u8f6c", "\u5782\u76f4\u7ffb\u8f6c"]}, "en": {"title": "Move and resize the webcam", "label": "Instructional illustration", "region": "Recording area (before start)", "webcam": "Webcam", "move": "Drag to move", "resize": "Drag the handle to resize", "desc": ["Check webcam position and size before recording.", "Move the webcam away from important actions.", "Then resize and check for covered controls."], "buttons": ["Rotate clockwise", "Rotate counterclockwise", "Flip horizontally", "Flip vertically"]}}


def text(x, y, s, size=24, color='#24344d', weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(s)}</text>'


def box(x, y, w, h, fill='#edf6ff', stroke='#8bbcff', rx=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def arrow(x1, y1, x2, y2):
    return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#1677ff" stroke-width="4" marker-end="url(#a)" fill="none"/>'


root = Path(__file__).resolve().parents[1] / 'docs/public/images/guides'
for locale, words in STRINGS.items():
    out = root / ('en' if locale == 'en' else '')
    out.mkdir(parents=True, exist_ok=True)
    for phase in range(1, 4):
        x = 85 if phase == 1 else 610
        side = 130 if phase < 3 else 190
        y = 220 if phase < 3 else 160
        b = box(40, 112, 820, 275) + text(65, 149, words['region'])
        b += box(x, y, side, side, '#d1e5f8', '#1677ff', 10) + text(x + 15, y + 50, words['webcam'])
        # The actual resize control is inside the preview's upper-right corner.
        b += f'<rect x="{x+side-16}" y="{y+2}" width="14" height="14" fill="white" stroke="#1677ff" stroke-width="3"/>'
        # Show just the four known orientation controls in their released order.
        tx = x + (side - 124) / 2
        ty = y - 40
        for i, inner in enumerate(GLYPHS):
            gx = tx + i * 32
            b += box(gx, ty, 28, 28, '#fff', '#b9cde8', 5)
            b += f'<svg x="{gx+4}" y="{ty+4}" width="20" height="20" viewBox="0 0 1024 1024" fill="#24344d" color="#24344d"><title>{escape(words["buttons"][i])}</title>{inner}</svg>'
        if phase == 2:
            b += arrow(210, 285, 588, 255) + text(304, 220, words['move'], 26)
        if phase == 3:
            # Enlargement keeps bottom-left fixed; upper-right moves up/right.
            b += arrow(744, 218, 793, 169) + text(420, 379, words['resize'], 25)
        title = words['title']
        desc = words['desc'][phase - 1]
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="470" viewBox="0 0 900 470" role="img" aria-labelledby="title desc">'
               f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>'
               '<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#1677ff"/></marker></defs>'
               '<rect width="900" height="470" rx="20" fill="#fff"/><g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif">'
               f'{text(30,47,title,30,"#163963",700)}{text(30,79,words["label"],18,"#62758e")}{b}{text(30,444,desc,20,"#52647e")}</g></svg>')
        (out / f'rec-webcam-drag-{phase}.svg').write_text(svg + '\n', encoding='utf-8')
