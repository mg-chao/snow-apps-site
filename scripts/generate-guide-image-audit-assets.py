"""Original source-backed teaching diagrams; never app screenshots or runtime evidence."""
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]/'docs/public/images/guides'
ROOT.mkdir(parents=True,exist_ok=True)
def text(x,y,t,size=23,color='#1e293b',weight=400):return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(t)}</text>'
def rect(x,y,w,h,fill='#fff',stroke='#c8d3e6',r=12):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
def line(x,y,X,Y,color='#7154d9',width=3,dash=''):return f'<path d="M{x} {y} L{X} {Y}" fill="none" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
def pill(x,y,w,t):return rect(x,y,w,38,'#ede9fe','#ede9fe',19)+text(x+14,y+26,t,20,'#6146bd',600)
def save(name,title,subtitle,body):
 s='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 560" role="img" aria-labelledby="title desc">'+f'<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}。原创教学示意，非应用截图或录屏。</desc><rect width="960" height="560" rx="22" fill="#f5f7fc"/><g font-family="system-ui,-apple-system,PingFang SC,Microsoft YaHei,sans-serif">'+text(35,50,title,29,weight=700)+text(35,86,subtitle,20,'#53627d')+body+line(35,511,925,511,'#dbe3ef',1)+text(35,539,'Snow Shot · 源码核对的教学示意，非应用截图 / 录屏',18,'#53627d')+'</g></svg>'
 (ROOT/name).write_text(s)
COLORS=[('#e7e0fa','#7654c9'),('#dcefe9','#268471'),('#fce8d7','#c26b2c')]
def tile(x,y,w,h,label,i=0):
 fill,stroke=COLORS[i%3];return rect(x,y,w,h,fill,stroke,5)+text(x+12,y+min(h-7,32),label,22,stroke,600)
def handles(x,y,w,h):return ''.join(rect(X-4,Y-4,8,8,'#fff','#7154d9',0) for X,Y in [(x,y),(x+w,y),(x+w,y+h),(x,y+h)])
def sample(x,y,w,h,flip=False,turn=False):
 # Asymmetric F and direction pointer make mirrors/rotation visible without fictional UI.
 b=rect(x,y,w,h,'#e6e0fa','#7654c9',0)+text(x+18,y+55,'F',44,'#6146bd',700)+line(x+w*.25,y+h*.68,x+w*.77,y+h*.68,'#6146bd',6)+f'<path d="M{x+w*.69} {y+h*.57} L{x+w*.80} {y+h*.68} L{x+w*.69} {y+h*.79}" fill="none" stroke="#6146bd" stroke-width="6"/>'
 if flip:b=f'<g transform="translate({2*x+w} 0) scale(-1 1)">{b}</g>'
 if turn:b=f'<g transform="rotate(90 {x+w/2} {y+h/2})">{b}</g>'
 return b
save('img-audit-layout.svg','同一组图片，三种布局方向','纵向串接、横向并排、自定义行列；先检查顺序再输出',
 rect(36,132,277,331)+pill(52,148,115,'纵向')+tile(102,211,142,56,'A',0)+tile(102,282,142,56,'B',1)+tile(102,353,142,56,'C',2)+rect(342,132,277,331)+pill(358,148,115,'横向')+tile(358,251,71,125,'A',0)+tile(444,251,71,125,'B',1)+tile(530,251,71,125,'C',2)+rect(648,132,276,331)+pill(664,148,224,'自定义：2 行 × 2 列')+tile(670,221,111,85,'A',0)+tile(795,221,111,85,'B',1)+tile(670,321,111,85,'C',2)+rect(795,321,111,85,'#f5f7fc','#c8d3e6',5)+text(48,490,'示例只讲解位置与顺序；实际输出范围取决于图片、尺寸策略、边框和间距。',21,'#53627d'))
# Actual automatic-layout sizing rule: vertical Uniform matches first transformed image width.
body=rect(36,130,275,348)+pill(53,146,194,'来源尺寸不同')+tile(74,205,150,100,'A',0)+tile(110,318,75,75,'B',1)+tile(91,406,113,56,'C',2)
body+=rect(342,130,275,348)+pill(359,146,224,'纵向 · 统一尺寸')+tile(407,201,138,92,'A',0)+tile(407,303,138,138,'B',1)+tile(407,451,138,16,'C',2)
# Reserve height for all three while preserving ratios by scaling the entire illustration uniformly.
body=body[:body.find(rect(342,130,275,348))]+rect(342,130,275,348)+pill(359,146,224,'纵向 · 统一尺寸')+tile(421,204,108,72,'A',0)+tile(421,286,108,108,'B',1)+tile(421,404,108,54,'C',2)
body+=rect(648,130,276,348)+pill(665,146,224,'纵向 · 原始尺寸')+tile(731,204,108,72,'A',0)+tile(758,286,54,54,'B',1)+tile(744,350,81,41,'C',2)+text(39,502,'统一尺寸：各图按首图宽度等比缩放。原始尺寸：保留各图大小，较窄图片居中。',20,'#53627d')
save('img-audit-size.svg','统一尺寸与原始尺寸：看相同素材如何变化','保持纵向与图片顺序相同，只改变尺寸策略',body)
# Static collage placement/cropping, rotation, and mirroring.
for i,(title,caption) in enumerate([
 ('先选中一张有方向标记的图片','选中对象后出现控制柄；后续操作只针对这张图。'),
 ('拖控制柄，从中心等比放大','图片超过格子边界的部分会被裁掉；外围虚线只说明完整图片范围。'),
 ('拖图片本体，调整格内保留内容','在同一格内小幅移动；拖到另一图片上可能改为交换。'),
 ('分别比较旋转与水平翻转','旋转改变朝向；翻转产生镜像，文字也会反向。')],1):
 body=rect(37,134,545,325)+pill(56,151,222,'预览中的一个图片格子')
 cx,cy,cw,ch=137,227,320,190
 if i<4:
  sx,sy,sw,sh=(153,242,288,160) if i==1 else ((81,194,432,240) if i==2 else (28,194,432,240))
  body+=f'<defs><clipPath id="clip"><rect x="{cx}" y="{cy}" width="{cw}" height="{ch}"/></clipPath></defs>'
  body+=f'<g clip-path="url(#clip)">{sample(sx,sy,sw,sh)}</g>'+rect(cx,cy,cw,ch,'none','#7654c9',0)+handles(sx,sy,sw,sh)
  if i>1:body+=f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="none" stroke="#7654c9" stroke-width="2" stroke-dasharray="8 6"/>'
 else:
  body+=sample(91,227,175,150,turn=True)+sample(336,227,175,150,flip=True)+text(103,431,'顺时针 90°',22)+text(342,431,'水平翻转',22)
 body+=rect(609,134,315,325)+pill(628,152,265,['选中单张图片','从中心缩放','在原格中移动','两个操作分别比较'][i-1])+text(634,265,['确认选择范围','检查裁掉的边缘','重新露出关键内容','不要镜像正式文字'][i-1],25,'#6146bd')+text(634,409,'可用重置变换重新开始',21,'#53627d')
 save(f'img-audit-collage-transform-{i}.svg',title,caption,body)
# Source ID card template: two cells, ratio85.60/53.98; width constrained to.41 of paper short edge.
body=pill(40,126,293,'分页拼接：每张各占一页')+pill(576,126,346,'身份证模板：正反面放一页')
for x,label,j in [(40,'正面',0),(258,'反面',1)]:
 body+=rect(x,182,183,258,'#fff','#aabbd2',0)+tile(x+16,246,151,95,'虚构卡片',j)+text(x+46,393,label,25)
body+=rect(660,182,183,258,'#fff','#aabbd2',0)+tile(714,235,75,47,'正',0)+tile(714,354,75,47,'反',1)+text(548,477,'卡片比例有约束；不承诺打印一定为实物尺寸。',19,'#53627d')
save('img-audit-pdf-layout.svg','分页与身份证模板，纸张安排不同','只使用虚构正反面素材；选择模板后再次检查位置和页数',body)
for i,(title,caption) in enumerate([
 ('先选择纸张中的单张图片','点击图片后检查控制柄；不要把整页查看缩放当成单图缩放。'),
 ('放大图片，格子只保留相交部分','在控制柄上拖动从中心缩放，检查关键内容有没有超出格子。'),
 ('修正方向，再检查格内裁切','旋转、翻转后仍要检查边缘；不合适时重置图像。')],1):
 body=rect(61,126,264,373,'#fff','#aabbd2',0)+rect(82,148,222,151,'none','#c8d3e6',0)+tile(82,323,222,151,'第二张保持原样',1)
 sx,sy,sw,sh=(95,170,196,112) if i==1 else (27,126,333,190)
 body+=f'<defs><clipPath id="pdfclip"><rect x="82" y="148" width="222" height="151"/></clipPath></defs>'
 body+=f'<g clip-path="url(#pdfclip)">{sample(sx,sy,sw,sh,turn=i==3)}</g>'+rect(82,148,222,151,'none','#7154d9',0)+handles(sx,sy,sw,sh)
 body+=rect(379,137,545,336)+pill(401,156,490,['选中当前格子里的图片','缩放范围与格子边界分开看','旋转改变朝向，翻转改变左右关系'][i-1])+text(404,268,['控制柄包围被选图片','放大后：只输出格子内部内容','镜像会使文字反向'][i-1],27,'#6146bd')+text(404,340,'先看预览，再导出 PDF 检查整页',25)+text(404,419,'虚构素材 · 操作示意 · 非实际 PDF 截图',20,'#53627d')
 save(f'img-audit-pdf-transform-{i}.svg',title,caption,body)
# Independent selected-file action sequences with distinct outcomes.
actions=[('edit','编辑选中的图像','IMG-041'),('collage','拼接选中的图像','IMG-042'),('split','分割选中的图像','IMG-043')]
for slug,label,fid in actions:
 for step in range(1,4):
  if step==1:
   body=rect(40,132,880,329)+pill(60,151,253,'设置 → 全局快捷键')+text(76,266,label,32,'#6146bd',600)+rect(76,307,805,83,'#edf2fb','#c8d3e6')+text(95,358,'配置自己的组合键　→　确认没有冲突',29)+text(77,432,'新配置无默认绑定；不要套用截图快捷键。',23,'#53627d')
   title='先为独立动作配置快捷键';caption=label+'：确认按键后，回到文件管理器。'
  elif step==2:
   body=rect(40,132,880,329)+pill(61,151,379,'Finder / 文件资源管理器 / 桌面')+tile(83,228,362,81,'已选中：A.png',0)+tile(83,328,362,81,'已选中：B.png',1)+text(481,267,'保持文件选择与焦点',29)+text(481,330,'调用刚配置的快捷键',29,'#6146bd')+text(482,416,'macOS：按提示允许读取 Finder',21,'#53627d')
   title='在来源中选择实际图片文件';caption='使用虚构A/B图片练习；没有所选图像时会进入空窗口。'
  else:
   title=label+'：检查打开的结果';caption='图示窗口只表达数量与内容去向，不是应用界面截图。'
   if slug=='collage':
    body=rect(109,144,741,309)+pill(130,162,461,'一个拼接会话，包含全部所选图像')+tile(144,246,287,161,'图片 A',0)+tile(472,246,287,161,'图片 B',1)
   else:
    body=''
    for j,name in enumerate(['A','B']):
     x=41+476*j;body+=rect(x,144,435,309)+pill(x+19,162,395,'图片 '+name+' 的独立'+('编辑' if slug=='edit' else '分割')+'窗口')+tile(x+43,235,349,177,'图片 '+name,j)
     if slug=='split':body+=line(x+43,317,x+392,317,'#c26b2c',4,'9 6')
   body+=text(42,490,'不同入口取得相同编辑能力；随后按本页教程继续处理并保存。',22,'#53627d')
  save(f'img-audit-files-{slug}-{step}.svg',title,caption,body)
save('img-audit-windows-edit.svg','Windows 右键编辑：开关决定新贴图状态','设置 → 搜索“打开编辑时启用标注模式”；不改变独立图像编辑窗口',
 rect(38,136,884,139)+pill(57,154,206,'开关关闭')+text(286,190,'文件右键 → 使用 Snow Shot 编辑',25)+text(286,243,'新贴图先显示图像 → 需要时手动进入标注模式',23,'#53627d')+rect(38,306,884,139)+pill(57,324,206,'开关开启')+text(286,360,'文件右键 → 使用 Snow Shot 编辑',25)+text(286,413,'新贴图直接进入标注模式 → 可以继续绘制',23,'#6146bd'))
print('Generated20source-backed teachingSVGs; no app UI/runtime claim.')
