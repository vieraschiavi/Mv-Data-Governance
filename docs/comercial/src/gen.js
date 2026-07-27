const P = require("pptxgenjs");
const fs = require("fs");
const { variants } = require("./content_i18n.js");
const { CHART_SIN, CHART_CON, CATS, SERIES_SIN, SERIES_CON } = require("./content.js");

const OUT = __dirname;
const esc = s => String(s);

/* ===================== HTML: DECK ===================== */
const DECK_CSS = `
:root[data-theme="dark"]{
  --navy:#0a1a2f; --surface:#0e2138; --surface2:#12283f; --line:#20384f;
  --ink:#eef4fb; --muted:#a2b6cd; --faint:#6f86a0;
  --amber:#f2b441; --amber-deep:#e39a2e; --good:#37c891; --warn:#f2b441; --bad:#e0685c;
  --s-pes:#dc5f53; --s-base:#e6a636; --s-opt:#2fb783;
  --sans:"Helvetica Neue",Arial,"Liberation Sans",sans-serif;
  --mono:"DejaVu Sans Mono","Liberation Mono",monospace;
}
*{box-sizing:border-box}
body{margin:0;background:var(--navy);color:var(--ink);font-family:var(--sans);
  -webkit-font-smoothing:antialiased;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.num{font-variant-numeric:tabular-nums;font-family:var(--mono)}
mark{background:rgba(242,180,65,.24);color:var(--ink);padding:0 4px;border-radius:3px}
.amb{color:var(--amber-deep)} .good{color:var(--good)} .warn{color:var(--warn)} .bad{color:var(--bad)}
.slide{position:relative;overflow:hidden;display:flex;flex-direction:column;justify-content:center;
  padding:52px 76px;border-bottom:1px solid var(--line);min-height:100vh}
.inner{width:100%;max-width:1080px;margin:0 auto}
.kick{font-size:12px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--amber);
  display:flex;align-items:center;gap:10px;margin-bottom:16px}
.kick .no{font-family:var(--mono);color:var(--faint);letter-spacing:0}
.slide h2{font-size:36px;font-weight:850;letter-spacing:-.02em;line-height:1.1}
.slide .lead{color:var(--muted);font-size:16px;max-width:66ch;margin-top:14px;line-height:1.5}
.cover{background:radial-gradient(820px 440px at 80% -10%,rgba(242,180,65,.16),transparent 60%),linear-gradient(160deg,var(--surface),var(--navy))}
.brandrow{display:flex;align-items:center;gap:13px;margin-bottom:24px}
.glyph{width:44px;height:44px;border-radius:11px;flex:none;background:linear-gradient(150deg,var(--amber),var(--amber-deep));
  display:grid;place-items:center;color:#1a1205;font-weight:850;font-family:var(--mono);font-size:20px}
.brandrow .nm{font-size:19px;font-weight:800;letter-spacing:-.01em}
.brandrow .tg{font-size:12px;color:var(--faint)}
.cover h1{font-size:54px;font-weight:850;letter-spacing:-.03em;line-height:1.03}
.cover .sub{color:var(--muted);font-size:18px;max-width:62ch;margin-top:18px;line-height:1.5}
.cover .foot{margin-top:30px;display:flex;flex-wrap:wrap;gap:8px 22px;font-size:13px;color:var(--faint)}
.cover .foot b{color:var(--muted)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:24px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px}
.card h4{margin:0 0 6px;font-size:16px;font-weight:800}
.card p{margin:0;font-size:13.5px;color:var(--muted)}
.tag{display:inline-block;font-size:10.5px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;padding:3px 9px;border-radius:20px;margin-bottom:9px}
.tag.g{background:rgba(55,200,145,.15);color:var(--good)}
.tag.w{background:rgba(242,180,65,.16);color:var(--amber-deep)}
.tag.b{background:rgba(224,104,92,.15);color:var(--bad)}
.tag.a{background:rgba(242,180,65,.15);color:var(--amber-deep)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border:1px solid var(--line);border-radius:14px;overflow:hidden;margin-top:24px}
.stat{background:var(--surface);padding:22px}
.stat .v{font-size:35px;font-weight:850;letter-spacing:-.02em;line-height:1.02}
.stat .k{font-size:12px;font-weight:700;letter-spacing:.03em;text-transform:uppercase;color:var(--faint);margin-top:9px}
.stat .k.amb{color:var(--amber-deep)}
.stat .n{font-size:12.5px;color:var(--muted);margin-top:5px}
.tbl-wrap{overflow:hidden;margin-top:22px;border:1px solid var(--line);border-radius:12px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{padding:9px 13px;text-align:right;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}
thead th{background:var(--surface2);color:var(--muted);font-weight:700;font-size:11px;letter-spacing:.04em;text-transform:uppercase}
tbody tr:last-child td{border-bottom:0}
tbody tr.hl td{background:rgba(242,180,65,.08)}
.callout{background:rgba(242,180,65,.08);border:1px solid rgba(242,180,65,.30);border-left:3px solid var(--amber);border-radius:11px;padding:16px 20px;margin-top:22px}
.callout.risk{background:rgba(224,104,92,.08);border-color:rgba(224,104,92,.30);border-left-color:var(--bad)}
.callout .t{font-size:11.5px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:var(--amber-deep);margin-bottom:5px}
.callout p{margin:0;font-size:14.5px;max-width:84ch}
ul.tick{list-style:none;padding:0;margin:22px 0 0}
ul.tick li{position:relative;padding:11px 0 11px 26px;font-size:15px;color:var(--muted);border-bottom:1px solid var(--line)}
ul.tick li:last-child{border-bottom:0}
ul.tick li::before{content:"";position:absolute;left:3px;top:18px;width:8px;height:8px;border-radius:2px;background:var(--amber)}
ul.tick.risk li::before{background:var(--bad);border-radius:50%}
ul.tick li b{color:var(--ink);font-weight:700}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:20px}
.chart{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px 16px 10px}
.chart .ct{font-size:13px;font-weight:800}
.chart .cs{font-size:11.5px;color:var(--faint);margin:2px 0 8px}
svg{display:block;width:100%;height:auto;overflow:visible}
.axlab{font-family:var(--mono);font-size:10px;fill:var(--faint)}
.endlab{font-family:var(--mono);font-size:10.5px;font-weight:700}
.legend{display:flex;flex-wrap:wrap;gap:14px;margin-top:12px;font-size:12.5px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.dot{width:10px;height:10px;border-radius:3px;flex:none}
.flow{display:flex;align-items:stretch;gap:0;margin-top:24px}
.step{flex:1;background:var(--surface);border:1px solid var(--line);padding:16px 18px}
.step:first-child{border-radius:12px 0 0 12px}
.step:last-child{border-radius:0 12px 12px 0}
.step .st{font-family:var(--mono);font-size:11px;color:var(--amber-deep);font-weight:800}
.step h4{margin:6px 0 4px;font-size:14.5px;font-weight:800}
.step p{margin:0;font-size:12.5px;color:var(--muted)}
.closing{background:radial-gradient(700px 400px at 20% 110%,rgba(242,180,65,.14),transparent 60%),linear-gradient(200deg,var(--surface),var(--navy))}
.contact{margin-top:24px;display:flex;flex-wrap:wrap;gap:10px 26px;font-size:15px;color:var(--muted)}
.contact b{color:var(--ink)}
@media print{
  @page{size:13.33in 7.5in;margin:0}
  html,body{background:#0a1a2f}
  .slide{min-height:0;height:7.5in;width:13.33in;page-break-after:always;break-after:page;border-bottom:0}
  .slide:last-child{page-break-after:auto;break-after:auto}
}`;

function chartSVG(D, title, sub){
  const P2=D.points, E=D.ends;
  return `<div class="chart"><div class="ct">${title}</div><div class="cs">${sub}</div>
    <svg viewBox="0 0 480 250" role="img">
      <line x1="8" y1="242" x2="472" y2="242" stroke="var(--line)"/>
      <line x1="8" y1="182" x2="472" y2="182" stroke="var(--line)" stroke-dasharray="2 4"/>
      <line x1="8" y1="122" x2="472" y2="122" stroke="var(--line)" stroke-dasharray="2 4"/>
      <line x1="8" y1="62"  x2="472" y2="62"  stroke="var(--line)" stroke-dasharray="2 4"/>
      <text class="axlab" x="8" y="58">300k</text><text class="axlab" x="8" y="118">200k</text><text class="axlab" x="8" y="178">100k</text>
      <polyline fill="none" stroke="var(--s-pes)" stroke-width="2" points="${P2.pes}"/>
      <polyline fill="none" stroke="var(--s-base)" stroke-width="2.4" points="${P2.base}"/>
      <polyline fill="none" stroke="var(--s-opt)" stroke-width="2" points="${P2.opt}"/>
      <circle cx="472" cy="${P2.pes.split(' ').pop().split(',')[1]}" r="3.2" fill="var(--s-pes)"/>
      <circle cx="472" cy="${P2.base.split(' ').pop().split(',')[1]}" r="3.6" fill="var(--s-base)"/>
      <circle cx="472" cy="${P2.opt.split(' ').pop().split(',')[1]}" r="3.2" fill="var(--s-opt)"/>
      <text class="endlab" x="466" y="${E.pes[0]}" text-anchor="end" fill="var(--s-pes)">${E.pes[1]}</text>
      <text class="endlab" x="466" y="${E.base[0]}" text-anchor="end" fill="var(--s-base)">${E.base[1]}</text>
      <text class="endlab" x="466" y="${E.opt[0]}" text-anchor="end" fill="var(--s-opt)">${E.opt[1]}</text>
      <text class="axlab" x="8" y="250">1m</text><text class="axlab" x="120" y="250">3m</text>
      <text class="axlab" x="236" y="250">6m</text><text class="axlab" x="350" y="250">12m</text><text class="axlab" x="462" y="250">18m</text>
    </svg></div>`;
}

function statV(v, token){
  const isWord = token==="good";
  const cls = (isWord?"":"num ") + (token==="amb"?"amb":(token==="good"?"good":""));
  return `<div class="v ${cls.trim()}">${v}</div>`;
}

function deckSlide(s){
  const head = `<div class="kick"><span class="no">${s.no}</span> ${s.kick}</div>`;
  const lead = s.lead? `<p class="lead">${s.lead}</p>`:"";
  const callout = c => `<div class="callout"><div class="t">${c[0]}</div><p>${c[1]}</p></div>`;
  if(s.type==="cover"){
    const foot = s.foot.map(f=> (f.length>1 && f[0]) ? `<span><b>${f[0]}:</b> ${f[1]}</span>` : `<span>${f[f.length-1]}</span>`).join("");
    return `<section class="slide cover"><div class="inner">
      <div class="brandrow"><div class="glyph">MV</div><div><div class="nm">${s.brand[0]}</div><div class="tg">${s.brand[1]}</div></div></div>
      <h1>${s.h1}</h1><p class="sub">${s.sub}</p><div class="foot">${foot}</div></div></section>`;
  }
  if(s.type==="badcards"){
    const cards = s.cards.map(c=>`<div class="card"><h4 class="bad">${c[0]}</h4><p>${c[1]}</p></div>`).join("");
    return `<section class="slide"><div class="inner">${head}<h2>${s.title}</h2>${lead}<div class="grid3">${cards}</div></div></section>`;
  }
  if(s.type==="table4"){
    let title=s.title;
    if(s.titleMark) title=title.replace(s.titleMark, `<mark>${s.titleMark}</mark>`);
    const th=s.head.map(h=>`<th>${h}</th>`).join("");
    const rows=s.rows.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join("")}</tr>`).join("");
    return `<section class="slide"><div class="inner">${head}<h2>${title}</h2>${lead}
      <div class="tbl-wrap"><table><thead><tr>${th}</tr></thead><tbody>${rows}</tbody></table></div></div></section>`;
  }
  if(s.type==="tagcards"){
    const cards=s.cards.map((c,i)=>`<div class="card"${i===1?' style="border-color:rgba(242,180,65,.45)"':''}><span class="tag ${c[1]}">${c[0]}</span><h4>${c[2]}</h4><p>${c[3]}</p></div>`).join("");
    return `<section class="slide"><div class="inner">${head}<h2>${s.title}</h2>${lead}<div class="grid3">${cards}</div>${s.callout?callout(s.callout):""}</div></section>`;
  }
  if(s.type==="flow"){
    const steps=s.steps.map(st=>`<div class="step"><div class="st">${st[0]}</div><h4>${st[1]}</h4><p>${st[2]}</p></div>`).join("");
    return `<section class="slide"><div class="inner">${head}<h2>${s.title}</h2>${lead}<div class="flow">${steps}</div>${callout(s.callout)}</div></section>`;
  }
  if(s.type==="statscallout"){
    const st=s.stats.map(x=>`<div class="stat">${statV(x[0],x[1])}<div class="k${s.kAmber?' amb':''}">${x[2]}</div><div class="n">${x[3]}</div></div>`).join("");
    return `<section class="slide"><div class="inner">${head}<h2>${s.title}</h2><div class="stats">${st}</div>${callout(s.callout)}</div></section>`;
  }
  if(s.type==="charts"){
    const leg=s.legend.map((l,i)=>{
      const col=["--s-pes","--s-base","--s-opt"][i];
      let extra="";
      if(l[1]) extra = i===1? ` <b class="amb">${l[1]}</b>` : ` <span style="color:var(--faint)">${l[1]}</span>`;
      return `<span><i class="dot" style="background:var(${col})"></i> ${l[0]}${extra}</span>`;
    }).join("");
    return `<section class="slide"><div class="inner">${head}<h2>${s.title}</h2>
      <div class="charts">${chartSVG(CHART_SIN,s.c1[0],s.c1[1])}${chartSVG(CHART_CON,s.c2[0],s.c2[1])}</div>
      <div class="legend">${leg}</div></div></section>`;
  }
  if(s.type==="ticklist"){
    const items=s.items.map(it=>`<li><b>${it[0]}</b> ${it[1]}</li>`).join("");
    return `<section class="slide"><div class="inner">${head}<h2>${s.title}</h2><ul class="tick${s.risk?' risk':''}">${items}</ul></div></section>`;
  }
  if(s.type==="closing"){
    const cards=s.cards.map((c,i)=>`<div class="card"${i===1?' style="border-color:rgba(242,180,65,.45)"':''}><span class="tag ${c[1]}">${c[0]}</span><h4>${c[2]}</h4><p>${c[3]}</p></div>`).join("");
    const contact=s.contact.map(c=> c[0]&&c[1]?`<span><b>${c[0]}</b> ${c[1]}</span>`: `<span>${c[0]||c[1]}</span>`).join("");
    return `<section class="slide closing"><div class="inner">${head}<h2>${s.title}</h2>${lead}<div class="grid2">${cards}</div><div class="contact">${contact}</div></div></section>`;
  }
  return "";
}

function deckHTML(v){
  return `<!doctype html><html lang="${v.lang}" data-theme="dark"><head><meta charset="utf-8">
<title>${v.title}</title><meta name="viewport" content="width=device-width, initial-scale=1">
<style>${DECK_CSS}</style></head><body>
${v.deck.map(deckSlide).join("\n")}
</body></html>`;
}

/* ===================== HTML: ONE-PAGER ===================== */
const OP_CSS = `
:root{--surface:#ffffff;--surface2:#f4f7fb;--line:#d3ddea;--ink:#0f2137;--muted:#3d5069;--faint:#6b7a90;
  --amber:#b3720f;--amber-deep:#9a6109;--good:#0d8a5e;--bad:#bd4034;
  --sans:"Helvetica Neue",Arial,"Liberation Sans",sans-serif;--mono:"DejaVu Sans Mono","Liberation Mono",monospace;}
*{box-sizing:border-box}html,body{margin:0;padding:0}
body{background:#fff;color:var(--ink);font-family:var(--sans);line-height:1.5;-webkit-font-smoothing:antialiased;font-size:10.4pt}
.sheet{max-width:190mm;margin:0 auto;padding:2mm 0}
.num{font-variant-numeric:tabular-nums;font-family:var(--mono)}
h1,h2,h3,h4{margin:0;line-height:1.15}
.mast{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;padding-bottom:11px;border-bottom:2px solid var(--amber)}
.mark{display:flex;align-items:center;gap:10px}
.glyph{width:32px;height:32px;border-radius:8px;flex:none;background:linear-gradient(150deg,#f2b441,#e39a2e);display:grid;place-items:center;color:#1a1205;font-weight:850;font-family:var(--mono);font-size:15px}
.mark .nm{font-size:17px;font-weight:850;letter-spacing:-.02em}
.mark .tg{font-size:10.5px;color:var(--faint);margin-top:1px}
.mast .rt{text-align:right;font-size:10px;color:var(--faint);line-height:1.55}
.mast .rt b{color:var(--muted);font-weight:700}
.thesis{margin:12px 0 4px;font-size:15px;font-weight:750;letter-spacing:-.01em;line-height:1.34}
.thesis mark{background:rgba(242,180,65,.28);color:var(--ink);padding:0 3px;border-radius:3px}
.subt{color:var(--muted);font-size:11.5px;max-width:84ch;margin:0}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:13px 0 4px}
.kpi{background:var(--surface);padding:9px 12px}
.kpi .k{font-size:9px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--faint)}
.kpi .v{font-size:19px;font-weight:850;margin-top:3px;letter-spacing:-.01em;font-family:var(--sans);font-variant-numeric:tabular-nums}
.kpi .n{font-size:9.5px;color:var(--muted);margin-top:2px;line-height:1.35}
.good{color:var(--good)} .amb{color:var(--amber-deep)}
.body{display:grid;grid-template-columns:1.05fr 1fr;gap:20px;margin-top:16px}
.blk+.blk{margin-top:13px}
.blk h3{font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--amber-deep);margin-bottom:6px}
.blk p{margin:0;font-size:11px;color:var(--muted)}
.blk b{color:var(--ink);font-weight:700}
ul.tick{list-style:none;padding:0;margin:0}
ul.tick li{position:relative;padding:5px 0 5px 17px;font-size:11px;color:var(--muted);border-bottom:1px solid var(--line)}
ul.tick li:last-child{border-bottom:0}
ul.tick li::before{content:"";position:absolute;left:2px;top:10px;width:7px;height:7px;border-radius:2px;background:#e6a636}
ul.tick li b{color:var(--ink);font-weight:700}
.tbl-wrap{border:1px solid var(--line);border-radius:10px;overflow:hidden}
table{border-collapse:collapse;width:100%;font-size:10.5px}
th,td{padding:5px 8px;text-align:right;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}
thead th{background:var(--surface2);color:var(--muted);font-weight:700;font-size:9px;letter-spacing:.04em;text-transform:uppercase}
tbody tr:last-child td{border-bottom:0}
tbody tr.hl td{background:rgba(230,166,54,.14)}
td.pos{color:var(--good)}
caption{caption-side:bottom;text-align:left;color:var(--faint);font-size:9.5px;padding:6px 3px 0;line-height:1.42}
.model{background:rgba(230,166,54,.11);border:1px solid rgba(230,166,54,.34);border-left:3px solid #e6a636;border-radius:8px;padding:9px 13px;margin-top:12px}
.model .t{font-size:9.5px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--amber-deep);margin-bottom:3px}
.model p{margin:0;font-size:11px;color:var(--ink)}
.seam{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px}
.chip{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:8px 10px}
.chip .h{font-size:10.5px;font-weight:800;color:var(--ink);margin-bottom:2px}
.chip .m{font-size:14px;font-weight:850;font-family:var(--mono);letter-spacing:-.01em}
.chip .s{font-size:9px;color:var(--faint);margin-top:1px}
.status{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.pill{font-size:9.5px;font-weight:700;padding:3px 9px;border-radius:20px;letter-spacing:.02em;display:inline-flex;align-items:center;gap:5px}
.pill.g{background:rgba(13,138,94,.16);color:var(--good)}
.pill.w{background:rgba(179,114,15,.17);color:var(--amber-deep)}
.pill.b{background:rgba(189,64,52,.15);color:var(--bad)}
.cta{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-top:16px;padding:12px 16px;background:var(--surface2);border:1px solid var(--line);border-radius:10px}
.cta .big{font-size:14px;font-weight:800;letter-spacing:-.01em}
.cta .sm{font-size:11px;color:var(--muted);margin-top:2px}
.cta .who{text-align:right;font-size:11px;color:var(--muted);line-height:1.5}
.cta .who b{color:var(--ink)}
.foot{margin-top:11px;font-size:9px;color:var(--faint);line-height:1.5}
.foot b{color:var(--muted)}
@page{size:A4;margin:11mm}`;

function opHTML(v){
  const o=v.op;
  const rt=o.rt.map(r=> r[0]?`<div><b>${r[0]}</b> ${r[1]}</div>`:`<div>${r[1]}</div>`).join("");
  const kpis=o.kpis.map(k=>`<div class="kpi"><div class="k">${k[0]}</div><div class="v ${k[2]==='good'?'good':(k[2]==='amb'?'num amb':(k[2]==='num'?'num':''))}">${k[1]}</div><div class="n">${k[3]}</div></div>`).join("");
  const sells=o.sells.map(s=>`<li><b>${s[0]}</b>${s[1]}</li>`).join("");
  const chips=o.chips.map(c=>`<div class="chip"><div class="h">${c[0]}</div><div class="m">${c[1]}</div><div class="s">${c[2]}</div></div>`).join("");
  const th=o.tblHead.map(h=>`<th>${h}</th>`).join("");
  const rows=o.tblRows.map(r=>`<tr class="${r[0]}"><td>${r[1]}</td><td class="num">${r[2]}</td><td class="num">${r[3]}</td><td class="num pos">${r[4]}</td><td class="num">${r[5]}</td></tr>`).join("");
  const pills=o.pills.map(p=>`<span class="pill ${p[0]}">${p[1]}</span>`).join("");
  return `<!doctype html><html lang="${v.lang}"><head><meta charset="utf-8"><title>${v.title.replace('Pitch deck','One-pager')}</title>
<meta name="viewport" content="width=device-width, initial-scale=1"><style>${OP_CSS}</style></head><body>
<div class="sheet">
  <div class="mast">
    <div class="mark"><div class="glyph">MV</div><div><div class="nm">MV Data Governance</div><div class="tg">${o.tagline}</div></div></div>
    <div class="rt">${rt}</div>
  </div>
  <p class="thesis">${o.thesis}</p>
  <p class="subt">${o.subt}</p>
  <div class="kpis">${kpis}</div>
  <div class="body">
    <div class="col">
      <div class="blk"><h3>${o.sellsH}</h3><ul class="tick">${sells}</ul></div>
      <div class="blk"><h3>${o.seamH}</h3><p>${o.seam}</p></div>
      <div class="blk"><h3>${o.marketH}</h3><div class="seam">${chips}</div></div>
    </div>
    <div class="col">
      <div class="blk"><h3>${o.tblH}</h3><div class="tbl-wrap"><table><thead><tr>${th}</tr></thead><tbody>${rows}</tbody><caption>${o.tblCap}</caption></table></div></div>
      <div class="model"><div class="t">${o.modelH}</div><p>${o.model}</p></div>
      <div class="blk"><h3>${o.statusH}</h3><div class="status">${pills}</div></div>
    </div>
  </div>
  <div class="cta">
    <div><div class="big amb">${o.ctaBig}</div><div class="sm">${o.ctaSm}</div></div>
    <div class="who"><b>${o.who[0]}</b> ${o.who[1]}<br>${o.who[2]}</div>
  </div>
  <p class="foot">${o.foot}</p>
</div></body></html>`;
}

/* ===================== PPTX ===================== */
const NAVY="0A1A2F",SURF="0E2138",SURF2="12283F",LINE="24405C",INK="EEF4FB",MUTE="A6BAD1",FAINT="7C93AE",
  AMB="F2B441",AMBD="E39A2E",GOOD="37C891",BAD="E0685C",PES="DC5F53",BASE="E6A636",OPT="2FB783",F="Arial";
const W=13.3,MX=0.62,CW=W-2*MX;

function buildPPTX(v){
  const pres=new P();
  pres.layout="LAYOUT_WIDE"; pres.author="VieraSchiavi"; pres.company="MV Data Governance";
  const bg=s=>{s.background={color:NAVY};};
  const glow=(s,x,y,d,tr)=>s.addShape(pres.ShapeType.ellipse,{x,y,w:d,h:d,fill:{color:AMB,transparency:tr},line:{type:"none"}});
  const card=(s,x,y,w,h,o={})=>s.addShape(pres.ShapeType.roundRect,{x,y,w,h,rectRadius:0.09,fill:{color:o.fill||SURF},line:{color:o.border||LINE,width:1}});
  const tagPill=(s,x,y,txt,col)=>{const w=Math.max(0.7,0.16+txt.length*0.083);
    s.addShape(pres.ShapeType.roundRect,{x,y,w,h:0.28,rectRadius:0.14,fill:{color:col,transparency:82},line:{type:"none"}});
    s.addText(txt.toUpperCase(),{x,y,w,h:0.28,fontFace:F,fontSize:9,bold:true,color:col,align:"center",valign:"middle",margin:0,charSpacing:1});};
  const TAGCOL={g:GOOD,w:AMBD,b:BAD,a:AMBD};
  const head=(s,no,kick,title,o={})=>{bg(s);
    s.addText([{text:no+"  ",options:{color:FAINT,bold:true}},{text:kick.toUpperCase(),options:{color:AMB,bold:true}}],
      {x:MX,y:0.44,w:CW,h:0.3,fontFace:F,fontSize:12.5,charSpacing:2,margin:0});
    s.addText(title,{x:MX,y:0.78,w:o.tw||CW,h:o.th||0.95,fontFace:F,fontSize:o.ts||26,bold:true,color:INK,margin:0,lineSpacingMultiple:1.02});
    if(o.lead) s.addText(o.lead,{x:MX,y:o.ly||1.74,w:11.4,h:0.7,fontFace:F,fontSize:13.5,color:MUTE,margin:0,lineSpacingMultiple:1.1});};
  const calloutBox=(s,cy,c,h=1.35)=>{card(s,MX,cy,CW,h,{fill:"22180A",border:"5A4620"});
    s.addShape(pres.ShapeType.rect,{x:MX,y:cy,w:0.06,h,fill:{color:AMB},line:{type:"none"}});
    s.addText(c[0].toUpperCase(),{x:MX+0.3,y:cy+0.18,w:CW-0.6,h:0.3,fontFace:F,fontSize:11,bold:true,color:AMBD,margin:0,charSpacing:1.5});
    const rich = c[2]!==undefined ? [{text:c[2],options:{bold:true,color:INK}},{text:c[3],options:{color:MUTE}}] : [{text:c[1].replace(/<[^>]+>/g,""),options:{color:MUTE}}];
    s.addText(rich,{x:MX+0.3,y:cy+0.5,w:CW-0.6,h:h-0.6,fontFace:F,fontSize:14,margin:0,valign:"top",lineSpacingMultiple:1.12});};

  v.deck.forEach(sl=>{
    const s=pres.addSlide();
    if(sl.type==="cover"){
      bg(s); glow(s,9.7,-2.1,6.2,80); glow(s,10.9,-1.2,3.6,66);
      s.addShape(pres.ShapeType.roundRect,{x:MX,y:0.62,w:0.62,h:0.62,rectRadius:0.11,fill:{color:AMB},line:{type:"none"}});
      s.addText("MV",{x:MX,y:0.62,w:0.62,h:0.62,fontFace:F,fontSize:20,bold:true,color:"1A1205",align:"center",valign:"middle",margin:0});
      s.addText(sl.brand[0],{x:MX+0.78,y:0.63,w:7,h:0.34,fontFace:F,fontSize:17,bold:true,color:INK,margin:0,valign:"middle"});
      s.addText(sl.brand[1],{x:MX+0.78,y:0.97,w:7,h:0.28,fontFace:F,fontSize:11.5,color:FAINT,margin:0,valign:"middle"});
      s.addText(sl.h1.replace(/<br>/g,"\n"),{x:MX,y:2.05,w:11.6,h:1.95,fontFace:F,fontSize:39,bold:true,color:INK,margin:0,lineSpacingMultiple:1.02,charSpacing:-0.5});
      s.addText(sl.sub,{x:MX,y:4.28,w:9.9,h:1.2,fontFace:F,fontSize:14.5,color:MUTE,margin:0,lineSpacingMultiple:1.22});
      s.addShape(pres.ShapeType.line,{x:MX,y:6.05,w:CW,h:0,line:{color:LINE,width:1}});
      let fx=MX;
      sl.foot.forEach(f=>{
        const k=(f.length>1&&f[0])?f[0]:null, val=f[f.length-1];
        const t=(k?k+": ":"")+val, w=0.2+t.length*0.085;
        s.addText(k?[{text:k+": ",options:{color:MUTE,bold:true}},{text:val,options:{color:FAINT}}]:[{text:val,options:{color:FAINT}}],
          {x:fx,y:6.35,w,h:0.32,fontFace:F,fontSize:12.5,margin:0,valign:"middle"});
        fx+=w+0.35;
      });
      s.addNotes(sl.kick||"Portada.");
      return;
    }
    if(sl.type==="badcards"){
      head(s,sl.no,sl.kick,sl.title,{ts:26,lead:sl.lead});
      const g=0.34,w=(CW-2*g)/3,y=2.85,h=3.3;
      sl.cards.forEach((c,i)=>{const x=MX+i*(w+g);card(s,x,y,w,h);
        s.addShape(pres.ShapeType.roundRect,{x:x+0.28,y:y+0.3,w:0.42,h:0.42,rectRadius:0.1,fill:{color:BAD,transparency:80},line:{type:"none"}});
        s.addText("✕",{x:x+0.28,y:y+0.3,w:0.42,h:0.42,fontFace:F,fontSize:16,bold:true,color:BAD,align:"center",valign:"middle",margin:0});
        s.addText(c[0],{x:x+0.28,y:y+0.88,w:w-0.56,h:0.7,fontFace:F,fontSize:17,bold:true,color:INK,margin:0});
        s.addText(c[1],{x:x+0.28,y:y+1.66,w:w-0.56,h:h-1.85,fontFace:F,fontSize:13,color:MUTE,margin:0,valign:"top",lineSpacingMultiple:1.18});});
      s.addNotes(sl.title); return;
    }
    if(sl.type==="table4"){
      head(s,sl.no,sl.kick,sl.title,{ts:22,th:1.15,lead:sl.lead,ly:2.05});
      const rows=[sl.head,...sl.rows];
      const colW=[2.5,3.05,3.15,3.36];
      const tRows=rows.map((r,ri)=>r.map((c,ci)=>({text:c,options:{fontFace:F,fontSize:ri===0?11:12.5,bold:ri===0||ci===3,
        color:ri===0?MUTE:(ci===3?AMBD:(ci===0?INK:MUTE)),fill:{color:ri===0?SURF2:(ri%2?SURF:"0C1E33")},align:"left",valign:"middle",margin:[3,7,3,7]}})));
      s.addTable(tRows,{x:MX,y:2.95,w:CW,colW,border:{type:"solid",color:LINE,pt:1},rowH:0.6,autoPage:false});
      s.addNotes(sl.title); return;
    }
    if(sl.type==="tagcards"){
      head(s,sl.no,sl.kick,sl.title,{ts:26,lead:sl.lead,th:sl.lead?1.0:0.95});
      const y=sl.lead?2.95:2.05,h=sl.lead?2.15:3.0,g=0.34,w=(CW-2*g)/3;
      sl.cards.forEach((c,i)=>{const x=MX+i*(w+g);card(s,x,y,w,h,{border:i===1?AMBD:LINE});
        tagPill(s,x+0.28,y+0.26,c[0],TAGCOL[c[1]]);
        s.addText(c[2],{x:x+0.28,y:y+0.62,w:w-0.56,h:0.44,fontFace:F,fontSize:15.5,bold:true,color:INK,margin:0,valign:"middle"});
        s.addText(c[3],{x:x+0.28,y:y+1.08,w:w-0.56,h:h-1.24,fontFace:F,fontSize:12,color:MUTE,margin:0,valign:"top",lineSpacingMultiple:1.15});});
      if(sl.callout) calloutBox(s,5.4,sl.callout,1.3);
      s.addNotes(sl.title); return;
    }
    if(sl.type==="flow"){
      head(s,sl.no,sl.kick,sl.title,{ts:25,lead:sl.lead});
      const g=0.28,w=(CW-3*g)/4,y=2.85,h=2.05;
      sl.steps.forEach((st,i)=>{const x=MX+i*(w+g);card(s,x,y,w,h,{border:i===1?AMBD:LINE});
        s.addText(st[0],{x:x+0.24,y:y+0.22,w:1,h:0.34,fontFace:F,fontSize:13,bold:true,color:AMBD,margin:0});
        s.addText(st[1],{x:x+0.24,y:y+0.58,w:w-0.48,h:0.4,fontFace:F,fontSize:15.5,bold:true,color:INK,margin:0});
        s.addText(st[2],{x:x+0.24,y:y+1.0,w:w-0.48,h:h-1.15,fontFace:F,fontSize:12,color:MUTE,margin:0,valign:"top",lineSpacingMultiple:1.13});
        if(i<3) s.addText("→",{x:x+w-0.02,y,w:g+0.04,h,fontFace:F,fontSize:16,bold:true,color:FAINT,align:"center",valign:"middle",margin:0});});
      calloutBox(s,5.4,sl.callout,1.3); s.addNotes(sl.title); return;
    }
    if(sl.type==="statscallout"){
      head(s,sl.no,sl.kick,sl.title,{ts:26});
      const g=0.02,w=(CW-2*g)/3,y=2.35,h=2.5;
      sl.stats.forEach((x0,i)=>{const x=MX+i*(w+g);card(s,x,y,w,h,{fill:SURF});
        const token=x0[1], vc=token==="good"?GOOD:(token==="amb"?AMBD:INK);
        s.addText(x0[0],{x:x+0.3,y:y+0.4,w:w-0.55,h:0.9,fontFace:F,fontSize:30,bold:true,color:vc,margin:0,valign:"middle",charSpacing:-0.5});
        s.addText(x0[2],{x:x+0.3,y:y+1.38,w:w-0.6,h:0.34,fontFace:F,fontSize:12,bold:true,color:sl.kAmber?AMBD:FAINT,margin:0,charSpacing:0.3});
        s.addText(x0[3],{x:x+0.3,y:y+1.72,w:w-0.6,h:0.66,fontFace:F,fontSize:12,color:MUTE,margin:0,valign:"top",lineSpacingMultiple:1.12});});
      calloutBox(s,5.35,sl.callout,1.35); s.addNotes(sl.title); return;
    }
    if(sl.type==="charts"){
      head(s,sl.no,sl.kick,sl.title,{ts:26});
      const cw=(CW-0.34)/2,cy=2.15,ch=3.55;
      const co={chartColors:[PES,BASE,OPT],lineSize:2.5,lineSmooth:false,showLegend:false,showTitle:false,
        valAxisMinVal:0,valAxisMaxVal:380,valAxisMajorUnit:100,valGridLine:{color:LINE,size:0.5},catGridLine:{style:"none"},
        catAxisLabelColor:FAINT,valAxisLabelColor:FAINT,catAxisLabelFontFace:F,valAxisLabelFontFace:F,
        catAxisLabelFontSize:10,valAxisLabelFontSize:10,catAxisLineColor:LINE,valAxisLineColor:LINE,
        valAxisLabelFormatCode:'#"k"',lineDataSymbol:"circle",lineDataSymbolSize:5,
        chartArea:{fill:{color:SURF}},plotArea:{fill:{color:SURF}}};
      const mk=(arr)=>arr.map(x=>({name:x.name,labels:CATS,values:x.values}));
      [[sl.c1,SERIES_SIN,MX],[sl.c2,SERIES_CON,MX+cw+0.34]].forEach(([tt,ser,x])=>{
        card(s,x,cy,cw,ch+0.62,{fill:SURF});
        s.addText(tt[0],{x:x+0.24,y:cy+0.16,w:cw-0.48,h:0.3,fontFace:F,fontSize:13,bold:true,color:INK,margin:0});
        s.addText(tt[1],{x:x+0.24,y:cy+0.46,w:cw-0.48,h:0.26,fontFace:F,fontSize:10.5,color:FAINT,margin:0});
        s.addChart(pres.ChartType.line,mk(ser),Object.assign({},co,{x:x+0.12,y:cy+0.78,w:cw-0.24,h:ch-0.35}));});
      const ly=6.5;let lx=MX;
      sl.legend.forEach((l,i)=>{const c=[PES,BASE,OPT][i];const t=l[0]+(l[1]?" "+l[1]:"");
        s.addShape(pres.ShapeType.roundRect,{x:lx,y:ly+0.03,w:0.16,h:0.16,rectRadius:0.03,fill:{color:c},line:{type:"none"}});
        const w=0.28+t.length*0.076;
        s.addText(t,{x:lx+0.24,y:ly-0.04,w,h:0.3,fontFace:F,fontSize:11.5,color:MUTE,margin:0,valign:"middle"});
        lx+=0.24+w+0.3;});
      s.addNotes(sl.title); return;
    }
    if(sl.type==="ticklist"){
      head(s,sl.no,sl.kick,sl.title,{ts:24});
      const y=2.4,h=0.98,g=0.16, risk=sl.risk;
      sl.items.forEach((it,i)=>{const yy=y+i*(h+g);card(s,MX,yy,CW,h,{fill:risk?"22110F":SURF,border:risk?"5A2B26":LINE});
        if(risk){s.addShape(pres.ShapeType.ellipse,{x:MX+0.28,y:yy+0.35,w:0.28,h:0.28,fill:{color:BAD},line:{type:"none"}});
          s.addText("!",{x:MX+0.28,y:yy+0.33,w:0.28,h:0.3,fontFace:F,fontSize:14,bold:true,color:"22110F",align:"center",valign:"middle",margin:0});}
        else{s.addShape(pres.ShapeType.roundRect,{x:MX+0.26,y:yy+0.28,w:0.42,h:0.42,rectRadius:0.09,fill:{color:AMB,transparency:80},line:{type:"none"}});
          s.addText(String(i+1),{x:MX+0.26,y:yy+0.28,w:0.42,h:0.42,fontFace:F,fontSize:15,bold:true,color:AMB,align:"center",valign:"middle",margin:0});}
        const tx=risk?0.82:0.9;
        s.addText([{text:it[0]+"  ",options:{bold:true,color:INK}},{text:it[1],options:{color:MUTE}}],
          {x:MX+tx,y:yy,w:CW-tx-0.3,h,fontFace:F,fontSize:13.5,margin:0,valign:"middle",lineSpacingMultiple:1.08});});
      s.addNotes(sl.title); return;
    }
    if(sl.type==="closing"){
      bg(s); glow(s,-2.4,4.8,6.4,82);
      s.addText([{text:sl.no+"  ",options:{color:FAINT,bold:true}},{text:sl.kick.toUpperCase(),options:{color:AMB,bold:true}}],
        {x:MX,y:0.6,w:CW,h:0.3,fontFace:F,fontSize:12.5,charSpacing:2,margin:0});
      s.addText(sl.title,{x:MX,y:0.98,w:11.6,h:0.9,fontFace:F,fontSize:29,bold:true,color:INK,margin:0,charSpacing:-0.4});
      s.addText(sl.lead,{x:MX,y:1.92,w:11.4,h:1.0,fontFace:F,fontSize:14,color:MUTE,margin:0,lineSpacingMultiple:1.2});
      const g=0.34,w=(CW-g)/2,y=3.2,h=2.25;
      sl.cards.forEach((c,i)=>{const x=MX+i*(w+g);card(s,x,y,w,h,{border:i===1?AMBD:LINE});
        tagPill(s,x+0.3,y+0.28,c[0],TAGCOL[c[1]]);
        s.addText(c[2],{x:x+0.3,y:y+0.64,w:w-0.6,h:0.44,fontFace:F,fontSize:17,bold:true,color:INK,margin:0});
        s.addText(c[3],{x:x+0.3,y:y+1.12,w:w-0.6,h:h-1.28,fontFace:F,fontSize:12.5,color:MUTE,margin:0,valign:"top",lineSpacingMultiple:1.16});});
      const cyy=5.68;
      s.addShape(pres.ShapeType.line,{x:MX,y:cyy,w:CW,h:0,line:{color:LINE,width:1}});
      const ct=sl.contact;
      s.addText([{text:ct[0][0]+" ",options:{bold:true,color:INK}},{text:ct[0][1],options:{color:MUTE}}],
        {x:MX,y:cyy+0.2,w:8.5,h:0.4,fontFace:F,fontSize:14,margin:0,valign:"middle"});
      s.addText([{text:ct[1][0],options:{bold:true,color:INK}},{text:" "+ct[1][1]+"   ·   "+ct[2][1],options:{color:MUTE}}],
        {x:MX,y:cyy+0.66,w:CW,h:0.4,fontFace:F,fontSize:13,margin:0,valign:"middle"});
      s.addShape(pres.ShapeType.roundRect,{x:W-MX-0.56,y:cyy+0.3,w:0.56,h:0.56,rectRadius:0.1,fill:{color:AMB},line:{type:"none"}});
      s.addText("MV",{x:W-MX-0.56,y:cyy+0.3,w:0.56,h:0.56,fontFace:F,fontSize:17,bold:true,color:"1A1205",align:"center",valign:"middle",margin:0});
      s.addNotes(sl.title); return;
    }
  });
  return pres.writeFile({fileName:OUT+"/"+v.file.pptx});
}

/* ===================== MAIN ===================== */
(async()=>{
  for(const v of variants){
    fs.writeFileSync(OUT+"/"+v.file.deckHtml, deckHTML(v));
    fs.writeFileSync(OUT+"/"+v.file.opHtml, opHTML(v));
    await buildPPTX(v);
    console.log("built", v.code, "->", v.file.pptx, "+", v.file.deckHtml, "+", v.file.opHtml);
  }
  console.log("ALL DONE");
})();
