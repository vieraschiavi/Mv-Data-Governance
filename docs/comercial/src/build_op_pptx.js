// One-pager editable como slide-resumen apaisada 16:9, por variante.
const P = require("pptxgenjs");
const { variants } = require("./content_i18n.js");
const OUT = __dirname;

const NAVY="0A1A2F",SURF="0E2138",SURF2="12283F",LINE="24405C",INK="EEF4FB",MUTE="A6BAD1",FAINT="7C93AE",
  AMB="F2B441",AMBD="E39A2E",GOOD="37C891",BAD="E0685C",F="Arial";
const W=13.33,H=7.5,MX=0.5,CW=W-2*MX;

// convierte <mark>/<b> a runs con formato
function rich(s, base={}){
  const runs=[]; let rest=s;
  const re=/(<mark>(.*?)<\/mark>|<b>(.*?)<\/b>)/;
  let m;
  while((m=rest.match(re))){
    const i=m.index;
    if(i>0) runs.push({text:rest.slice(0,i), options:{...base}});
    if(m[2]!==undefined) runs.push({text:m[2], options:{...base,bold:true,color:AMBD}});
    else runs.push({text:m[3], options:{...base,bold:true,color:INK}});
    rest=rest.slice(i+m[0].length);
  }
  if(rest) runs.push({text:rest, options:{...base}});
  return runs.map(r=>({...r, text:r.text.replace(/<[^>]+>/g,"")}));
}

function buildOP(v){
  const o=v.op;
  const pres=new P(); pres.layout="LAYOUT_WIDE"; pres.author="VieraSchiavi";
  const s=pres.addSlide(); s.background={color:NAVY};
  const card=(x,y,w,h,fill=SURF,border=LINE)=>s.addShape(pres.ShapeType.roundRect,{x,y,w,h,rectRadius:0.06,fill:{color:fill},line:{color:border,width:1}});

  // ---- masthead ----
  s.addShape(pres.ShapeType.roundRect,{x:MX,y:0.36,w:0.46,h:0.46,rectRadius:0.09,fill:{color:AMB},line:{type:"none"}});
  s.addText("MV",{x:MX,y:0.36,w:0.46,h:0.46,fontFace:F,fontSize:15,bold:true,color:"1A1205",align:"center",valign:"middle",margin:0});
  s.addText("MV Data Governance",{x:MX+0.6,y:0.34,w:7,h:0.3,fontFace:F,fontSize:16,bold:true,color:INK,margin:0,valign:"middle"});
  s.addText(o.tagline,{x:MX+0.6,y:0.64,w:7.6,h:0.24,fontFace:F,fontSize:9.5,color:FAINT,margin:0,valign:"middle"});
  // rt meta
  const rt=o.rt.map(r=> r[0]? [{text:r[0]+" ",options:{bold:true,color:MUTE}},{text:r[1],options:{color:FAINT}}] : [{text:r[1],options:{color:FAINT}}]);
  let ry=0.34;
  rt.forEach(line=>{ s.addText(line,{x:W-MX-4.2,y:ry,w:4.2,h:0.2,fontFace:F,fontSize:9.5,align:"right",margin:0,valign:"middle"}); ry+=0.205; });
  s.addShape(pres.ShapeType.line,{x:MX,y:1.15,w:CW,h:0,line:{color:AMB,width:1.5}});

  // ---- thesis ----
  s.addText(rich(o.thesis,{color:MUTE,fontFace:F,fontSize:13.5}),{x:MX,y:1.28,w:CW,h:0.72,fontFace:F,fontSize:13.5,margin:0,valign:"top",lineSpacingMultiple:1.12});

  // ---- KPIs ----
  const ky=2.12, kh=0.98, kg=0.02, kw=(CW-3*kg)/4;
  o.kpis.forEach((k,i)=>{const x=MX+i*(kw+kg); card(x,ky,kw,kh,SURF);
    s.addText(k[0].toUpperCase(),{x:x+0.16,y:ky+0.12,w:kw-0.32,h:0.2,fontFace:F,fontSize:8,bold:true,color:FAINT,margin:0,charSpacing:0.3});
    const vc=k[2]==="good"?GOOD:(k[2]==="amb"?AMBD:INK);
    s.addText(k[1],{x:x+0.16,y:ky+0.3,w:kw-0.32,h:0.36,fontFace:F,fontSize:17,bold:true,color:vc,margin:0,valign:"middle"});
    s.addText(k[3],{x:x+0.16,y:ky+0.68,w:kw-0.32,h:0.26,fontFace:F,fontSize:8.5,color:MUTE,margin:0,valign:"top",lineSpacingMultiple:1.0});});

  // ---- body columns ----
  const by=3.28, colGap=0.4, lw=6.25, rw=CW-lw-colGap, rx=MX+lw+colGap;
  const h3=(x,y,w,t)=>s.addText(t.toUpperCase(),{x,y,w,h:0.24,fontFace:F,fontSize:9.5,bold:true,color:AMBD,margin:0,charSpacing:0.6});

  // left: qué se vende
  h3(MX,by,lw,o.sellsH);
  let ly=by+0.3;
  o.sells.forEach(se=>{
    s.addShape(pres.ShapeType.roundRect,{x:MX+0.02,y:ly+0.06,w:0.09,h:0.09,rectRadius:0.02,fill:{color:AMBD},line:{type:"none"}});
    s.addText([{text:se[0].replace(/<[^>]+>/g,""),options:{bold:true,color:INK}},{text:se[1].replace(/<[^>]+>/g,""),options:{color:MUTE}}],
      {x:MX+0.22,y:ly-0.02,w:lw-0.22,h:0.42,fontFace:F,fontSize:10,margin:0,valign:"top",lineSpacingMultiple:1.05});
    ly+=0.44;
  });
  // left: seam
  const sy=ly+0.12; h3(MX,sy,lw,o.seamH);
  s.addText(rich(o.seam,{color:MUTE,fontFace:F,fontSize:10}),{x:MX,y:sy+0.28,w:lw,h:1.15,fontFace:F,fontSize:10,margin:0,valign:"top",lineSpacingMultiple:1.1});

  // right: tabla
  h3(rx,by,rw,o.tblH);
  const rows=[o.tblHead, ...o.tblRows.map(r=>r.slice(1))];
  const hlFlags=[false, ...o.tblRows.map(r=>r[0]==="hl")];
  const colW=[ (rw*0.30),(rw*0.165),(rw*0.175),(rw*0.185),(rw*0.175) ];
  const tRows=rows.map((r,ri)=>r.map((c,ci)=>({text:c,options:{
    fontFace:F,fontSize:ri===0?8:9.5,bold:ri===0,
    color:ri===0?MUTE:(ci===3?GOOD:(ci===0?INK:MUTE)),
    fill:{color: ri===0?SURF2 : (hlFlags[ri]? "241E10" : "0C1E33")},
    align: ci===0?"left":"right", valign:"middle", margin:[2,5,2,5]}})));
  s.addTable(tRows,{x:rx,y:by+0.3,w:rw,colW,border:{type:"solid",color:LINE,pt:0.75},rowH:0.28,autoPage:false});
  // right: callout modelo
  const my=by+0.3+0.28*5+0.16;
  card(rx,my,rw,0.86,"22180A","5A4620");
  s.addShape(pres.ShapeType.rect,{x:rx,y:my,w:0.05,h:0.86,fill:{color:AMB},line:{type:"none"}});
  s.addText(o.modelH.toUpperCase(),{x:rx+0.2,y:my+0.1,w:rw-0.35,h:0.2,fontFace:F,fontSize:8.5,bold:true,color:AMBD,margin:0,charSpacing:0.5});
  s.addText(rich(o.model,{color:INK,fontFace:F,fontSize:10}),{x:rx+0.2,y:my+0.3,w:rw-0.4,h:0.5,fontFace:F,fontSize:10,margin:0,valign:"top",lineSpacingMultiple:1.06});

  // ---- chips (izq abajo) ----
  const cy=6.05, chg=0.12, chw=(lw-2*chg)/3;
  o.chips.forEach((c,i)=>{const x=MX+i*(chw+chg); card(x,cy,chw,0.62,SURF);
    s.addText(c[0],{x:x+0.12,y:cy+0.08,w:chw-0.24,h:0.2,fontFace:F,fontSize:9,bold:true,color:INK,margin:0});
    s.addText(c[1],{x:x+0.12,y:cy+0.26,w:chw-0.24,h:0.24,fontFace:F,fontSize:12.5,bold:true,color:INK,margin:0});
    s.addText(c[2],{x:x+0.12,y:cy+0.48,w:chw-0.24,h:0.14,fontFace:F,fontSize:7.5,color:FAINT,margin:0});});

  // ---- pills (der abajo) ----
  const PC={g:GOOD,w:AMBD,b:BAD};
  let px=rx, py=6.05;
  o.pills.forEach(p=>{
    const w=Math.min(rw, 0.24+p[1].length*0.062);
    if(px+w>rx+rw+0.001){ px=rx; py+=0.34; }
    s.addShape(pres.ShapeType.roundRect,{x:px,y:py,w,h:0.26,rectRadius:0.13,fill:{color:PC[p[0]],transparency:82},line:{type:"none"}});
    s.addText(p[1],{x:px,y:py,w,h:0.26,fontFace:F,fontSize:8.5,bold:true,color:PC[p[0]],align:"center",valign:"middle",margin:0});
    px+=w+0.1;
  });

  // ---- CTA ----
  const ty=6.86;
  card(MX,ty,CW,0.5,SURF2,LINE);
  s.addText(o.ctaBig.replace(/<[^>]+>/g,""),{x:MX+0.22,y:ty+0.07,w:CW-4.6,h:0.22,fontFace:F,fontSize:11.5,bold:true,color:AMBD,margin:0,valign:"middle"});
  s.addText(o.ctaSm.replace(/<[^>]+>/g,""),{x:MX+0.22,y:ty+0.28,w:CW-4.6,h:0.18,fontFace:F,fontSize:8.5,color:MUTE,margin:0,valign:"middle"});
  s.addText([{text:o.who[0],options:{bold:true,color:INK}},{text:"  "+o.who[1]+"   ·   "+o.who[2],options:{color:MUTE}}],
    {x:W-MX-4.3,y:ty,w:4.3,h:0.5,fontFace:F,fontSize:9.5,align:"right",valign:"middle",margin:0});

  const name = v.file.op.replace("OnePager.pdf","OnePager-PPTX.pptx").replace("-PDF","");
  return pres.writeFile({fileName:OUT+"/"+name}).then(()=>name);
}

(async()=>{
  for(const v of variants){ const n=await buildOP(v); console.log("built", v.code, "->", n); }
  console.log("DONE");
})();
