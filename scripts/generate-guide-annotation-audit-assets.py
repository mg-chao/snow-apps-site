"""Focused source-backed guide reconstructions; never actual application recordings."""
from pathlib import Path
from xml.sax.saxutils import escape
import csv, math, textwrap, re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/public/images/guides'
records=[]
BLUE='#2877bd';RED='#d84d53';INK='#24384f';GREEN='#258568'
def text(x,y,s,size=21,color=INK):return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{escape(s)}</text>'
def rect(x,y,w,h,fill='white',stroke='#b9cce0',r=7,extra=''):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" {extra}/>'
def path(d,color=BLUE,width=4,fill='none',extra=''):return f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="{fill}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
def line(a,b,color=BLUE,width=4,extra=''):return path(f'M{a[0]} {a[1]} L{b[0]} {b[1]}',color,width,extra=extra)
def circle(x,y,r=6,fill='white',stroke=BLUE):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
def arrow(a,b,color=RED,width=3,head_scale=1):
 dx=b[0]-a[0];dy=b[1]-a[1];l=max(math.hypot(dx,dy),.01);ux=dx/l;uy=dy/l
 return line(a,b,color,width)+path(f'M{b[0]-12*head_scale*ux+6*head_scale*uy} {b[1]-12*head_scale*uy-6*head_scale*ux} L{b[0]} {b[1]} L{b[0]-12*head_scale*ux-6*head_scale*uy} {b[1]-12*head_scale*uy+6*head_scale*ux}',color,width)
def handles(x,y,w,h):return rect(x,y,w,h,'none',BLUE,0,'stroke-dasharray="5 5"')+''.join(rect(a-4,b-4,8,8,'white',BLUE,1) for a,b in [(x,y),(x+w,y),(x,y+h),(x+w,y+h)])
def pill(x,y,label):return rect(x,y,len(label)*15+30,33,'#e2effb',BLUE,5)+text(x+12,y+23,label,18,BLUE)
def save(slug,title,label,caption,body,fids,doc,source,step=''):
 raw_label=label
 label=re.sub(r'^\d+[.、]\s*','',label)
 filename='ann-audit-'+slug+'.svg'
 lines=textwrap.wrap(caption,36,break_long_words=True,break_on_hyphens=False)
 footer=''.join(text(26,364+i*25,s,18) for i,s in enumerate(lines[:2]))
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="430" viewBox="0 0 760 430" role="img" aria-labelledby="title desc" font-family="system-ui,sans-serif"><title id="title">{escape(title+"："+label)}</title><desc id="desc">源码核对的教学重建，非应用截图或录屏。{escape(caption)}</desc><rect width="760" height="430" rx="12" fill="#f3f7fc"/>{text(24,34,title,25)}{text(24,63,label,18,"#536c86")}{rect(18,80,724,260)}{body}{footer}{text(24,416,"教学示意 · 非应用截图或录屏",15,"#536c86")}</svg>'
 (OUT/filename).write_text(svg)
 records.append({'Asset':filename,'Feature group':doc.split('/')[-1],'Teaching purpose and step':step or raw_label,'Documentation path':doc,'Source and production method':source+'；手工编写专属SVG状态/参数示意；scripts/generate-guide-annotation-audit-assets.py','Caption':'教学示意，非应用截图或录屏','Status':'已制作；待独立渲染与内容检查','Feature IDs':';'.join(fids)})
 return {'src':'/images/guides/'+filename,'alt':title+'：'+label,'label':label,'caption':caption}
frames={}
# Shape variants: source document/speech_bubble/thought_bubble.rs builds cloud + a trail of circles.
body=text(86,118,'对话气泡',22)+text(452,118,'思考气泡',22)
body+=path('M65 145 H310 Q330 145 330 165 V235 Q330 255 310 255 H160 L118 295 L130 255 H65 Q45 255 45 235 V165 Q45 145 65 145 Z',BLUE,3,'#e8f2fc')+text(95,205,'同一段说明文字',22)
body+=path('M430 155 C430 130 466 125 480 143 C495 112 540 115 554 142 C580 118 620 134 617 155 C657 155 672 186 650 205 C671 232 642 260 616 251 C611 279 568 282 550 261 C527 285 486 276 480 253 C451 272 417 251 427 228 C398 218 402 176 430 155 Z',BLUE,3,'#e8f2fc')+text(450,208,'同一段说明文字',22)+circle(464,282,11,'#e8f2fc')+circle(447,306,7,'#e8f2fc')
frames['bubble']=[save('bubble-modes','气泡形状改变外观','矩形主体与云朵主体','保持对话气泡工具，选中已有气泡后切换思考气泡；主体变为云朵，尾部为圆点轨迹。',body,['ANN-015'],'docs/zh/guides/annotations/speech-bubbles.mdx','snow-draw-engine-document/src/speech_bubble.rs 与 speech_bubble/thought_bubble.rs')]
# Elbow arrows are two-click rather than continuous-point creation.
frames['elbow']=[]
for i,(label,cap) in enumerate([('1. 单击起点','折线箭头模式下，在空白处单击起点；移开鼠标，准备确定终点。'),('2. 移动预览','只移动指针，不继续加拐点；正交折线路径随终点位置预览。'),('3. 单击终点即完成','在终点单击，折线箭头立即完成；之后再用控制段改变绕行。')],1):
 body=pill(45,100,'折线箭头')+circle(110,245,8)+text(75,286,'起点',19)
 if i>1:
  body+=path('M110 245 H365 V160 H620',BLUE,4,extra='stroke-dasharray="7 5"' if i==2 else '')
  body+=arrow((580,160),(620,160),BLUE,4)+circle(620,160,8)+text(587,205,'终点',19)
 if i==3:body+=circle(365,205,7)+text(300,302,'第二次单击提交；不是继续加第三个点',19)
 frames['elbow'].append(save(f'elbow-{i}','折线箭头两次单击完成',label,cap,body,['ANN-022'],'docs/zh/guides/annotations/arrows.mdx','snow-draw-engine-editor/src/creation_workflow.rs handle_arrow_pointer_down Elbow branch'))
# Binding and attached labels: object movement changes attached endpoint, not a static arrow.
frames['binding']=[]
for i,(label,cap) in enumerate([('1. 在图形边缘连接','画箭头时将端点靠近图形边缘，按吸附预览确认连接。'),('2. 移动被连接图形','拖动右侧图形后，绑定的箭头端点随图形位置变化，左侧关系保留。'),('3. 给箭头添加文字','选中箭头后进入文字输入，输入短标签；这里用光标表示输入状态。'),('4. 完成并再次移动','结束输入后再移动图形，箭头与随附标签一起更新；检查结果后输出。')],1):
 y=155 if i==1 else 115
 if i==4:y=190
 body=rect(65,190,155,74,'#e8f2fc',BLUE)+text(92,235,'来源图形',22)+rect(525,y,155,74,'#e8f2fc',BLUE)+text(553,y+45,'目标图形',22)
 body+=arrow((224,227),(520,y+37),BLUE,4)+circle(224,227,6)+circle(520,y+37,6)
 if i==2:body+=arrow((708,222),(708,156))+text(318,304,'移动主体 → 端点随动',20)
 if i>=3:
  body+=rect(290,167 if i==3 else 205,165,45,'white',BLUE,4)+text(306,198 if i==3 else 236,'提交请求',22)
  if i==3:body+=line((407,175),(407,203),INK,2)
 frames['binding'].append(save(f'binding-label-{i}','连线绑定图形与随附文字',label,cap,body,['ANN-029','ANN-030'],'docs/zh/guides/annotations/arrows.mdx','creation_workflow.rs ArrowSuggestedBinding；snow_canvas_widget.cpp beginArrowText；arrow_text.rs'))
# Qualitative pressure response, without claiming a calibrated pressure-to-width function.
body=text(45,125,'普通画笔：较一致的宽度',22)+path('M70 180 Q150 105 225 180 T385 180 T560 180',BLUE,7)
body+=text(45,238,'压感画笔：粗细随输入变化',22)+path('M70 285 Q145 218 225 280 Q300 340 385 280 Q470 218 560 280 Q470 230 385 294 Q300 355 225 293 Q145 230 70 285 Z',BLUE,1,BLUE)
frames['pressure']=[save('brush-pressure','普通与压感笔画的差异','同类轨迹，比较粗细变化','此图只示意模式区别，不对应固定压力值；鼠标模式可模拟粗细，有压力设备可使用原生压力。',body,['ANN-037'],'docs/zh/guides/annotations/brush.mdx','free_draw_pressure.rs native pressure/simulated speed response；free_draw_workflow.rs')]
# Magnifier shapes and source outline / leader endpoints.
body=''
for i,name in enumerate(['矩形与圆角','椭圆','菱形']):
 x=45+i*240;body+=text(x,124,name,22)
 if i==0:body+=rect(x+15,155,165,115,'#e8f2fc',RED,22)
 elif i==1:body+=f'<ellipse cx="{x+98}" cy="212" rx="90" ry="62" fill="#e8f2fc" stroke="{RED}" stroke-width="3"/>'
 else:body+=path(f'M{x+98} 145 L{x+188} 212 L{x+98} 279 L{x+8} 212 Z',RED,3,'#e8f2fc')
 body+=text(x+47,221,'细节',27)
frames['mag-shapes']=[save('magnifier-shapes','放大镜范围形状','相同内容下比较形状','先选中放大镜，再切换形状；矩形圆角控制边界，椭圆和菱形不是矩形圆角效果。',body,['ANN-083'],'docs/zh/guides/annotations/magnifier.mdx','snow_canvas_types.h MagnifierStyle；screenshottoolpalettestylecontrols.cpp Magnifier shape / corner_radius')]
body=''
for i,label in enumerate(['来源轮廓开 · 端点比例1×','来源轮廓关 · 端点比例1.8×']):
 x=35+i*360;body+=text(x,122,label,19)+rect(x+16,213,60,60,'white',RED if i==0 else 'none')+text(x+28,246,'细节',16)+rect(x+213,156,120,120,'#e8f2fc',RED)+text(x+235,222,'细节',32)
 body+=arrow((x+209,222),(x+46,243),BLUE,3,1 if i==0 else 1.8)
frames['mag-leader']=[save('magnifier-leader','来源轮廓和引线端点','轮廓开关与端点大小分别设置','引线从镜片边缘指向来源中心；关闭来源轮廓只隐藏来源框，来源内容和采样位置仍保留。',body,['ANN-085'],'docs/zh/guides/annotations/magnifier.mdx','snow-draw-engine-document/src/magnifier.rs leader_arrow / source_outline；style controls Magnifier')]
# Distance endpoints must not imply a change in the measured quantity.
body=''
for i,(label,head,scale) in enumerate([('竖线端点 · 小','bar',.6),('箭头端点 · 普通','arrow',1),('箭头端点 · 较大','arrow',1.8)]):
 y=145+i*75;body+=text(40,y-16,label,19)+line((285,y),(665,y),BLUE,3)+text(435,y-12,'10.00 cm',21)
 for x,d in [(285,1),(665,-1)]:
  if head=='bar':body+=line((x,y-12*scale),(x,y+12*scale),BLUE,3)
  else:body+=path(f'M{x+14*scale*d} {y-7*scale} L{x} {y} L{x+14*scale*d} {y+7*scale}',BLUE,3)
frames['distance']=[save('distance-ends','尺寸端点只改变标注外观','相同长度与比例，比较端点','切换端点样式与比例不会校准实际距离；测量端点、比例和单位要分别检查。',body,['ANN-089'],'docs/zh/guides/annotations/distance.mdx','DistanceStyle endpoint_scale/endpoint_style；screenshottoolpalettestylecontrols.cpp distance family')]
# Visual counterclockwise sweep: above -> right gives directed270°, interior90°.
body=''
for i,(label,value,large,sweep) in enumerate([('360° 角','270°',1,0),('180° 角','90°',0,1),('360° 角 / 弧度','4.712 rad',1,0)]):
 cx=130+i*250;cy=240;r=48;body+=text(cx-88,122,label,20)+line((cx,cy),(cx,145),BLUE,3)+line((cx,cy),(cx+94,cy),BLUE,3)
 body+=path(f'M{cx} {cy-r} A{r} {r} 0 {large} {sweep} {cx+r} {cy}',RED,3)+text(cx-58,310,value,23,RED)
frames['angle-types']=[save('angle-types-units','同组三点的角类型与单位','270° 有向角、90° 内角、4.712 弧度','先明确要表达的转向或内角，再选择类型；单位变化按数学换算显示，不是沿用同一个数字。',body,['ANN-092','ANN-093'],'docs/zh/guides/annotations/angle.mdx','snow-draw-engine-document/src/angle.rs AngleRays sweep；tests/angle.rs interior/formatting')]
# Arc dragging changes radius while preserving rays. Endpoint editing changes the angle.
frames['angle-edit']=[]
for i,(label,cap) in enumerate([('1. 选中角弧','角的两条边已经确定，点击选中对象，找到角弧控制位置。'),('2. 径向拖动角弧','沿离开顶点的方向拖动角弧，弧半径变大；两条边和90°数值保持不变。'),('3. 再编辑边端点','拖动第二条边端点时，夹角随边方向变化；这是改角度，与仅改角弧半径不同。')],1):
 cx=280;cy=278;r=46 if i==1 else 90;end=(450,278) if i<3 else (400,158)
 body=pill(45,98,'180° 角（内角）')+line((cx,cy),(cx,108),BLUE,4)+line((cx,cy),end,BLUE,4)+circle(cx,cy)+circle(cx,108)+circle(*end)
 if i<3:body+=path(f'M{cx} {cy-r} A{r} {r} 0 0 1 {cx+r} {cy}',RED,3)+text(408,232,'90°',28,RED)+circle(cx+r*.707,cy-r*.707,7)
 else:body+=path(f'M{cx} {cy-r} A{r} {r} 0 0 1 {cx+r*.707} {cy-r*.707}',RED,3)+text(432,205,'45°',28,RED)+arrow((450,278),end)
 if i==2:body+=arrow((325,233),(365,193))+text(470,132,'两边保持原位',21)
 frames['angle-edit'].append(save(f'angle-edit-{i}','区分角弧与边端点的编辑',label,cap,body,['ANN-095'],'docs/zh/guides/annotations/angle.mdx','editor/angle.rs angle_arc_drag_preserves_rays；document/angle.rs angle_with_moved_point'))
# Right-click is an idle temporary selection, not the right-click meaning during creation.
frames['right']=[]
for i,(label,cap) in enumerate([('1. 保持画笔工具','此时没有正在绘制的笔画；在同类已有笔画上准备临时选择。'),('2. 右键点中对象','右键单击笔画本体使其选中，画笔工具保持；不需要先切到选择元素。'),('3. 按住右键拖动','保持右键拖动，选中笔画整体移动；松开后可以继续用原来的画笔。')],1):
 offset=80 if i==3 else 0;body=pill(40,100,'当前：画笔')+path(f'M{110+offset} 250 Q{190+offset} 140 {290+offset} 235 T{470+offset} 200',BLUE,7)
 if i>=2:body+=handles(95+offset,155,390,115)+pill(535,115,'右键')
 if i==3:body+=arrow((420,295),(505,295))+text(65,320,'工具保持，移动的是已有对象',20)
 frames['right'].append(save(f'right-select-{i}','右键临时选择与移动',label,cap,body,['ANN-122'],'docs/zh/guides/annotations/elements.mdx','input/quick_selection.rs idle secondary selection；policy.rs Secondary forces quick selection'))
# Absolute rotation is snapped to 15 degree increments; center resize keeps center.
frames['rotate']=[]
for i,(label,cap) in enumerate([('1. 拖动旋转柄','先选中矩形，拖动外侧旋转柄；不按修饰键时可自由旋转。'),('2. 按住 Shift','继续拖动时按住Shift，绝对角度按15°增量对齐；此例从17°对齐到15°。'),('3. 松开完成','在目标角度松开鼠标，保留15°旋转结果；不要把旋转柄当缩放柄。')],1):
 deg=17 if i==1 else 15;body=f'<g transform="translate(350 220) rotate({deg})">'+rect(-130,-60,260,120,'#e8f2fc',BLUE)+handles(-130,-60,260,120)+line((0,-60),(0,-95),BLUE,2)+circle(0,-95,7)+'</g>'+circle(350,220,4,BLUE)+text(540,240,str(deg)+'°',35,RED)
 if i==2:body+=pill(55,105,'Shift')
 frames['rotate'].append(save(f'rotate-{i}','Shift 让旋转角度规整对齐',label,cap,body,['ANN-123'],'docs/zh/guides/annotations/elements.mdx','edit_workflow/selection_edit.rs Rotate lock_rotation_to_discrete_angle；test absolute15deg'))
frames['center']=[]
for i,(label,cap) in enumerate([('1. 找到缩放控制柄','选中对象，记住中心十字位置；这次操作针对控制柄，不是对象本体。'),('2. 按 Alt 拖动控制柄','按住Alt向外拖角柄，中心保持原位，两侧同步扩展。'),('3. 松开保留新大小','结果范围变大但中心没有移动；Alt拖对象本体则是复制移动，不能混用。')],1):
 x,y,w,h=(260,160,200,110) if i==1 else (195,124,330,182)
 body=rect(x,y,w,h,'#e8f2fc',BLUE)+handles(x,y,w,h)+line((350,215),(370,215),RED,2)+line((360,205),(360,225),RED,2)+text(560,217,'中心不动',22)
 if i>=2:body+=rect(260,160,200,110,'none','#8ea9c3',0,'stroke-dasharray="5 5"')+arrow((460,270),(525,306))+arrow((260,160),(195,124))+pill(45,100,'Alt')
 frames['center'].append(save(f'center-resize-{i}','Alt 从中心缩放',label,cap,body,['ANN-124'],'docs/zh/guides/annotations/elements.mdx','selection_edit.rs scale_from_center=event.modifiers.alt；geometry/resize.rs'))
# Freehand Shift switches the active segment to straight, without fixed-angle claims.
frames['brush-shift']=[]
for i,(label,cap) in enumerate([('1. 先画一段曲线','按住左键自由移动；当前轨迹按普通画笔方式记录。'),('2. 按住 Shift 形成直边','仍保持左键，按Shift后向另一位置移动；新增的当前部分呈直线段。'),('3. 松开 Shift 继续画','松开Shift再继续自由移动，最后抬起鼠标；曲线和直边属于同一笔画。')],1):
 body=path('M75 230 Q155 105 245 220',BLUE,7)
 if i>=2:body+=line((245,220),(445,160),BLUE,7)+pill(530,112,'Shift' if i==2 else '松开 Shift')
 if i==3:body+=path('M445 160 Q520 90 620 230',BLUE,7)
 frames['brush-shift'].append(save(f'brush-shift-{i}','在自由笔画中加入直线段',label,cap,body,['ANN-125'],'docs/zh/guides/annotations/brush.mdx','free_draw_workflow.rs append_input shift；test shift_creates_and_replaces_one_straight_endpoint'))
frames['continue']=[]
for i,(label,cap) in enumerate([('1. 靠近开放端点','保持画笔工具，把指针移到未闭合笔画的首端或末端，观察端点反馈。'),('2. 从端点按下继续拖','从反馈位置按住左键向外移动，新增部分接在原笔画末端。'),('3. 松开并检查对象','松开后续画合入原笔画；选中可看到它作为一个对象，而不是独立的新笔画。')],1):
 body=path('M80 245 Q165 125 280 225',BLUE,7)+circle(280,225,11,'none',RED)
 if i>=2:body+=path('M280 225 Q365 315 470 175 T645 190',BLUE,7,extra='stroke-dasharray="8 5"' if i==2 else '')
 if i==1:body+=text(330,210,'开放端点反馈',22)
 if i==3:body+=handles(60,130,610,168)+text(385,318,'同一个笔画对象',20)
 frames['continue'].append(save(f'brush-continue-{i}','从笔画端点继续画',label,cap,body,['ANN-126'],'docs/zh/guides/annotations/brush.mdx','free_draw_workflow.rs resolve_free_draw_endpoint excludes closed；continue_from updates existingid'))
frames['serial-reset']=[]
for i,(label,cap) in enumerate([('1. 已放置 1、2、3','当前编号体系已有三个徽标；准备重新开始一组，而不改动这些编号。'),('2. 在真正空白处右键','保持序号工具，在没有对象的空白处右键；后续起始值重置为1，旧数字不变。'),('3. 再单击放一个 1','单击新位置得到新的一号；点旧对象的右键会选择它，不是执行空白重置。')],1):
 for j,n in enumerate([1,2,3]):bodypart=circle(130+j*180,170,25,BLUE,BLUE)+text(122+j*180,179,str(n),25,'white');body=bodypart if j==0 else body+bodypart
 body+=pill(45,101,'当前：序号')
 if i==2:body+=circle(600,280,15,'none',RED)+pill(540,238,'空白处右键')+text(185,305,'下一次：1',23,RED)
 if i==3:body+=circle(595,275,25,GREEN,GREEN)+text(587,284,'1',25,'white')+text(125,310,'旧 1 / 2 / 3 保持，新的一组从 1 开始',20)
 frames['serial-reset'].append(save(f'serial-reset-{i}','空白处右键重置下一次序号',label,cap,body,['ANN-128'],'docs/zh/guides/annotations/sequence.mdx','input/quick_selection.rs blank SerialNumber supports_number resetscreationto1 afterdeselect'))
# Publish manifest and frame payloads for exact MDX integration.
with (ROOT/'artifacts/assets-annotation-audit.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['Asset','Feature group','Teaching purpose and step','Documentation path','Source and production method','Caption','Status','Feature IDs']);w.writeheader();w.writerows(records)
import json
(ROOT/'artifacts/annotation-audit-frames.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2)+'\n')
print('created',len(records),'focused SVG assets for',len({fid for r in records for fid in r['Feature IDs'].split(';')}),'operations')
