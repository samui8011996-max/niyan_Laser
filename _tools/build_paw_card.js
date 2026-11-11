// 用法:OT=<opentype.js 1.3.4 的 dist/opentype.min.js 路徑> node _tools/build_paw_card.js out.json "英文祝賀語" "背面第一行" "背面第二行"
// 需要 Playwright。產生的 out.json 貼到 default-zodiac-cards.js 最後的 ZODIAC_CARDS["貓掌"] = ...; 取代舊的;同目錄會出一張 out.png 預覽(跟牡羊座並排)。
// 用牡羊座小卡當版型做「貓掌」款:正面符號換貓掌、英文祝賀語重寫;背面兩行中文重寫。字用 ChenYu 手寫細字轉路徑。
const fs = require('fs');
const { chromium } = require('D:/下載區/20261111/niyan_dashboard/node_modules/playwright');
const [,, OUTJSON, EN, TITLE, ZH] = process.argv;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:900,height:540}});
  await p.goto('file:///C:/Users/Administrator/Downloads/niyan_Laser-main/index.html'); await p.waitForTimeout(800);
  await p.addScriptTag({path: process.env.OT});
  const rec = await p.evaluate(async ({EN, TITLE, ZH}) => {
    const b64 = DEFAULT_FONTS.CHENYU.split(',')[1];
    const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
    const font = opentype.parse(bin.buffer);
    const BASE = '牡羊座';
    const SEL = 'path,polygon,rect,circle,line,polyline,ellipse';
    const draw = r => { document.body.innerHTML = '<svg id="c" xmlns="http://www.w3.org/2000/svg" width="900" height="540" viewBox="0 0 900 540"><g id="g" transform="'+r.g+'">'+r.inner+'</g></svg>'; document.body.style.margin=0; return document.getElementById('g'); };
    const box = els => { const r = els.map(e => e.getBoundingClientRect()); const x0=Math.min(...r.map(a=>a.x)), y0=Math.min(...r.map(a=>a.y)), x1=Math.max(...r.map(a=>a.x+a.width)), y1=Math.max(...r.map(a=>a.y+a.height)); return {x0,y0,x1,y1,cx:(x0+x1)/2,cy:(y0+y1)/2,w:x1-x0,h:y1-y0}; };
    // 文字轉路徑,置中在 (cx, cy),字高(含上下伸部的外框高)= h
    const textPath = (str, cx, cy, h) => {
      const tmp = font.getPath(str, 0, 0, 100); const bb = tmp.getBoundingBox();
      const s = 100 * h / (bb.y2 - bb.y1);
      const p = font.getPath(str, 0, 0, s); const q = p.getBoundingBox();
      const dx = cx - (q.x1+q.x2)/2, dy = cy - (q.y1+q.y2)/2;
      const p2 = font.getPath(str, dx, dy, s);
      return {d: p2.toPathData(2), w: q.x2-q.x1};
    };
    const out = {};
    // ── 正面 ──
    const fr = ZODIAC_CARDS[BASE].front;
    let g = draw(fr);
    const els = [...g.querySelectorAll(SEL)];
    const bbs = els.map(e => box([e]));
    const mainI = bbs.reduce((a,x,i) => x.w > bbs[a].w ? i : a, 0);
    const line = els.filter((e,i) => bbs[i].h < 12 && Math.abs(bbs[i].cy - bbs[mainI].cy) < 8);
    const lineBox = box(line);
    const sym = els.filter((e,i) => bbs[i].cy < lineBox.y0 - 5);
    const slo = els.filter((e,i) => bbs[i].cy > lineBox.y1 + 2);
    const symBox = box(sym), sloBox = box(slo);
    // 貓掌圖案:等比縮到原符號的高度,置中在原符號位置
    const icon = new DOMParser().parseFromString(DEFAULT_LIBRARY['貓掌'], 'image/svg+xml').documentElement;
    const vb = icon.getAttribute('viewBox').split(/[\s,]+/).map(Number);
    const ih = symBox.h * 1.15, k = ih / vb[3];
    const iconInner = [...icon.querySelectorAll(SEL)].map(e => { e.setAttribute('fill', INK); return e.outerHTML; }).join('');
    const iconG = '<g transform="translate('+(symBox.cx - vb[2]*k/2).toFixed(2)+' '+(symBox.cy - ih/2).toFixed(2)+') scale('+k.toFixed(4)+')" stroke-width="'+(1.5/k).toFixed(2)+'">'+iconInner+'</g>';
    const en = textPath(EN, lineBox.cx, sloBox.cy, sloBox.h);
    // 新增的東西用卡片座標畫,外面包一層「卡片座標 → 原稿座標」的反矩陣
    const m = g.getCTM().inverse();
    const inv = 'matrix('+[m.a,m.b,m.c,m.d,m.e,m.f].map(v=>+v.toFixed(5)).join(' ')+')';
    const keepLine = line.map(e => e.outerHTML).join('');
    out.front = {g: fr.g, stroke: fr.stroke, name: fr.name,
      inner: keepLine + '<g transform="'+inv+'" stroke-width="1.5">' + iconG + '<path fill="'+INK+'" d="'+en.d+'"/></g>'};
    // ── 背面:兩行,沿用牡羊座背面兩行的位置跟字高 ──
    const bk = ZODIAC_CARDS[BASE].back;
    g = draw(bk);
    const be = [...g.querySelectorAll(SEL)]; const bb = be.map(e => box([e]));
    const midY = (Math.min(...bb.map(a=>a.cy)) + Math.max(...bb.map(a=>a.cy))) / 2;
    const l1 = box(be.filter((e,i) => bb[i].cy < midY)), l2 = box(be.filter((e,i) => bb[i].cy >= midY));
    const t1 = textPath(TITLE, 450, l1.cy, l1.h), t2 = textPath(ZH, 450, l2.cy, l2.h);
    out.back = {g: 'translate(0 0)', stroke: 1.5, inner: '<path fill="'+INK+'" d="'+t1.d+'"/><path fill="'+INK+'" d="'+t2.d+'"/>'};
    return out;
  }, {EN, TITLE, ZH});
  fs.writeFileSync(OUTJSON, JSON.stringify(rec));
  // 預覽:跟牡羊座並排
  await p.evaluate(r => { ZODIAC_CARDS['貓掌'] = r; }, rec);
  await p.evaluate(() => {
    const row = z => '<div style="display:flex;gap:6px;margin:6px">' + ['front','back'].map(s => '<div style="border:1px solid #999">'+buildCardSvg({zodiac:z, text:'Amy'}, s, settings).svg.replace(/width="[\d.]+" height="[\d.]+"/, 'width="420" height="252"')+'</div>').join('') + '</div>';
    document.body.innerHTML = '<div style="background:#fff;display:inline-block">'+row('牡羊座')+row('貓掌')+'</div>';
  });
  await p.screenshot({path: OUTJSON.replace('.json','.png'), fullPage:true});
  await b.close();
})();
