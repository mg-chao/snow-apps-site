#!/usr/bin/env python3
"""Dedicated capture gesture diagrams. Fixed-release behavior; no fabricated app chrome."""
from pathlib import Path
from html import escape
import re ,math ,json ,csv
ROOT =Path (__file__ ).resolve ().parents [1 ]
OUT =ROOT /'docs/public/images/guides'
META =[]
DEMOS =[]
P ='#7652dc';M ='#536078';R ='#c5503e'
def measure (s ):return sum (1 if ord (c )>255 else .53 for c in s )
def wrap (s ,
size ,
w ):
    tokens =re .findall (r'[0-9]+(?::[0-9]+|–[0-9]+|%)+|[A-Za-z0-9]+(?:[’\'-][A-Za-z0-9]+)*|\s+|.',
    s );out =[];line =''
    for t in tokens :
        if measure (line +t )*size >w and line .strip ():
            if t in '，。！？；：、）”.,!?;:)':line +=t ;continue
            out .append (line .rstrip ());line =t .lstrip ()
        else :line +=t
    if line .strip ():out .append (line .rstrip ())
    return out
class F :
    def __init__ (self ,
    title ,
    sub ,
    en =False ,
    h =700 ):
        self .en =en ;self .h =h ;self .title =title ;self .caption_text ='';self .s =[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 {h}" width="600" height="{h}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><defs><pattern id="check" width="20" height="20" patternUnits="userSpaceOnUse"><rect width="20" height="20" fill="#fff"/><path d="M0 0h10v10H0zM10 10h10v10H10z" fill="#dce1ec"/></pattern></defs><rect x="1" y="1" width="598" height="{h-2}" rx="14" fill="#f6f7fc" stroke="#cbd4e4"/><g font-family="Arial, PingFang SC, Microsoft YaHei, sans-serif">']
        self .t (28 ,
        42 ,
        title ,
        25 ,
        w =544 );self .t (28 ,
        108 ,
        sub ,
        19 ,
        M ,
        w =544 )
    def t (self ,
    x ,
    y ,
    s ,
    size =22 ,
    color ='#263148',
    w =500 ):
        for i ,l in enumerate (wrap (s ,
        size ,
        w )):self .s .append (f'<text x="{x}" y="{y+i*(size+6)}" font-size="{size}" fill="{color}">{escape(l)}</text>')
    def box (self ,
    x ,
    y ,
    w ,
    h ,
    fill ='#fff',
    stroke ='#cbd4e4',
    rx =10 ):self .s .append (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    def path (self ,
    d ,
    color =P ,
    width =3 ,
    fill ='none',
    dash =False ,
    opacity =1 ):self .s .append (f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="{fill}"'+(' stroke-dasharray="7 5"'if dash else '')+f' opacity="{opacity}"/>')
    def pointer (self ,
    x ,
    y ,
    held =False ):
        self .s .append (f'<path d="M{x} {y}v24l6-6 6 10 5-3-6-10h10z" fill="#263148" stroke="white" stroke-width="1"/>')
        if held :self .s .append (f'<circle cx="{x+8}" cy="{y+8}" r="16" fill="none" stroke="{R}" stroke-width="2"/>')
    def dot (self ,
    x ,
    y ,
    label =None ,
    hollow =False ):
        self .s .append (f'<circle cx="{x}" cy="{y}" r="6" fill="{("white" if hollow else P)}" stroke="{P}" stroke-width="2"/>')
        if label is not None :self .t (x +9 ,
        y -9 ,
        str (label ),
        17 ,
        P ,
        w =60 )
    def arrow (self ,
    x ,
    y ,
    a ,
    b ,
    color =R ):
        self .path (f'M{x} {y}L{a} {b}',
        color ,
        3 )
        angle =math .atan2 (b -y ,
        a -x );l =10
        self .path (f'M{a-l*math.cos(angle-.5):.2f} {b-l*math.sin(angle-.5):.2f}L{a} {b}L{a-l*math.cos(angle+.5):.2f} {b-l*math.sin(angle+.5):.2f}',
        color ,
        3 )
    def caption (self ,
    s ):
        self .caption_text =s
        self .t (28 ,
        self .h -165 ,
        s ,
        22 ,
        w =544 )
    def save (self ,
    name ,
    ids ,
    purpose ,
    doc ,
    step ,
    sources ):
        self .t (28 ,
        self .h -24 ,
        'Instructional illustration'if self .en else '操作示意',
        18 ,
        M ,
        w =544 );self .s .append ('</g></svg>')
        rel ='docs/public/images/guides/'+('en/'if self .en else '')+name +'.svg';p =ROOT /rel ;p .parent .mkdir (parents =True ,
        exist_ok =True );p .write_text ('\n'.join (self .s )+'\n')
        DEMOS .append ({'locale':'en'if self .en else 'zh',
        'name':name ,
        'src':'/images/guides/'+('en/'if self .en else '')+name +'.svg',
        'alt':self .title ,
        'label':self .title ,
        'caption':self .caption_text or purpose })
        META .append ({'Asset':rel ,
        'Feature IDs':ids ,
        'Teaching purpose':purpose ,
        'Documentation path':'docs/'+('en'if self .en else 'zh')+'/guides/capture/'+doc ,
        'Associated step':step ,
        'Source':'f02f50e: '+sources ,
        'Production method':'专用原始矢量步骤/参数对照；仅已知手势状态及示例内容，非原生界面；图内操作示意。',
        'Status':'已制作；离线目检/网站检查另见本批报告；未证明普通UI',
        'Capture prerequisites and next action':'根代理窄合入后检查受控Next/Reset、浅深色和手机；普通UI状态不提升。'})

def ratio (en ):
    titles =['Unlocked rectangular drag',
    'Hold Shift: make it square',
    'Release Shift, then keep dragging',
    'Hold Q to snap to a ratio',
    'Release Q: the ratio stays locked',
    'Press Q again, then resize freely']if en else ['自由比例开始拖动',
    '按住 Shift：临时正方形',
    '松开 Shift，再继续拖动',
    '按住 Q：吸附标准比例',
    '松开 Q：比例仍然锁定',
    '再按 Q 解锁，继续自由调整']
    captions =['Start from Free with the ratio unlocked. Hold the left mouse button to draw a rectangle.',
    'Keep the left button held and hold Shift. The current rectangle is constrained to 1:1.',
    'Release Shift and move the pointer again. It is a temporary constraint; it does not lock 1:1.',
    'In an unlocked rectangular drag, hold Q. This example snaps to 16:9; the nearest preset depends on the raw rectangle.',
    'Release Q, then keep dragging. The selected 16:9 ratio stays locked instead of returning to Free.',
    'Press Q once more to unlock, then continue dragging. Check Free and the new bounds before releasing the mouse.']if en else ['先选自由并解除比例锁，再按住左键从一个角拖出矩形。',
    '左键保持按住，同时按住 Shift，矩形临时约束为 1:1。',
    '松开 Shift 后继续移动指针；临时约束结束，不会自动锁定 1:1。',
    '未锁定比例的矩形拖动中按住 Q。本例吸附 16:9，实际取决于当时矩形最接近的预设。',
    '松开 Q 后继续拖动，仍按已吸附的 16:9 调整，不会恢复自由比例。',
    '再次按 Q 解锁后继续拖动。核对自由比例和范围，再松开鼠标完成。']
    sizes =[(220 ,
    120 ),
    (180 ,
    180 ),
    (260 ,
    150 ),
    (240 ,
    135 ),
    (320 ,
    180 ),
    (300 ,
    210 )]
    for i ,(title ,
    cap ,
    (w ,
    h ))in enumerate (zip (titles ,
    captions ,
    sizes ),
    1 ):
        state =('Free · Unlocked'if i in [1 ,
        3 ,
        6 ]else '1:1 · Shift held'if i ==2 else '16:9 · Locked')if en else ('自由 · 未锁定'if i in [1 ,
        3 ,
        6 ]else '1:1 · 按住 Shift'if i ==2 else '16:9 · 已锁定')
        f =F (title ,
        state ,
        en );f .box (30 ,
        145 ,
        540 ,
        350 ,
        '#fff')
        for y in [220 ,
        280 ,
        340 ,
        400 ]:f .path (f'M65 {y}h465',
        '#e0e5ef',
        8 )
        f .box (110 ,
        185 ,
        w ,
        h ,
        '#eee9fb',
        P ,
        0 );f .dot (110 ,
        185 );f .pointer (110 +w ,
        185 +h ,
        True )
        f .t (128 ,
        220 ,
        '1:1'if i ==2 else '16:9'if i in [4 ,
        5 ]else ('Free'if en else '自由'),
        25 ,
        P ,
        w =190 )
        f .caption (cap );f .save (f'cap-ratio-gesture-{i}',
        'CAP-025' if i<=3 else 'CAP-026',
        title ,
        'precise-selection.mdx',
        str (i )+'/6',
        'snow_shot/src/presentation/overlay/screenshotoverlayinputhandler.cpp:1018–1116,1156–1181,1514–1554;snow_shot/tests/screenshot_selection_geometry_tests.cpp:675–720')

def scene(f,copy=False):
    f.box(30,145,540,350,'#fff')
    for x,y,label,color in [(100,205,'A','#e5effa'),(250,205,'C','#e8f4eb'),(350,300,'B','#fff0dc'),(100,320,'D','#f5e8ef')]:
        f.box(x,y,85,45,color)
        f.t(x+32,y+31,label,26,w=80)
    for y in [275,380,420]:f.path(f'M62 {y}h465','#e0e5ef',4)
    for n,x in [(1,60),(2,225)]+([(3,390)] if copy else []):
        col={1:P,2:'#d68b24',3:'#239b8d'}[n]
        f.path(f'M{x} 463h24',col,3)
        f.t(x+32,470,('Region ' if f.en else '区域')+str(n),18,col,w=120)
def region(f,rect,n,ghost=False):
    x,y,w,h=rect
    col='#adb8cd' if ghost else {1:P,2:'#d68b24',3:'#239b8d'}[n]
    f.path(f'M{x} {y}h{w}v{h}h{-w}Z',col,2 if ghost else 3,dash=ghost)
def moves (en ):
    titles =['Start with two regions',
    'Drag one region to a new position',
    'Hold Space to move both regions',
    'Snap one region to another',
    'Press R to duplicate the latest region']if en else ['先建立两个区域',
    '拖动一块，改变取景位置',
    '按住 Space，整组一起移动',
    '移动单块并对齐吸附',
    '按 R，复制最后创建的区域']
    captions =['The letters belong to the screen. Region 1 covers A and region 2 covers B.',
    'Drag region 1 over C and release. Region 2 stays put; region 1 now captures C, without carrying A along.',
    'Hold Space while dragging a retained region. Both regions move by the same offset; their shapes stay unchanged.',
    'Release Space. Hold Ctrl on Windows or Command on macOS while dragging region 1 near region 2’s left edge; release at the guide.',
    'With Move idle, point at D and press R. The new bounds copy region 2, the most recently created region, and capture D at the new position.']if en else ['字母属于屏幕内容。区域1框住 A，区域2框住 B。',
    '把区域1拖到 C 上方并松开。区域2不动；区域1现在截取 C，不会把 A 的像素搬过来。',
    '按住 Space 拖动保留区域，两块都按相同位移移动，形状保持不变。',
    '松开 Space。Windows 按住 Ctrl、macOS 按住 Command，拖区域1靠近区域2左边，看到对齐线后松开。',
    '移动工具空闲时，把指针放在 D 上按 R。副本来自最后创建的区域2，取景内容变为新位置的 D。']
    configs =[[(90 ,
    195 ,
    120 ,
    90 ),
    (340 ,
    285 ,
    120 ,
    90 )],
    [(240 ,
    195 ,
    120 ,
    90 ),
    (340 ,
    285 ,
    120 ,
    90 )],
    [(220 ,
    230 ,
    120 ,
    90 ),
    (320 ,
    320 ,
    120 ,
    90 )],
    [(320 ,
    210 ,
    120 ,
    90 ),
    (320 ,
    320 ,
    120 ,
    90 )],
    [(320 ,
    210 ,
    120 ,
    90 ),
    (320 ,
    320 ,
    120 ,
    90 ),
    (90 ,
    305 ,
    120 ,
    90 )]]
    for i in range (5 ):
        f =F (titles [i ],
        ('Selection bounds move; screen pixels stay fixed'if en else '移动取景范围；屏幕像素位置不变'),
        en );scene (f ,i ==4 )
        if i >0 :
            for j ,old in enumerate (configs [i -1 ]):
                if j <len (configs [i ])and old !=configs [i ][j ]:region (f ,
                old ,
                j +1 ,
                True )
        for j ,r in enumerate (configs [i ]):region (f ,
        r ,
        j +1 )
        if i ==1 :f .arrow (150 ,
        250 ,
        300 ,
        250 );f .pointer (300 ,
        250 ,
        True )
        if i ==2 :
            f .arrow (275 ,
            240 ,
            255 ,
            275 );f .arrow (430 ,
            305 ,
            410 ,
            340 );f .pointer (260 ,
            280 ,
            True )
        if i ==3 :f .path ('M320 192V430',
        '#238b81',
        2 ,
        dash =True );f .pointer (350 ,
        250 ,
        True )
        if i ==4 :f .pointer (150 ,
        350 );f .arrow (340 ,
        375 ,
        210 ,
        375 )
        f .caption (captions [i ]);f .save (f'cap-region-move-{i+1}',
        ['CAP-043;CAP-044;CAP-045;CAP-046','CAP-043','CAP-044','CAP-045','CAP-046'][i],
        titles [i ],
        'multiple-regions.mdx',
        str (i +1 )+'/5',
        'snow_shot/src/presentation/selection/screenshotselectionmodel.cpp:224–297,903–935;snow_shot/src/presentation/overlay/screenshotoverlayinputhandler.cpp:983–1016,1124–1152,1503–1514;snow_shot/tests/screenshot_multi_region_tests.cpp:176–298')

def opacity (en ):
    f =F ('Compare the selection background'if en else '对比选区背景 0% 与 100%',
    ('Same two regions · Compact layout off'if en else '同一组区域 · 关闭紧凑布局'),
    en ,
    h =900 )
    for top ,pct in [(145 ,
    0 ),
    (445 ,
    100 )]:
        f .box (26 ,
        top ,
        548 ,
        260 );f .t (46 ,
        top +38 ,
        ('Background opacity: 'if en else '选区背景不透明度：')+str (pct )+'%',
        24 ,
        w =500 )
        y =top +65 ;f .box (60 ,
        y ,
        480 ,
        140 ,
        'url(#check)',
        '#cbd4e4',
        0 )
        if pct ==100 :
            f .box (220 ,
            y ,
            160 ,
            140 ,
            '#fff0dc',
            '#fff0dc',
            0 );f .t (235 ,
            y +58 ,
            'Middle'if en else '中间内容',
            22 ,
            w =135 )
            for k in [80 ,
            105 ]:f .path (f'M238 {y+k}h125',
            '#d6b987',
            4 )
        for x ,label in [(60 ,
        'A'),
        (380 ,
        'B')]:
            f .box (x ,
            y ,
            160 ,
            140 ,
            '#e7effb',
            '#cbd4e4',
            0 );f .t (x +61 ,
            y +80 ,
            label ,
            34 ,
            w =90 )
        f .t (46 ,
        top +238 ,
        ('The gap is transparent.'if pct ==0 else 'The original gap content is visible.')if en else ('间隙透明，原图中间内容不参与。'if pct ==0 else '原图中间内容参与背景显示。'),
        21 ,
        w =500 )
    f .caption ('The retained A and B stay opaque. Click the opacity control to reset to 0%; save a transparency-capable format to preserve the gap.'if en else 'A、B 保留区域本身仍不透明。单击不透明度控件恢复 0%；保存为支持透明度的格式，才能保留透明间隙。')
    f .save ('cap-region-background-opacity',
    'CAP-050;CAP-051',
    '0/100%原画面背景参与对照',
    'multiple-regions.mdx',
    '紧凑布局、间距与背景',
    'snow_shot/include/snow_shot/presentation/screenshotselectionbackground.h:41–116;snow_shot/src/presentation/tools/screenshottoolpalette.cpp:2824–2834,4366–4377,9681–9687')

def curve_path (points ,
closed ):
    if not points :return ''
    out =[f'M{points[0][0]:.3f} {points[0][1]:.3f}'];n =len (points )
    for i in range (n if closed else n -1 ):
        b =points [i ];c =points [(i +1 )%n ];a =points [i -1 ]if i else points [-1 ]if closed else (2 *b [0 ]-c [0 ],
        2 *b [1 ]-c [1 ]);d =points [(i +2 )%n ]if closed or i +2 <n else (2 *c [0 ]-b [0 ],
        2 *c [1 ]-b [1 ])
        ts =[0 ]
        for u ,v in [(a ,
        b ),
        (b ,
        c ),
        (c ,
        d )]:ts .append (ts [-1 ]+math .sqrt (math .hypot (v [0 ]-u [0 ],
        v [1 ]-u [1 ])))
        if min (ts [i +1 ]-ts [i ]for i in range (3 ))<=0 :out .append (f'L{c[0]} {c[1]}');continue
        def tangent (p ,
        q ,
        r ,
        t0 ,
        t1 ,
        t2 ):return tuple ((q [j ]-p [j ])/(t1 -t0 )-(r [j ]-p [j ])/(t2 -t0 )+(r [j ]-q [j ])/(t2 -t1 )for j in [0 ,
        1 ])
        t =tangent (a ,
        b ,
        c ,
        *ts [:3 ]);u =tangent (b ,
        c ,
        d ,
        *ts [1 :]);seg =ts [2 ]-ts [1 ]
        one =tuple (b [j ]+t [j ]*seg /3 for j in [0 ,
        1 ]);two =tuple (c [j ]-u [j ]*seg /3 for j in [0 ,
        1 ])
        out .append (f'C{one[0]:.3f} {one[1]:.3f} {two[0]:.3f} {two[1]:.3f} {c[0]:.3f} {c[1]:.3f}')
    return ' '.join (out )+(' Z'if closed else '')
def irregular (en ,
free =False ):
    titles =(['Press to start a freehand region',
    'Keep holding and trace the outline',
    'Release to commit the region']if free else ['Click to place curve points',
    'Preview the closing curve',
    'Double-click the endpoint to finish'])if en else (['按下左键，开始自由绘制',
    '保持按住，沿轮廓拖动',
    '松开左键，提交闭合区域']if free else ['单击放置曲线区域的点',
    '继续取点，检查闭合预览',
    '双击终点完成曲线区域'])
    captions =(['Choose Freehand region, then press the left mouse button at the outline.',
    'Keep the button held and trace around the content. A visible draft is still unfinished.',
    'Release after tracing a valid area. Inspect the closed boundary before copying or saving.']if free else ['Choose Curve region. Click the first points; moving the pointer previews the next part.',
    'Continue clicking around the outline. The hollow endpoint is a preview, not a committed point.',
    'Double-click the preview endpoint to complete the closed capture region.'])if en else (['选择自由绘制区域，在轮廓起点按下左键。',
    '保持左键按住，沿内容轮廓拖动；看到了草稿并不代表已经完成。',
    '围出有效面积后松开左键。检查闭合边界，再复制或保存。']if free else ['选择曲线区域，依次单击前几个点；移动指针会预览后续轮廓。',
    '沿轮廓继续单击。空心终点是预览位置，尚未固定。',
    '在预览终点双击完成，闭合内部成为截图区域。'])
    points =[(155 ,
    265 ),
    (315 ,
    205 ),
    (455 ,
    315 ),
    (315 ,
    430 ),
    (140 ,
    365 )]if free else [(125 ,
    260 ),
    (310 ,
    205 ),
    (455 ,
    330 ),
    (240 ,
    430 )]
    for i in range (3 ):
        f =F (titles [i ],
        ('Freehand region · Hold → drag → release'if free else 'Curve region · Click points → confirm')if en else ('自由绘制区域 · 按住→拖动→松开'if free else '曲线区域 · 逐点单击→确认'),
        en );f .box (30 ,
        145 ,
        540 ,
        350 ,
        '#fff')
        for y in [220 ,
        280 ,
        340 ,
        400 ]:f .path (f'M65 {y}h465',
        '#e0e5ef',
        5 )
        if free :
            ps =points [:1 ]if i ==0 else points if i ==2 else points [:4 ]
            if i ==0 :f .dot (*points [0 ]);f .pointer (*points [0 ],
            True )
            else :
                f .path (curve_path (ps ,
                True ),
                P ,
                3 ,
                '#eee9fb'if i ==2 else '#f4f0fc',
                dash =i ==1 )
                f .pointer (*ps [-1 ],
                i ==1 )
                if i ==1 :f .arrow (240 ,
                190 ,
                315 ,
                205 )
        else :
            ps =points [:2 ]if i ==0 else points
            f .path (curve_path (ps ,
            i >0 ),
            P ,
            3 ,
            '#eee9fb'if i >0 else 'none',
            dash =i ==1 )
            for j ,p in enumerate (ps ):
                if i <2 :f .dot (*p ,
                j +1 ,
                hollow =i ==1 and j ==3 )
            f .pointer (*(ps [-1 ]),
            False )
        f .caption (captions [i ]);prefix ='cap-freehand-region'if free else 'cap-curve-region'
        f .save (f'{prefix}-{i+1}',
        'CAP-062' if free else 'CAP-061',
        titles [i ],
        'irregular-regions.mdx',
        str (i +1 )+'/3',
        'snow_shot/src/presentation/overlay/screenshotoverlayinputhandler.cpp:332–360,725–738,1833–1908;snow_draw_engine_qt/crates/snow-draw-engine-core/src/path.rs:233–365 (centripetal curve construction)')

        # Original released glyph geometry. These are isolated icon recognitions, not a complete toolbar.
ICONS ={
'hmove':['M261.12 252.16V126.72h501.76v125.44M261.12 771.84v125.44h501.76V771.84',
'M99.84 512h824.32M225.28 386.56 99.84 512l125.44 125.44M798.72 386.56l125.44 125.44-125.44 125.44'],

'vmove':['M252.16 261.12H126.72v501.76h125.44M771.84 261.12h125.44v501.76H771.84',
'M512 99.84v824.32M386.56 225.28 512 99.84l125.44 125.44M386.56 798.72l125.44 125.44 125.44-125.44']}
def moveicon (f ,
key ,
x ,
y ,
enabled ):
    col =P if enabled else '#a6afbf';f .box (x ,
    y ,
    58 ,
    58 ,
    '#eee9fb'if enabled else '#f4f5f8',
    col )
    f .s .append (f'<g transform="translate({x+8} {y+8}) scale({42/1024})" fill="none" stroke="{col}" stroke-width="80.64" stroke-linecap="round" stroke-linejoin="round">'+''.join (f'<path d="{d}"/>'for d in ICONS [key ])+'</g>')
def axes (en ):
    f =F ('Scrolling direction and movement controls'if en else '滚动方向与可用的选区移动控件',
    'Hover to check the control name; start dragging on the control.'if en else '悬停核对名称；从控件本身按住并开始拖动。',
    en ,
    h =1100 )
    for y ,horiz in [(155 ,
    False ),
    (555 ,
    True )]:
        f .box (26 ,
        y ,
        548 ,
        365 );f .t (46 ,
        y +35 ,
        ('Horizontal scrolling'if horiz else 'Vertical scrolling')if en else ('水平滚动'if horiz else '垂直滚动'),
        24 )
        moveicon (f ,
        'hmove',
        54 ,
        y +55 ,
        horiz );moveicon (f ,
        'vmove',
        295 ,
        y +55 ,
        not horiz )
        f .t (122 ,
        y +88 ,
        ('Horizontal move'if en else '水平移动'),
        18 ,
        w =155 );f .t (363 ,
        y +88 ,
        ('Vertical move'if en else '垂直移动'),
        18 ,
        w =155 )
        f .t (54 ,
        y +140 ,
        ('Hold → drag along the active axis → release'if en else '按住可用按钮 → 沿当前轴拖动 → 松开'),
        20 ,
        w =500 )
        x =80 ;ry =y +175 ;f .box (52 ,
        ry -10 ,
        340 ,
        145 ,
        '#f4f6fb');f .path (f'M{x} {ry}h210v100H{x}Z',
        '#aeb8cc',
        2 ,
        dash =True )
        dx ,dy =(40 ,
        0 )if horiz else (0 ,
        25 );f .path (f'M{x+dx} {ry+dy}h210v100H{x+dx}Z',
        P ,
        3 );f .arrow (185 ,
        ry +50 ,
        185 +dx ,
        ry +50 +dy )
        f .t (410 ,
        ry +32 ,
        ('Trim ends:'if en else '裁剪端点：'),
        18 ,
        w =135 )
        if horiz :
            f .box (408 ,
            ry +55 ,
            130 ,
            43 ,
            '#e7effb',
            P ,
            0 );f .path (f'M413 {ry+50}v53M533 {ry+50}v53',
            R ,
            3 )
            f .t (408 ,
            ry +124 ,
            'Left / Right'if en else '左 / 右',
            18 ,
            w =145 )
        else :
            f .box (440 ,
            ry +44 ,
            50 ,
            65 ,
            '#e7effb',
            P ,
            0 );f .path (f'M433 {ry+48}h64M433 {ry+105}h64',
            R ,
            3 )
            f .t (411 ,
            ry +136 ,
            'Top / Bottom'if en else '上 / 下',
            18 ,
            w =135 )
        f .t (54 ,
        y +342 ,
        'Width and height stay unchanged.'if en else '选区宽高不变；另一方向按钮不可用。',
        20 ,
        w =500 )
    f .t (28 ,
    975 ,
    'Stop Auto-scroll before moving. Changing direction starts a fresh stitch.'if en else '先停止自动滚动再移动。改变滚动方向会重新开始拼接。',
    22 ,
    w =540 )
    f .save ('cap-scrolling-axis-controls',
    'CAP-084;CAP-096;CAP-097',
    '纵横方向可用控件/按住拖动前后/首尾trim位置对照',
    'scrolling.mdx',
    '看清拼接结果，修正开头与结尾',
    'snow_shot/src/presentation/tools/screenshottoolpalette.cpp:2984–2992,4605–4638,9849–9868;snow_shot/src/presentation/capture/scrollingselectionmovement.h;snow_shot/src/presentation/components/icons/resources/move-selection-{horizontal,vertical}.svg')

def bands (f ,
x ,
y ,
w ,
h ,
start ,
end ,
clipid ):
    f .s .append (f'<defs><clipPath id="{clipid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#{clipid})">')
    scale =h /(end -start )
    for k in range (6 ):
        top =y +(k *100 -start )*scale ;bh =100 *scale
        f .box (x ,
        top ,
        w ,
        bh ,
        ['#e7effb',
        '#eaf4e8',
        '#fff1d8',
        '#f1e8fb',
        '#e4f3f1',
        '#f8e6ed'][k ],
        '#fff',
        0 )
        f .t (x +15 ,
        top +bh *.55 ,
        str (k +1 ),
        min (32 ,
        bh *.5 ),
        w =w -20 )
    f .s .append ('</g>')
def hovertrim (en ):
    titles =['Hover to inspect stitched detail',
    'Drag the start boundary inward',
    'Release, then drag the end boundary',
    'Drag the start outward to restore content',
    'Release and leave the preview']if en else ['悬停缩略预览，检查拼接细节',
    '把首边界向内拖动',
    '松开后，再把尾边界向内拖动',
    '首边界向外拖回，恢复更多内容',
    '松开并离开预览，检查保留范围']
    captions =['Stop Auto-scroll first. Hover over the thumbnail: the corresponding detail temporarily appears inside the original capture region.',
    'Hold the start boundary and drag inward. Here sections 1–2 are excluded; the detail follows that boundary.',
    'Release the start handle, then drag the end inward. This example now keeps sections 3–5.',
    'Before exporting, drag the start boundary outward. Section 2 is restored from the retained stitch; you need not capture it again.',
    'Release and move away from the thumbnail. The source page is visible again; sections 2–5 remain selected for output.']if en else ['先停止自动滚动。悬停缩略图，对应拼接细节会临时显示在原捕获选区内。',
    '按住首边界向内拖动。本例排除第1–2段，细节预览跟随边界。',
    '先松开首边界，再按住尾边界向内拖动。本例现在保留第3–5段。',
    '导出前把首边界向外拖回。第2段从保留的拼接结果中恢复，无需重新捕获。',
    '松开后把指针移出缩略图，原目标页面重新可见；第2–5段仍为准备输出的范围。']
    states =[(0 ,
    600 ,
    200 ,
    400 ,
    None ),
    (200 ,
    600 ,
    100 ,
    300 ,
    'head'),
    (200 ,
    500 ,
    400 ,
    600 ,
    'tail'),
    (100 ,
    500 ,
    0 ,
    200 ,
    'head'),
    (100 ,
    500 ,
    400 ,
    600 ,
    None )]
    for i ,(top ,
    bottom ,
    start ,
    end ,
    handle )in enumerate (states ):
        f =F (titles [i ],
        'Auto-scroll off · Six numbered content sections'if en else '自动滚动已关闭 · 六段编号内容',
        en )
        f .t (42 ,
        155 ,
        ('Source page'if i ==4 else 'Capture region: detail')if en else ('原目标页面'if i ==4 else '捕获选区：显示细节'),
        19 ,
        w =340 )
        bands (f ,
        42 ,
        175 ,
        300 ,
        300 ,
        start ,
        end ,
        'detail');f .box (42 ,
        175 ,
        300 ,
        300 ,
        'none',
        P ,
        0 )
        f .t (420 ,
        155 ,
        'Preview'if en else '缩略预览',
        19 ,
        w =160 )
        bands (f ,
        440 ,
        175 ,
        100 ,
        300 ,
        0 ,
        600 ,
        'thumb')
        if top :f .box (440 ,
        175 ,
        100 ,
        top *.5 ,
        '#e0e4ec',
        '#e0e4ec',
        0 )
        if bottom <600 :f .box (440 ,
        175 +bottom *.5 ,
        100 ,
        (600 -bottom )*.5 ,
        '#e0e4ec',
        '#e0e4ec',
        0 )
        f .path (f'M433 {175+top*.5}h114M433 {175+bottom*.5}h114',
        R ,
        3 )
        if i ==0 :
            f .box (437 ,
            275 ,
            106 ,
            100 ,
            'none',
            P ,
            0 );f .pointer (505 ,
            320 )
        if handle :
            value =top if handle =='head'else bottom ;py =175 +value *.5
            f .path ('M42 325h300',
            R ,
            3 ,
            dash =True );f .pointer (535 ,
            py ,
            True )
            if i ==1 :f .arrow (560 ,
            182 ,
            560 ,
            270 )
            if i ==2 :f .arrow (560 ,
            465 ,
            560 ,
            430 )
            if i ==3 :f .arrow (560 ,
            270 ,
            560 ,
            230 )
        if i ==4 :f .pointer (380 ,
        455 )
        kept =(f'{top//100+1}–{bottom//100}'if top else f'1–{bottom//100}')
        f .t (42 ,
        505 ,
        ('Kept sections: 'if en else '保留段落：')+kept ,
        22 ,
        P ,
        w =510 )
        f .caption (captions [i ]);f .save (f'cap-scrolling-detail-trim-{i+1}',
        ['CAP-091','CAP-093','CAP-094','CAP-095','CAP-093;CAP-094;CAP-095'][i],
        titles [i ],
        'scrolling.mdx',
        str (i +1 )+'/5',
        'snow_shot/src/presentation/capture/screenshotscrollingthumbnailwidget.cpp:718–798,825–890;snow_shot/src/presentation/capture/screenshotscrollingcapturecontroller.cpp:59–93,593–610;snow_shot/src/presentation/capture/scrollinghoverpreview.h:33–121')

for en in [False ,
True ]:ratio (en );moves (en );opacity (en );irregular (en );irregular (en ,
True );axes (en );hovertrim (en )
GEN =ROOT /'artifacts/capture-followup-generation';GEN .mkdir (parents =True ,
exist_ok =True )
(GEN /'demo-data.json').write_text (json .dumps (DEMOS ,
ensure_ascii =False ,
indent =2 )+'\n')
meta =GEN /'frames.json';meta .write_text (json .dumps (META ,
ensure_ascii =False ,
indent =2 )+'\n')
registry =GEN /'assets.csv'
with registry .open ('w',
newline ='')as out :
    w =csv .DictWriter (out ,
    fieldnames =list (META [0 ]));w .writeheader ();w .writerows (META )
print ('Generated',
len (META ),
'dedicated bilingual assets')
