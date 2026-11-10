#!/usr/bin/env python3
"""Draw dedicated clipboard-append and split-replacement teaching states."""
from pathlib import Path
from html import escape
import csv
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/public/images/guides'
COLORS=['#f3d0d7','#cde8c9','#c5dbf3','#bdebe5','#f7e8b3','#dfcff0']
def t(x,y,v,size=22,color='#233a5b',weight=400,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(v)}</text>'
def box(x,y,w,h,fill='#fff',stroke='#c7d4e7',radius=12,dash=False):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"'+(' stroke-dasharray="7 5"' if dash else '')+'/>'
def wrap(x,y,s,width=500,size=21,line_height=30):
    # Keep word boundaries, including one-letter words, while wrapping CJK individually.
    tokens=re.findall(r'[A-Za-z0-9]+(?:[+./×_-][A-Za-z0-9]+)*|[^\x00-\x7f]|\s+|.',s) if any('\u4e00'<=c<='\u9fff' for c in s) else re.findall(r'\S+\s*',s)
    lines=[];cur='';length=0
    for token in tokens:
        n=sum(size*(1 if ord(c)>255 else .55) for c in token)
        if cur and length+n>width:
            lines.append(cur.rstrip());cur='';length=0
        cur+=token;length+=n
    if cur:lines.append(cur.rstrip())
    return ''.join(t(x,y+i*line_height,line,size) for i,line in enumerate(lines))
def arrow(x1,y1,x2,y2):
    return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#487bd0" stroke-width="4" marker-end="url(#arrow)"/>'
def image_tile(x,y,w,h,name,color=0,turned=False):
    s=box(x,y,w,h,COLORS[color%len(COLORS)],'#8fa7c8',7)
    if turned:
        cx,cy=x+w/2,y+h/2
        s+=f'<g transform="translate({cx} {cy}) rotate(90)">'+t(-22,9,'F',36,'#345075',700)+arrow(19,20,19,-25)+'</g>'
    else:s+=t(x+w/2,y+h/2+12,name,32,'#345075',600,'middle')
    return s

def old_image(x=150,y=190):
    s=''
    for row in range(2):
        for col in range(3):
            i=row*3+col;s+=box(x+col*100,y+row*100,100,100,COLORS[i],'#fff',0)+t(x+col*100+50,y+row*100+62,chr(65+i),34,anchor='middle')
    return s+f'<path d="M{x+120} {y}V{y+200}" stroke="#387bcf" stroke-width="3" stroke-dasharray="7 5"/>'
def new_image(x=200,y=210,w=200,h=160):
    return image_tile(x,y,w/2,h,'G',2)+image_tile(x+w/2,y,w/2,h,'H',4)
def badge(x,y,text_value,w=200):return box(x,y,w,38,'#ecf3fe','#9db8e0',7)+t(x+w/2,y+27,text_value,20,'#325a92',600,'middle')
rows=[]
for locale in ('zh','en'):
    en=locale=='en'
    ct=['Copy an image, then Paste','The image is appended','Readable file lists keep order','PDF appends keep prior transforms'] if en else ['复制图像后，返回拼接粘贴','图片会追加到已有拼接','可读文件列表保留顺序与重复项','PDF 追加保留已有变换']
    ca=['Keep the existing A. Copy image B, focus the stitching preview, then press Ctrl+V (Mac: Command+V).','B is appended. The existing A and its rotation remain. Paste does not replace the selected image.','When the clipboard provides local image paths B, C, B, Paste appends them in order and keeps duplicates.','In a two-image PDF template, Paste fills the next cell. The existing A keeps its rotation and placement.'] if en else ['保留已有图片 A。复制图片 B，回到拼接预览，按 Ctrl+V（Mac 为 Command+V）。','B 追加到已有图片后。A 及其旋转保持；粘贴不会替换当前选中的图片。','剪贴板提供可读图片路径 B、C、B 时，按顺序追加三张，重复的 B 也会保留。','两图 PDF 模板中，粘贴把 B 加入下一个格子；已有 A 的旋转和位置保持。']
    st=['Paste into an empty split window','Review replacement before accepting','Cancel keeps the old image and cuts','Accept loads the new image'] if en else ['空分割窗口可直接粘贴','已有图片时，先决定是否替换','取消后保留原图与旧切线','确认后载入新图，重查切线']
    sa=['Paste image pixels or readable local image paths. With a file list, only the first supported image is read.','The current image has a manual cut at x=120. Pasting a new image asks whether to discard those edits.','Cancel replacement. The 300×200 image, manual cut at x=120, and current layout remain.','Accept replacement to load the 200×160 input. Old split edits and history are reset; check the new cut lines.'] if en else ['粘贴图像像素或可读的本地图片路径；文件列表只读第一张支持的图片，不会逐张开窗。','当前图片有 x=120 的手动切线。粘贴新图时，先确认是否舍弃当前分割编辑。','取消这次替换，300×200 原图、x=120 手动切线和当前布局都保留。','确认替换，载入 200×160 新图。旧分割编辑和历史不保留，重新检查新图切线。']
    for family in ('collage','split'):
      for index in range(1,5):
        title=(ct if family=='collage' else st)[index-1];action=(ca if family=='collage' else sa)[index-1]
        body=t(24,43,title,25,'#203858',700)+box(24,98,552,398)
        if family=='collage':
          if index in (1,2):
            body+=t(48,134,('Current collage' if en else '当前拼接'),21)
            body+=image_tile(52,168,192,118,'A',0,True)+t(148,319,'A · 90°',21,anchor='middle')
            if index==1:
                body+=box(330,168,210,118,'#f6f9fd','#a8bbd7',7,True)+t(435,223,'Not added yet' if en else '尚未加入',19,anchor='middle')
                body+=image_tile(108,356,138,92,'B',2)+badge(300,378,'Ctrl+V / ⌘V',228)+t(48,478,'Clipboard: image B' if en else '剪贴板：图片 B',20)
            else:
                body+=image_tile(330,168,210,118,'B',2)+t(435,319,'B',21,anchor='middle')+badge(70,385,'A unchanged' if en else 'A 保持原样',220)+badge(318,385,'B appended' if en else 'B 已追加',220)
          elif index==3:
            body+=t(48,135,'Clipboard file order' if en else '剪贴板文件列表顺序',21)
            for c,name in enumerate(('B','C','B')):body+=image_tile(55+c*174,158,140,74,name,{'B':2,'C':1}[name])
            body+=arrow(300,251,300,286)+t(48,328,'After Paste: A, B, C, B' if en else '粘贴后：A、B、C、B',21)
            for c,name in enumerate(('A','B','C','B')):body+=image_tile(48+c*134,355,102,94,name,{'A':0,'B':2,'C':1}[name], c==0)
          else:
            body+=t(44,132,'PDF: two-image template' if en else 'PDF：两图模板',21)
            for c,label in enumerate(('Before','After') if en else ('追加前','追加后')):
                x=46+c*290;body+=t(x+103,170,label,21,anchor='middle')+box(x,188,210,262,'#fff','#9fb1cb',3)
                body+=box(x+13,200,184,112,'#f9fbff','#cbd7e7',3)+box(x+13,326,184,112,'#f9fbff','#cbd7e7',3)
                body+=image_tile(x+34,221,130,69,'A',0,True)
                if c:body+=image_tile(x+35,345,140,75,'B',2)
            body+=t(48,480,'A retains rotation and position' if en else 'A 的旋转与位置均保留',20)
        else:
          if index==1:
            body+=t(44,134,'Clipboard input' if en else '剪贴板输入',21)
            body+=new_image(60,150,125,100)+t(123,276,'Image B pixels' if en else '图像 B 像素',19,anchor='middle')
            body+=box(318,158,232,90,'#f7faff')+t(434,195,'Paths: B, C' if en else '本地路径 B、C',23,anchor='middle')+t(434,228,'Read B only' if en else '只读取 B',18,anchor='middle')
            body+=arrow(300,284,300,316)+new_image(210,332,180,144)
          elif index in (2,3):
            body+=t(44,133,('Existing image · 300×200 px' if en else '已有图片 · 300×200 px'),21)
            body+=old_image(150,172)+t(44,405,'Manual cut: x=120' if en else '手动切线：x=120',21)
            body+=badge(83,437,('Review replacement' if index==2 else 'Canceled: unchanged') if en else ('等待替换决定' if index==2 else '已取消：原样保留'),434)
          else:
            body+=t(44,134,'New input · 200×160 px' if en else '新输入 · 200×160 px',21)+new_image(200,181)
            body+=badge(65,378,'Old split history reset' if en else '旧分割历史已重置',470)+t(44,461,'Check new cut positions' if en else '重新检查新图的切线位置',21)
        body+=box(24,516,552,144,'#fff','#d2dced')+wrap(44,548,action)+t(24,694,'Instructional illustration' if en else '操作示意',19,'#5a6c86')+t(548,694,f'{index}/4',19,'#5a6c86',anchor='end')
        svg='<svg xmlns="http://www.w3.org/2000/svg" width="600" height="720" viewBox="0 0 600 720" role="img"><title>'+escape(title)+'</title><desc>'+escape(action)+'</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#487bd0"/></marker></defs><rect width="600" height="720" rx="20" fill="#f4f7fc"/><g font-family="Arial,PingFang SC,Microsoft YaHei,sans-serif">'+body+'</g></svg>\n'
        rel=f'{"en/" if en else ""}img-paste-{family}-{index}.svg';p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(svg)
        page='collage' if family=='collage' else 'split';fid='IMG-044' if family=='collage' else 'IMG-050'
        rows.append({'Asset':'docs/public/images/guides/'+rel,'Feature IDs':fid,'Teaching purpose':title,'Documentation path':f'docs/{locale}/guides/image-editing/{page}.mdx','Associated step':f'{index}/4: {action}','Source':'f02f50e:snow_shot/src/presentation/'+('collage/collagewindow.cpp:306-323,501-505,1381-1411' if family=='collage' else 'imagesplit/imagesplitwindow.cpp:333-352,1114-1164')+';snow_shot/tests/image_paste_tests.cpp:140-263;artifacts/operation-candidates-image-review-20261110.json','Production method':'Dedicated original SVG of clipboard input/append or replacement decision semantics, generated by scripts/generate-guide-paste-teaching-assets.py. No application toolbar/dialog is reconstructed. Instructional illustration only.','Status':'Produced; source-grounded illustration. Visual/site review pending; no native pass attributed.','Capture prerequisites and next action':'Root may review source/diagram geometry and browser controls. Ordinary clipboard paste and replacement confirmation still require scoped native verification. No previous file-open or mode-selection pass is inherited.'})
registry = ROOT/'artifacts/assets-paste-teaching-20261110.csv'
# Keep independently captured native rows when regenerating these SVG illustrations.
if registry.exists():
    generated = {row['Asset'] for row in rows}
    with registry.open() as stream:
        rows.extend(row for row in csv.DictReader(stream) if row['Asset'] not in generated)
with registry.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Generated',len(rows),'bilingual paste teaching SVGs')
