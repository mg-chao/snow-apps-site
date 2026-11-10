#!/usr/bin/env python3
"""Generate source-coordinate examples for image split direction selection."""
from pathlib import Path
from html import escape
import argparse

parser=argparse.ArgumentParser()
parser.add_argument('--output-root', type=Path, default=Path(__file__).resolve().parents[1])
args=parser.parse_args()
def text(x,y,value,size=19,color='#273957',weight='400',anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'
def rect(x,y,w,h,fill,stroke='#cbd5e4',radius=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'
def line(x1,y1,x2,y2):
    return f'<path d="M{x1} {y1}H{x2}" stroke="#e85b6b" stroke-width="3" stroke-dasharray="7 5"/>' if y1==y2 else f'<path d="M{x1} {y1}V{y2}" stroke="#e85b6b" stroke-width="3" stroke-dasharray="7 5"/>'
for lang in ('zh','en'):
    zh=lang=='zh'
    title='选择切线方向，再设置数量或尺寸' if zh else 'Choose the cut direction before setting size'
    subtitle='同一张 300 × 180 px 图片；以下示例的重叠宽度均为 0。' if zh else 'One 300 × 180 px source. All examples use zero overlap.'
    labels=['垂直','水平','网格'] if zh else ['Vertical','Horizontal','Grid']
    hints=['竖切线 → 左右片','横切线 → 上下片','行与列 → 二维切片'] if zh else ['Vertical cuts → left/right','Horizontal cuts → top/bottom','Rows and columns → grid']
    inputs=['精确分割：宽度 100 px','精确分割：高度 60 px','2 行 × 3 列'] if zh else ['Precise: width 100 px','Precise: height 60 px','2 rows × 3 columns']
    results=['3 张，每张 100 × 180 px','3 张，每张 300 × 60 px','6 张，每张 100 × 90 px'] if zh else ['3 images: 100 × 180 px each','3 images: 300 × 60 px each','6 images: 100 × 90 px each']
    pieces=[rect(0,0,960,560,'#f5f7fc','none',20),text(28,42,title,28,'#182e50','700'),text(28,79,subtitle,19,'#53647c')]
    colors=['#e9ddff','#d7eefc','#d9f2e7','#ffe9c8','#f8dfec','#dfebff']
    for col in range(3):
        x=26+col*310
        pieces += [rect(x,108,288,378,'#fff'),rect(x+17,126,254,35,'#eef3fc','none',7),text(x+29,151,labels[col],23,'#334e78','700')]
        # The displayed 240×144 area is exactly 0.8 of the 300×180 source.
        ox,oy=x+24,188
        rows,cols=(1,3) if col==0 else (3,1) if col==1 else (2,3)
        cw,ch=240/cols,144/rows
        for row in range(rows):
            for c in range(cols):
                n=row*cols+c
                pieces += [rect(ox+c*cw,oy+row*ch,cw,ch,colors[n],'#fff',0),text(ox+(c+.5)*cw,oy+(row+.5)*ch+8,str(n+1),25,'#31425e','600','middle')]
        pieces.append(rect(ox,oy,240,144,'none','#8b9bb2',0))
        for c in range(1,cols):pieces.append(line(ox+c*cw,oy,ox+c*cw,oy+144))
        for row in range(1,rows):pieces.append(line(ox,oy+row*ch,ox+240,oy+row*ch))
        pieces += [text(x+18,369,hints[col],18,'#4b5e7c'),text(x+18,407,inputs[col],19,'#2d4773','600'),text(x+18,450,results[col],17,'#4b5e7c')]
    footer='操作示意 · 长图按高度分段时选择“水平”；网格只按行列设置。' if zh else 'Instructional illustration · Use Horizontal for height. Grid uses row/column counts.'
    pieces.append(text(28,530,footer,18,'#53647c'))
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="560" viewBox="0 0 960 560" role="img"><title>{escape(title)}</title><g font-family="Arial, PingFang SC, Microsoft YaHei, sans-serif">'+''.join(pieces)+'</g></svg>\n'
    target=args.output_root/'docs/public/images/guides'/('' if zh else 'en')/'img-split-directions.svg'
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(svg)
    print(target)
