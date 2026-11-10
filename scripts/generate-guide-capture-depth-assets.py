#!/usr/bin/env python3
"""Generate focused capture instruction flows; no simulated application chrome."""
from pathlib import Path
from html import escape
import re
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/public/images/guides'
DELETE = 'M360 184h-8c4.4 0 8-3.6 8-8v8h304v-8c0 4.4 3.6 8 8 8h-8v72h72v-80c0-35.3-28.7-64-64-64H352c-35.3 0-64 28.7-64 64v80h72v-72zm504 72H160c-17.7 0-32 14.3-32 32v32c0 4.4 3.6 8 8 8h60.4l24.7 523c1.6 34.1 29.8 61 63.9 61h454c34.2 0 62.3-26.8 63.9-61l24.7-523H888c4.4 0 8-3.6 8-8v-32c0-17.7-14.3-32-32-32zM731.3 840H292.7l-24.2-512h487l-24.2 512z'
def width(s): return sum(1 if ord(c)>255 else .53 for c in s)
def lines(s, limit=43):
    tokens=re.findall(r'[A-Za-z0-9×%+–→≠.]+|\s+|.',s)
    out=[]; cur=''
    for token in tokens:
        if width(cur+token)>limit and cur.strip():
            if token in '，。！？；：、）”': cur+=token; continue
            out.append(cur.rstrip());cur=token.lstrip()
        else:cur+=token
    if cur.strip():out.append(cur.rstrip())
    return out
class Figure:
    def __init__(self,title,h,english=False):
        self.h=h;self.en=english
        self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="{h}" viewBox="0 0 600 {h}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title>', '<g font-family="Arial, PingFang SC, Microsoft YaHei, sans-serif">',f'<rect x="1" y="1" width="598" height="{h-2}" rx="14" fill="#f6f7fc" stroke="#cbd4e4"/>']
        self.text(28,41,title,27,limit=36)
    def box(self,x,y,w,h,fill='#ffffff',stroke='#cbd4e4'):
        self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    def text(self,x,y,s,size=22,color='#263148',limit=43):
        for i,line in enumerate(lines(s,limit)):
            self.s.append(f'<text x="{x}" y="{y+i*(size+6)}" font-size="{size}" fill="{color}">{escape(line)}</text>')
    def arrow(self,y):self.s.append(f'<path d="M300 {y}v20m-7-7 7 7 7-7" fill="none" stroke="#7652dc" stroke-width="3"/>')
    def finish(self,path):
        self.text(28,self.h-23,'Instructional illustration' if self.en else '操作示意',18,'#536078')
        self.s.append('</g></svg>');path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(self.s)+'\n')
def presets(en):
    f=Figure('Presets and Cancel have separate scopes' if en else '预设确认与取消调整的不同范围',1160,en)
    for y in [90,340,590,840]:f.box(26,y,548,220)
    for y in [314,564,814]:f.arrow(y)
    if en:
        titles=['1. Confirm Add preset separately','2. Hover a saved preset to delete','3. Read the delete confirmation','4. Cancel the size adjustment']
        cover,old='Cover','Old cover'
    else:titles=['1. 单独确认添加预设','2. 悬停命名预设，找到删除图标','3. 先读删除确认','4. 取消选区尺寸调整'];cover,old='封面','旧封面'
    for title,y in zip(titles,[125,375,625,875]):f.text(46,y,title,24,limit=39)
    f.text(46,166,'Selection: 640 × 360' if en else '画面选区：640 × 360')
    f.text(46,201,'Fields: 800 × 450 (not applied)' if en else '调整字段：800 × 450（尚未应用）')
    f.box(44,224,512,65,'#e9f5ef','#9ccbb1')
    f.text(58,251,'Add preset → Name: Cover → Add' if en else '添加预设 → 名称：封面 → 添加',21,limit=43)
    f.text(58,278,'Cover is now saved.' if en else '“封面”现已保存。',20,'#256145')
    f.text(46,410,'Quick set' if en else '快速设置',20,'#536078')
    f.box(44,425,512,48,'#ebe6fb','#7652dc');f.text(58,456,old,22)
    f.s.append(f'<g transform="translate(509 433) scale(.03125)" fill="#c53b4c"><path d="{DELETE}"/></g>')
    f.box(44,481,512,42);f.text(58,509,cover,22)
    f.text(46,550,'The delete icon appears on hover.' if en else '悬停预设行时，右侧出现删除图标。',20,limit=46)
    f.text(46,670,'Delete preset "Old cover"?' if en else '删除预设“旧封面”？',22)
    f.text(46,702,'This action cannot be undone.' if en else '此操作无法撤销。',21,'#b53849')
    f.text(46,744,'Delete → Remove; Cancel → Keep' if en else '删除 → 移除预设　取消 → 保留预设',21,limit=46)
    f.text(46,776,'Confirm Delete to continue below.' if en else '以下结果以已确认“删除”为例。',19,'#536078',limit=49)
    f.text(46,922,'Selection remains 640 × 360.' if en else '选区仍为 640 × 360。',22)
    f.text(46,959,'Cover (800 × 450) remains saved.' if en else '“封面”（800 × 450）仍然保留。',22,limit=43)
    f.text(46,996,'Old cover does not return.' if en else '已确认删除的“旧封面”不会恢复。',22,limit=43)
    f.text(46,1033,'Cancel does not undo preset changes.' if en else '取消尺寸调整，不会撤销预设操作。',20,'#7652dc',limit=46)
    f.finish(OUT/('en/' if en else '')/'cap-preset-commit-scopes.svg')
def scrolling(en):
    f=Figure('Changing scrolling capture settings' if en else '更改滚动截图设置后会重新采集',1000,en)
    for y,h in [(90,245),(370,250),(655,270)]:f.box(26,y,548,h)
    for y in [339,624]:f.arrow(y)
    f.text(46,125,'1. Decide whether to keep the result' if en else '1. 先决定是否需要保留当前结果',24,limit=40)
    f.text(46,164,'A stitched image already has a trim.' if en else '已有拼接长图，并设置了首尾裁剪。',21,limit=45)
    f.box(48,185,166,125,'#ffffff','#7652dc')
    for i in range(6):f.s.append(f'<path d="M65 {204+i*17}h132" stroke="#cbd4e4" stroke-width="4"/>')
    f.s.append('<path d="M48 219h166M48 285h166" stroke="#d15a45" stroke-width="3" stroke-dasharray="6 4"/>')
    f.text(238,223,'Need it? Save as file' if en else '需要保留？保存为文件',22,limit=24)
    f.text(238,267,'Then start a new capture' if en else '保存后重新开始截图',21,'#536078',limit=24)
    f.text(46,405,'2. Open Settings on the scroll toolbar' if en else '2. 打开滚动工具条上的“设置”',23,limit=40)
    f.text(46,449,'Capture UI during scrolling screenshots' if en else '滚动截图时捕获界面',22,limit=42)
    f.text(46,490,'Includes Snow Shot’s own toolbar and preview.' if en else '控制是否捕获 Snow Shot 工具条和缩略预览。',21,limit=43)
    f.text(46,554,'Change the switch → OK' if en else '更改开关 → 确定',22,'#7652dc',limit=42)
    f.text(46,590,'Cancel leaves the setting unchanged.' if en else '取消则不更改此设置。',20,'#536078',limit=47)
    f.text(46,690,'3. Capture starts again' if en else '3. 从新的采集结果重新开始',24,limit=40)
    f.text(46,734,'Old stitching and trim are cleared.' if en else '原拼接结果和首尾裁剪范围清空。',22,limit=43)
    f.text(46,775,'Region and direction stay the same.' if en else '捕获选区和滚动方向保持不变。',22,limit=43)
    f.text(46,817,'Wait for a new preview, then scroll again.' if en else '等待新预览出现，再重新滚动采集。',22,limit=43)
    f.text(46,879,'OK without a change does not restart.' if en else '未更改开关直接确定，不会重新采集。',20,'#536078',limit=47)
    f.finish(OUT/('en/' if en else '')/'cap-scrolling-settings-reset.svg')
for en in [False,True]:presets(en);scrolling(en)
print('4 focused SVGs generated')
def wheel_resize(en):
    f=Figure('Scroll to adjust the selection bounds' if en else '在画布滚动，围绕中心调整四边',880,en)
    f.text(30,83,'Move · One confirmed rectangle · No drag' if en else '移动工具 · 已确认单个矩形 · 未拖动',20,'#536078',limit=47)
    for top,expanded in [(110,False),(420,True)]:
        f.box(26,top,548,270)
        f.text(46,top+35,('After scrolling' if expanded else 'Before scrolling') if en else ('滚动后' if expanded else '滚动前'),24)
        oy=top+65
        f.box(54,oy,492,170,'#f4f6fb')
        # Fixed content and center share identical panel-relative coordinates.
        f.s.append(f'<path d="M114 {oy+48}h360M114 {oy+122}h360" stroke="#d2d8e5" stroke-width="7"/>')
        f.text(203,oy+90,'A',24);f.text(374,oy+90,'B',24)
        f.s.append(f'<rect x="200" y="{oy+40}" width="200" height="100" fill="none" stroke="#9ca7be" stroke-width="2" stroke-dasharray="6 5"/>')
        d=20 if expanded else 0
        f.s.append(f'<rect x="{200-d}" y="{oy+40-d}" width="{200+2*d}" height="{100+2*d}" fill="none" stroke="#7652dc" stroke-width="3"/>')
        f.s.append(f'<path d="M292 {oy+90}h16M300 {oy+82}v16" stroke="#7652dc" stroke-width="2"/>')
        if expanded:
            for x,y,dx,dy in [(180,oy+90,-18,0),(420,oy+90,18,0),(300,oy+20,0,-8),(300,oy+160,0,8)]:
                f.s.append(f'<path d="M{x} {y}l{dx} {dy}" stroke="#c5503e" stroke-width="3"/>')
        f.text(46,top+260,('Center and image content stay fixed.' if expanded else 'The locked ratio does not constrain this action.') if en else ('中心和底图内容位置不变。' if expanded else '比例锁不会约束这一滚轮操作。'),20,'#536078',limit=47)
    f.arrow(387)
    f.text(30,736,'All four edges move equally; the ratio may change.' if en else '四边等量调整，宽高比可能改变。',22,limit=45)
    f.text(30,782,'Reverse the scroll to adjust back. Check the size readout.' if en else '反向滚动即可调回；以宽高读数和边界为准。',21,limit=46)
    f.finish(OUT/('en/' if en else '')/'cap-wheel-selection-bounds.svg')
def wheel_candidates(en):
    f=Figure('Choose a Smart Selection candidate' if en else '智能框选：用滚轮选择候选范围',1030,en)
    f.text(30,83,'Tab: Window ↔ Child elements' if en else 'Tab：整窗 ↔ 子元素模式',22,'#7652dc',limit=45)
    f.text(30,117,'Wheel: adjacent detected bounds in child-element mode' if en else '滚轮：在子元素模式的候选层级间切换',20,limit=48)
    names=['Button candidate','Panel candidate','Window candidate'] if en else ['按钮候选','面板候选','整窗候选']
    for i,y in enumerate([150,405,660]):
        f.box(26,y,548,225)
        f.text(46,y+34,names[i],23)
        for j,(x,ry,w,h) in enumerate([(60,53,480,145),(100,82,370,98),(200,112,150,48)]):
            active=j==2-i
            f.s.append(f'<rect x="{x}" y="{y+ry}" width="{w}" height="{h}" rx="4" fill="none" stroke="{("#7652dc" if active else "#bac4d8")}" stroke-width="{3 if active else 1.5}"/>')
        f.s.append(f'<path d="M270 {y+135}l0 23 6-6 6 10 5-3-6-10h10z" fill="#263148"/>')
        f.text(46,y+220,'Same pointer position' if en else '指针位置保持不变',18,'#536078',limit=48)
    f.text(30,928,'Scroll to another candidate; reverse to go back.' if en else '滚动查看相邻候选，反向滚动返回。',22,limit=44)
    f.text(30,968,'Available bounds depend on the target app.' if en else '实际可选层级由目标应用提供的信息决定。',20,'#536078',limit=47)
    f.finish(OUT/('en/' if en else '')/'cap-wheel-smart-candidates.svg')
for en in [False,True]:wheel_resize(en);wheel_candidates(en)
print('4 wheel comparison SVGs generated')
