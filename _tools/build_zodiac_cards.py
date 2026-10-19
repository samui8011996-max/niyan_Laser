import subprocess, re, json, os, html, sys
B = chr(92)
D = r'C:\Users\Administrator\Downloads\12ZODIC'
OUT = r'C:\Users\Administrator\Downloads\niyan_Laser-main\default-zodiac-cards.js'
SCR = os.path.dirname(os.path.abspath(__file__))
E = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(E): E = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

# (file, cols boundaries, rows boundaries, names grid, front?)
SRC = [
 ('12ZODIC_工作區域 3 複本 3.svg', [430,820], [340,600,880], [['天秤座','處女座','獅子座'],['雙子座','巨蟹座','金牛座'],['牡羊座','射手座','魔羯座'],['雙魚座','天蠍座','水瓶座']], 'front'),
 ('12ZODIC_工作區域 3 複本 4.svg', [625], [460,780], [['牡羊座','巨蟹座'],['金牛座','獅子座'],['雙子座','處女座']], 'back'),
 ('12ZODIC_工作區域 3 複本 5.svg', [625], [460,780], [['天秤座','魔羯座'],['天蠍座','水瓶座'],['射手座','雙魚座']], 'back'),
]
JS = '''
const COLS=%COLS%,ROWS=%ROWS%,FRONT=%FRONT%;
const s=document.getElementById('S');
const SEL='path,polygon,rect,circle,line,polyline,ellipse';
const leaves=[...s.querySelectorAll(SEL)];
const rects=leaves.map(e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height,cx:r.x+r.width/2,cy:r.y+r.height/2}});
const cellOf=r=>{let c=0;while(c<COLS.length&&r.cx>=COLS[c])c++;let q=0;while(q<ROWS.length&&r.cy>=ROWS[q])q++;return [q,c]};
const res={};
const nrows=ROWS.length+1,ncols=COLS.length+1;
for(let q=0;q<nrows;q++)for(let c=0;c<ncols;c++){
  let idx=[];rects.forEach((r,i)=>{const [rq,rc]=cellOf(r);if(rq==q&&rc==c&&r.w<=600&&r.h<=600)idx.push(i)});
  let nameIdx=[],slot=null;
  if(FRONT){
    const main=idx.filter(i=>rects[i].w>100&&rects[i].h<8).sort((a,b)=>rects[b].w-rects[a].w)[0];
    const lineY=rects[main].cy;
    const wide=idx.filter(i=>rects[i].h<8&&Math.abs(rects[i].cy-lineY)<8);
    const lineX0=Math.min(...wide.map(i=>rects[i].x)),lineX1=Math.max(...wide.map(i=>rects[i].x+rects[i].w));
    nameIdx=idx.filter(i=>rects[i].cy>lineY-42&&rects[i].cy<lineY-8&&rects[i].w<130);
    const nb=nameIdx.map(i=>rects[i]);
    const x0=Math.min(...nb.map(r=>r.x)),x1=Math.max(...nb.map(r=>r.x+r.w)),y0=Math.min(...nb.map(r=>r.y)),y1=Math.max(...nb.map(r=>r.y+r.h));
    slot={cx:(x0+x1)/2,cy:(y0+y1)/2,w:x1-x0,h:y1-y0,bottom:y1,maxW:(lineX1-lineX0)*0.9};
  }
  const keep=new Set(idx.filter(i=>!nameIdx.includes(i)));
  const cl=s.cloneNode(true);const cll=[...cl.querySelectorAll(SEL)];
  cll.forEach((e,i)=>{if(!keep.has(i))e.remove()});
  for(let k=0;k<6;k++)cl.querySelectorAll('g').forEach(g=>{if(!g.querySelector(SEL))g.remove()});
  cl.querySelectorAll('defs,style').forEach(e=>e.remove());
  let minx=1e9,miny=1e9,maxx=-1e9,maxy=-1e9;
  [...keep].forEach(i=>{const r=rects[i];minx=Math.min(minx,r.x);miny=Math.min(miny,r.y);maxx=Math.max(maxx,r.x+r.w);maxy=Math.max(maxy,r.y+r.h)});
  if(slot){minx=Math.min(minx,slot.cx-slot.maxW/2);maxx=Math.max(maxx,slot.cx+slot.maxW/2)}
  res[q+','+c]={inner:cl.innerHTML,box:[minx,miny,maxx,maxy],slot};
}
document.getElementById('out').textContent=JSON.stringify(res);
'''
cards = {}
for fn, cols, rows, names, kind in SRC:
    svg = open(os.path.join(D, fn), encoding='utf-8').read()
    fill = re.search(r'fill:\s*(#[0-9a-fA-F]+)', svg).group(1)
    svg = re.sub(r'^<\?xml[^>]*\?>', '', svg).strip()
    svg = svg.replace('<svg ', '<svg id="S" width="1250.84" height="1250.84" ', 1)
    js = JS.replace('%COLS%', json.dumps(cols)).replace('%ROWS%', json.dumps(rows)).replace('%FRONT%', 'true' if kind=='front' else 'false')
    page = '<!doctype html><html><body style="margin:0">'+svg+'<pre id="out"></pre><script>'+js+'</script></body></html>'
    p = os.path.join(SCR, 'tmp_gen.html'); open(p, 'w', encoding='utf-8').write(page)
    r = subprocess.run([E,'--headless','--disable-gpu','--window-size=1300,1300','--dump-dom','file:///'+p.replace(B,'/')], capture_output=True, text=True, encoding='utf-8')
    m = re.search(r'<pre id="out">(.*?)</pre>', r.stdout, re.S)
    data = json.loads(html.unescape(m.group(1)))
    for q, row in enumerate(names):
        for c, z in enumerate(row):
            d = data['%d,%d' % (q, c)]
            inner = re.sub(r'class="cls-1"', 'fill="%s"' % fill, d['inner'])
            inner = re.sub(r'<(path|polygon|rect)(?![^>]*fill=)', r'<\1 fill="%s"' % fill, inner)
            cards.setdefault(z, {})[kind] = {'box': d['box'], 'inner': inner, 'slot': d['slot']}
# uniform scale per side so type sizes match across all 12 cards (card = 900x540 units, 10 units per mm)
out = {}
for kind, (mw, mh) in {'front': (780, 440), 'back': (780, 440)}.items():
    k = min(min(mw/(c[kind]['box'][2]-c[kind]['box'][0]), mh/(c[kind]['box'][3]-c[kind]['box'][1])) for c in cards.values())
    print(kind, 'scale', round(k, 4), '(mm per source unit %.3f)' % (k/10))
    for z, c in cards.items():
        b = c[kind]['box']; cx, cy = (b[0]+b[2])/2, (b[1]+b[3])/2
        g = 'translate(450 270) scale(%.5f) translate(%.2f %.2f)' % (k, -cx, -cy)
        rec = {'g': g, 'inner': re.sub(r'\s*\n\s*', '', c[kind]['inner'])}
        if c[kind]['slot']:
            sl = c[kind]['slot']; rec['name'] = {kk: round(v, 2) for kk, v in sl.items()}
        out.setdefault(z, {})[kind] = rec
js = ('// Auto-generated by _tools/build_zodiac_cards.py from 12ZODIC/*.svg。90x54mm 雙面星座小卡(viewBox 0 0 900 540,10 單位=1mm)。\n'
      '// front=英文面(符號+底線+英文祝賀語,name=客人文字的位置);back=中文面(固定)。\n'
      'const ZODIAC_CARDS = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
open(OUT, 'w', encoding='utf-8').write(js)
print(len(out), 'zodiacs', round(os.path.getsize(OUT)/1024), 'KB')
print(json.dumps(out['獅子座']['front']['name']))
