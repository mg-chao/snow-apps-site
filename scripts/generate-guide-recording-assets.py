# -*- coding: utf-8 -*-
from pathlib import Path
from html import escape

root = Path(__file__).resolve().parents[1] / 'docs/public/images/guides'
root.mkdir(parents=True, exist_ok=True)

def text(x,y,s,size=24,color='#24344d',weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(s)}</text>'

def box(x,y,w,h,fill='#f2f6fc',stroke='#cbd8e9',rx=16):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'

def arrow(x1,y1,x2,y2,color='#1677ff'):
    return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="4" marker-end="url(#a)" fill="none"/>'

def badge(x,y,n):
    return f'<circle cx="{x}" cy="{y}" r="20" fill="#1677ff"/>{text(x-7,y+8,str(n),24,"white",700)}'

def panel(x,y,w,h,label,n):
    return box(x,y,w,h)+badge(x+28,y+30,n)+text(x+58,y+39,label,24,'#163963',600)

def save(name,title,body,desc):
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="470" viewBox="0 0 900 470" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#1677ff"/></marker></defs>
<rect width="900" height="470" rx="20" fill="#fff"/>
<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif">{text(30,47,title,30,'#163963',700)}{text(30,79,'教学示意 · 非应用截图或录屏',18,'#62758e')}{body}{text(30,444,desc,20,'#52647e')}</g></svg>'''
    (root/name).write_text(svg,encoding='utf-8')

b=panel(30,112,405,265,'两种音源分别确认',1)+panel(465,112,405,265,'摄像头布局',3)
b+=text(60,202,'麦克风 → 人声')+badge(78,252,2)+text(112,261,'系统音频 → 电脑声')
b+=box(65,289,325,28,'#e0f4e8','#bedbc8',6)+box(68,292,213,22,'#36a76a','#36a76a',4)
b+=text(65,352,'悬停调增益：-24 ~ +24 dB',21)
b+=box(490,175,352,174,'#edf6ff','#8bbcff',8)+box(707,237,110,110,'#d7eafa','#1677ff',8)
b+=text(715,292,'摄像头',23)+arrow(720,241,648,197)+text(501,211,'拖动位置',21)+text(500,369,'缩放 · 方形/圆形 · 旋转翻转',20)
save('rec-audio-camera.svg','声音与摄像头准备',b,'MP4 支持声音；动图格式无音频。先确认预览，再开始。')

b=panel(30,112,405,265,'鼠标效果',1)+panel(465,112,405,265,'按键与后处理',3)
b+='<path d="M70 300Q140 180 225 240T340 220" fill="none" stroke="#75c8ff" stroke-width="12" stroke-linecap="round"/>'
b+='<circle cx="330" cy="220" r="45" fill="#ffe565" opacity=".55"/><circle cx="330" cy="220" r="22" fill="none" stroke="#f06d64" stroke-width="5"/><path d="M322 200L346 226L334 227L330 240Z" fill="#24344d"/>'
b+=badge(366,275,2)+text(65,353,'高亮 / 点击 / 滚动 / 拖尾',23)
b+=box(525,204,260,62,'#24344d','#24344d',10)+text(557,245,'Ctrl + Shift + S',25,'white')
b+=badge(510,320,4)+box(550,299,250,20,'#e3ebf5','#e3ebf5',4)+box(551,300,153,18,'#1677ff','#1677ff',4)
b+=text(526,358,'选择输入类别与进度提示',22)
save('rec-effects.svg','让观众看清操作位置',b,'效果在录制前配置；颜色、半径和按键大小分别调整。')

b=panel(30,112,263,265,'复制',1)+panel(318,112,263,265,'另存为',2)+panel(606,112,263,265,'快速保存',3)
for x,s1,s2 in [(55,'剪贴板','到目标应用粘贴'),(343,'本次路径与参数','确认文件名再保存'),(631,'预设目录和格式','直接生成文件')]:
    b+=box(x,196,213,76,'#fff','#9fc2ee',12)+text(x+16,241,s1,23)+arrow(x+105,281,x+105,313)+text(x+3,350,s2,22)
save('out-copy-save.svg','按需要选择输出方式',b,'复制图像、保存文件和打印/分享分别取得不同结果。')

b=panel(30,112,405,265,'来源与日期',1)+panel(465,112,405,265,'核对后操作',3)
b+=box(60,183,344,56,'#fff','#a9c8ee',8)+text(77,219,'来源：复制 / 文件 / 贴图',22)
b+=badge(84,284,2)+text(117,292,'开始日期 → 结束日期',23)
b+=text(62,346,'没有结果时先放宽筛选',22)
for x,y in [(495,183),(660,183),(495,269),(660,269)]:
    b+=box(x,y,144,65,'#fff','#b9cde8',7)+text(x+13,y+40,'截图记录',22)
b+=text(497,361,'预览 / 复制 / 保存 / 批处理',21)
save('out-history.svg','从历史中找回截图',b,'全选针对当前页；删除前核对选择数量与不可撤销提示。')

b=panel(30,112,263,265,'默认配置',1)+panel(318,112,263,265,'上传图像',2)+panel(606,112,263,265,'链接',3)
b+=text(54,208,'S3 端点 · 区域',24)+text(54,251,'存储桶 · 凭据',24)+text(54,307,'选择默认目标',24)
b+=box(346,193,206,126,'#e9f5ed','#9dceb0',12)+text(362,239,'准备 → 上传',24)+text(362,285,'等待进度完成',23)
b+=text(633,210,'复制对象 URL',24)+text(633,260,'浏览器验证访问',23)+text(633,310,'再分享给对方',23)
b+=arrow(290,250,317,250)+arrow(580,250,606,250)
save('out-cloud-upload.svg','上传成功后取得链接',b,'写入成功与公开读取是两件事；读取遵循存储桶/CDN 策略。')

b=panel(30,112,263,265,'全局快捷键',1)+panel(318,112,263,265,'应用快捷键',2)+panel(606,112,263,265,'全局鼠标',3)
b+=text(52,208,'其他应用前台',24)+box(54,239,210,53,'#fff','#9fc2ee',8)+text(74,274,'组合键 → 任务',23)+text(52,344,'检查注册状态',24)
b+=text(341,208,'当前工具内',24)+box(342,239,210,53,'#fff','#9fc2ee',8)+text(360,274,'按键 → 操作',23)+text(341,344,'注意焦点与状态',23)
b+=text(628,208,'按住激活键',24)+arrow(645,256,810,302)+text(628,344,'指定鼠标键拖动',23)
save('set-shortcuts.svg','先分清快捷操作的范围',b,'设置 → 录入组合 → 确定 → 检查状态 → 实际调用。')

b=panel(30,112,263,265,'选表面',1)+panel(318,112,263,265,'图片与位置',2)+panel(606,112,263,265,'共用参数',3)
b+=text(53,211,'主界面',25)+text(53,265,'工具栏',25)+text(53,319,'自定义托盘菜单',23)
b+=box(347,187,204,131,'#dcecf8','#9fc2ee',8)+box(365,203,121,96,'#a1c5df','#a1c5df',5)+text(350,353,'PNG / JPG / WebP',21)
b+=text(630,204,'叠加 / 完整显示',23)+text(630,250,'图片不透明度',23)+text(630,296,'模糊与遮罩',23)+text(630,343,'保持文字清晰',23)
save('set-appearance.svg','皮肤与界面可读性',b,'三个表面可独立选图；系统原生菜单仍使用系统外观。')

b=panel(30,112,263,265,'拖到旁边',1)+panel(318,112,263,265,'拖到上方',2)+panel(606,112,263,265,'拖入隐藏区',3)
for x in [55,125,195]: b+=box(x,236,54,54,'#fff','#8bbcff',7)
b+=text(68,273,'A',24)+text(138,273,'B',24)+text(208,273,'C',24)+arrow(160,185,160,227)+text(52,347,'创建独立位置',24)
b+=box(393,190,75,54,'#e6f0ff','#1677ff',7)+text(419,227,'A',24)+box(393,246,75,54,'#fff','#1677ff',7)+text(419,283,'B',24)+text(342,347,'底部 B 留在主行',22)
b+=box(633,260,206,73,'#edf0f5','#a6b6cb',8)+text(658,306,'隐藏工具',24)+arrow(735,184,735,250)
save('set-toolbars-tray.svg','工具栏的三种拖放结果',b,'隐藏的工具可以拖回预览；叠放组可展开选择其他工具。')

b=panel(30,112,263,265,'查看状态',1)+panel(318,112,263,265,'配置备份',2)+panel(606,112,263,265,'分类清理',3)
b+=text(54,209,'目录 / 模式 / 错误',22)+text(54,261,'历史 / 贴图 / OCR',22)+text(54,314,'临时录屏占用',23)
b+=text(341,209,'导出 → ZIP',24)+arrow(437,227,437,265)+text(341,303,'粘贴保存归档',23)+text(341,350,'导入会替换设置',21)
b+=text(630,209,'历史保留限制',23)+text(630,261,'已关闭贴图',23)+text(630,313,'录屏临时文件',23)
save('set-storage-backup.svg','先识别占用再清理',b,'日志 ZIP 用于诊断；配置 ZIP 用于恢复设置，不能互相替代。')

b=panel(30,112,405,265,'网络连接路径',1)+panel(465,112,405,265,'本机 MCP',2)
b+=text(58,204,'无代理 / 系统 / 手动',25)+arrow(90,250,360,250)+text(65,301,'Snow Shot → 在线服务',23)+text(60,351,'请求成功才证明连通',23)
b+=text(496,203,'客户端配置 → 连接',25)+arrow(516,249,811,249)+badge(529,312,3)+text(562,321,'Snow Shot 保持运行',23)+text(497,359,'检查状态与连接数',22)
save('set-network-integration.svg','网络访问与本机控制分别配置',b,'代理不是 API 地址；MCP 不是普通用户的截图按钮。')

b=box(40,112,820,275,'#d9e1ed','#cbd8e9',12)+box(245,158,405,185,'#fff','#1677ff',4)
b+='<path d="M447 112V387M40 250H860" stroke="#78a7d9" stroke-width="2" stroke-dasharray="8 7"/><path d="M397 250H497M447 200V300" stroke="#f06d64" stroke-width="3"/>'
b+=badge(219,158,1)+text(60,149,'选区边框',24)+badge(81,313,2)+text(111,321,'选区外遮罩',24)+badge(695,226,3)+text(678,266,'中心辅助线',23)
save('set-capture-interface.svg','截图界面颜色与辅助线',b,'界面边框/遮罩帮助选取范围；输出装饰在调整对话框单独设置。')

# Keep corrected bilingual webcam frames in their focused generator.
import subprocess
import sys
subprocess.run([sys.executable, str(Path(__file__).with_name('generate-guide-recording-webcam-assets.py'))], check=True)

for phase in range(1,4):
    b=box(40,112,820,275,'#f6f9fd','#cbd8e9',12)+text(64,149,'工具栏布局预览',24)
    for x,label in [(100,'A'),(280,'B')]:
        b+=box(x,267,120,68,'#fff','#8bbcff',10)+text(x+48,312,label,27)
    if phase==1:
        b+=box(460,267,120,68,'#fff','#8bbcff',10)+text(508,312,'C',27)
    elif phase==2:
        b+=box(100,185,120,68,'#e3efff','#1677ff',10)+text(148,230,'C',27)+arrow(515,278,245,207)+text(350,200,'拖到 A 上方',26)
    else:
        b+=box(100,197,120,68,'#e3efff','#1677ff',10)+text(148,242,'C',27)+text(300,228,'C 在展开组中',25)+text(300,300,'A 留在主工具栏行',25)
    save(f'set-toolbar-stack-{phase}.svg','把 C 叠放到 A 上方',b,['初始：A、B、C 各占独立位置。','拖动 C 到 A 上方的叠放区域。','松开：A 留在主行，展开组可以选择 C。'][phase-1])

for phase in range(1,4):
    b=box(40,112,820,275,'#f6f9fd','#cbd8e9',12)+box(65,178,270,56,'#fff','#9fc2ee',9)+text(83,216,'按住已配置激活按键',23)
    if phase<3:
        w=35 if phase==1 else 400
        h=25 if phase==1 else 120
        b+=box(380,190,w,h,'#e4efff','#1677ff',4)
        b+='<circle cx="380" cy="190" r="7" fill="#1677ff"/>'
        if phase==2:b+=arrow(392,204,760,300)+text(438,348,'用指定鼠标键拖动选区',24)
        else:b+=text(397,270,'按下指定鼠标键',24)
    else:
        b+=box(430,169,344,175,'#e4efff','#1677ff',9)+text(452,217,'对应动作：固定到屏幕',24)+text(454,292,'松开后检查结果',25)
    save(f'set-mouse-drag-{phase}.svg','激活按键加鼠标拖动',b,['先按住自己配置的激活按键。','保持按键，用指定鼠标键拖出范围。','松开完成选择，检查该动作的结果。'][phase-1])
