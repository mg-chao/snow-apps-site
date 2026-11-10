"""Generate source-backed, explicitly labelled instructional SVGs (not UI captures)."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'docs/public/images/guides'
ROOT.mkdir(parents=True, exist_ok=True)

def text(x,y,s,size=24,color='#263148'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{escape(s)}</text>'
def box(x,y,w,h,fill='#fff',stroke='#cbd4e4',r=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
def line(x,y,a,b,color='#7652dc',dash=False):
    return f'<path d="M{x} {y}L{a} {b}" fill="none" stroke="{color}" stroke-width="4"'+(' stroke-dasharray="8 6"' if dash else '')+'/>'
def dot(x,y,s):
    return f'<circle cx="{x}" cy="{y}" r="19" fill="#7652dc"/>'+text(x-7,y+8,str(s),23,'white')
def save(name,title,body):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="480" viewBox="0 0 960 480" role="img" aria-labelledby="title"><title id="title">{escape(title)}（操作示意）</title><g font-family="Arial, PingFang SC, Microsoft YaHei, sans-serif">'+box(1,1,958,478,'#f6f7fc')+text(30,43,title,28)+text(30,460,'操作示意',18,'#536078')+body+'</g></svg>'
    (ROOT/(name+'.svg')).write_text(svg+'\n')

save('start-install','根据电脑选择安装包',box(30,80,430,145)+text(54,118,'Windows',27)+text(54,160,'Intel / AMD → x64')+text(54,196,'ARM 处理器 → ARM64')+box(490,80,440,145)+text(514,118,'macOS 15 或更新',27)+text(514,160,'Apple 芯片 → arm64')+text(514,196,'Intel → x86_64 完整版')+box(30,250,900,165,'#ebe6fb','#d5caf7')+text(54,290,'完整版：准备本地识别与更多识别功能',26)+text(54,332,'Mini：包更小；文字识别可添加工具栏入口或绑定动作',24)+text(54,379,'先确认系统和架构，再选择安装渠道。',24))
save('start-permissions','macOS 权限：按功能逐项处理',''.join(box(30,80+i*79,900,65)+dot(60,112+i*79,i+1)+text(95,120+i*79,a,24)+text(445,120+i*79,b,22) for i,(a,b) in enumerate([('屏幕录制','截图与录屏画面'),('辅助功能','需要系统控制的操作'),('输入监控','全局键鼠与录制效果'),('麦克风','录制自己的声音')])) )
for stage in range(3):
    body=box(30,80,900,330)+text(55,120,'目标窗口',25)+box(70,150,300,210,'#edf0f6')+text(95,190,'需要保留的内容',24)+box(405,150,480,210,'#edf0f6')+text(440,190,'其他内容',24)
    if stage>=1:body+=box(90,205,540,140,'#ede8fb','#7652dc',0)+dot(90,205,1)+dot(630,345,2)+line(110,220,610,330)
    if stage==2:body+=box(330,365,555,40,'#fff')+text(348,393,'箭头 · 文字 · 复制到剪贴板 · 保存为文件',18)
    save(f'cap-basics-{stage+1}', ['开始截图，找到目标','按住左键从 1 拖到 2','松开后检查选区与工具栏'][stage],body)
save('cap-precise','精确选区：位置、尺寸、比例与装饰',box(30,80,900,70,'#fff')+text(50,124,'X, Y 位置   🔒   宽度 × 高度   px / dp   16:9',25)+line(145,150,145,200)+box(30,205,420,200)+text(55,246,'调整选区大小',25)+text(55,290,'X / Y：左上角位置',23)+text(55,331,'宽 / 高：需要保留的范围',23)+text(55,372,'锁定：联动修改宽高',23)+box(480,205,450,200,'#ebe6fb')+text(505,246,'在数值上单击 → 输入',24)+text(505,290,'在数值上滚动 → 微调',24)+text(505,331,'比例菜单 → 选择预设',24)+text(505,372,'确认后观察边框变化',24))
for stage in range(4):
    body=box(30,80,900,330)+box(60,110,310,250,'#e8edf5')+text(80,151,'区域 A',24)+box(420,110,250,250,'#e8edf5')+text(440,151,'区域 B',24)+text(715,190,'中间区域',24)
    body+=box(90,180,210,130,'#ede8fb','#7652dc',0)+dot(90,180,1)
    if stage>=1:body+=box(440,180,180,130,'#ede8fb','#7652dc',0)+dot(440,180,2)
    if stage==2:body+=box(510,245,110,65,'#f3f5fa','#de6161',0)+text(680,280,'减去重叠部分',23,'#b43c3c')
    if stage==3:body=box(30,80,900,330)+text(60,125,'紧凑布局：把多个区域靠拢排列',26)+box(180,170,260,160,'#ede8fb','#7652dc',0)+text(205,220,'A',32)+box(460,170,260,160,'#ede8fb','#7652dc',0)+text(485,220,'B',32)+text(180,380,'区域间距可调；复制前检查合成结果',24)
    save(f'cap-multiple-{stage+1}', ['先保留第一个区域','添加截图区域：框选第二块','减去截图区域：挖去不需要的部分','紧凑布局：调整区域间距'][stage],body)
for stage in range(3):
    pts=[(130,325),(200,130),(420,200),(600,115),(790,325)]
    visible=pts[:(2 if stage==0 else 5)]
    path='M'+' L'.join(f'{x} {y}' for x,y in visible)+(' Z' if stage==2 else '')
    body=box(30,80,900,330)+f'<path d="{path}" fill="'+('#ede8fb' if stage==2 else 'none')+'" stroke="#7652dc" stroke-width="4"/>'
    for i,(x,y) in enumerate(visible):body+=dot(x,y,i+1)
    body+=text(210,390,['逐次单击固定边界点','最后一点双击完成','闭合后只保留边界内的画面'][stage],24)
    save(f'cap-irregular-{stage+1}', ['折线选区：开始边界','折线选区：继续取点','折线选区：完成闭合'][stage],body)
for stage in range(4):
    body=box(30,80,550,330)+text(55,116,'目标内容区',24)+box(80,145,450,200,'#fff','#7652dc',0)
    offset=stage*45
    for i in range(5):body+=text(105,180+i*32,f'连续内容第 {1+i+stage*2} 行',22)
    body+=box(640,80,290,330,'#fff')+text(665,116,'拼接预览',24)
    for i in range(4+stage*2):body+=line(670,145+i*18,880,145+i*18,'#c2c8dc')
    body+=box(662,140+min(offset,110),226,95,'none','#7652dc',0)
    if stage==2:body+=line(640,160,930,160,'#de6161')+line(640,345,930,345,'#de6161')+text(60,390,'拖动预览边界，保留需要的开头和结尾',23)
    elif stage==3:body+=box(90,365,430,40,'#ebe6fb')+text(105,392,'保存为文件 → 打开图片检查接缝',21)
    else:body+=text(60,390,'相邻画面保留重叠，预览随拼接增长',23)
    save(f'cap-scrolling-{stage+1}', ['框选会滚动的内容','缓慢滚动，检查预览增长','裁剪开头和结尾','停止滚动并导出结果'][stage],body)
save('cap-modes','按任务选择截图入口', ''.join(box(30+300*i,90,280,290,'#fff')+dot(60+300*i,125,i+1)+text(55+300*i,182,a,25)+text(55+300*i,236,b,21)+text(55+300*i,284,c,21)+text(55+300*i,335,d,21) for i,(a,b,c,d) in enumerate([('延时截图','先触发 → 展开菜单','等待 1–10 秒','进入截图选区'),('直接截图','当前显示器 / 窗口','跳过选区编辑','结果复制到剪贴板'),('重新截图','保留当前操作上下文','刷新屏幕图像','再次检查内容')])) )
colors=['#7652dc','#6b48cb','#222b44','#2b3450','#d4c9ef','#906ee9','#7652dc','#7652dc','#736a8e']
body=''
for i,c in enumerate(colors):body+=box(60+(i%3)*82,100+(i//3)*82,82,82,c,'#fff',0)
body+=box(142,182,82,82,'none','#e44848',0)+line(224,222,390,222)+box(410,95,510,270)+text(440,145,'中心像素：#7652DC',27)+text(440,199,'HEX → 无 # HEX → RGB → HSL',22)+text(440,251,'Shift：切换格式；C：复制并退出',22)+text(440,312,'Shift+P：切换坐标模式',22)+text(60,405,'先对准中心像素，再复制；不要读取抗锯齿边缘的混合色。',23)
save('cap-color','放大取色：中心像素与格式',body)
print('capture SVG assets generated')
