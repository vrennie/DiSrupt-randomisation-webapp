"""DiSrupT RR-TB site-level geographic randomisation visual demonstration.

Not a clinical-trial allocation service. Image-derived site classifications
must be approved and verified before any operational deployment.
"""

import base64
import csv
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="DiSrupT | Randomisation", page_icon="🎯", layout="wide")
ASSETS = Path(__file__).resolve().parent / "assets"

@st.cache_data(show_spinner=False)
def asset_base64(name: str) -> str:
    """Encode static image assets once and reuse them across script reruns."""
    return base64.b64encode((ASSETS / name).read_bytes()).decode("ascii")


def get_sites():
    with (ASSETS / "sites.csv").open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    expected = {"A", "B", "non_study"}
    if any(site["area"] not in expected for site in rows):
        st.error("Invalid study-area category in assets/sites.csv")
        st.stop()
    return [
        {
            "id": item["site_id"],
            "x": float(item["x"]),
            "y": float(item["y"]),
            "area": item["area"],
        }
        for item in rows
    ]


sites = get_sites()
counts = {area: sum(site["area"] == area for site in sites) for area in ("A", "B", "non_study")}
outline_svg = (ASSETS / "province_outline.svg").read_bytes()
outline_b64 = asset_base64("province_outline.svg")
logo_b64 = asset_base64("Disrupt_scissor_cut_v2.gif")
# The province boundary is used as an always-filled blue base. Thus any area
# not occupied by A or B is non-study, never a white/unclassified gap.
import xml.etree.ElementTree as ET
province_path = next(el.attrib["d"] for el in ET.fromstring(outline_svg).iter()
                     if el.tag.endswith("path") and "d" in el.attrib)
# These shaded, 50% opacity province-clipped partitions are generated
# with scripts/generate_areas.py. They illustrate the site groups, not
# official boundaries.
area_envelopes = json.loads((ASSETS / "area_envelopes.json").read_text(encoding="utf-8"))
if set(area_envelopes.get("paths", {})) != {"A", "B", "non_study"}:
    st.error("Missing shaded-area paths. Regenerate assets/area_envelopes.json.")
    st.stop()

if "allocation" not in st.session_state:
    st.session_state.allocation = None

st.html("""<style>

.stApp,[data-testid="stAppViewContainer"]{background:#fff!important}
[data-testid="stHeader"]{background:transparent!important}
.block-container{max-width:1210px!important;padding-top:.1rem!important;padding-bottom:.4rem!important}
.block-container [data-testid="stVerticalBlock"]{gap:.35rem!important}
.st-key-randomise button,[data-testid="stButton"]>button[kind="primary"],div.stButton>button[kind="primary"]{
 width:100%!important;max-width:none!important;min-width:0!important;
 display:flex!important;align-items:center!important;justify-content:center!important;
 height:94px!important;min-height:94px!important;padding:10px 24px!important;
 border:2px solid #183c46!important;border-radius:16px!important;
 color:#fff!important;background:#183c46!important;box-shadow:none!important;
 font-family:system-ui,-apple-system,Segoe UI,sans-serif!important;
 font-weight:850!important;font-size:clamp(3rem,5vw,4rem)!important;
 line-height:1.05!important;text-shadow:none!important
}
.st-key-randomise button p,[data-testid="stButton"]>button[kind="primary"] p,
div.stButton>button[kind="primary"] p,.st-key-randomise button span{
 font-size:clamp(3rem,5vw,4rem)!important;font-weight:850!important;
 color:#fff!important;line-height:1.05!important;margin:0!important
}
.st-key-randomise button:hover,[data-testid="stButton"]>button[kind="primary"]:hover{background:#285564!important}
.st-key-map_visual iframe,.st-key-control_footer iframe{display:block;border:0!important}
@media(max-height:800px) and (min-width:1000px){
 .st-key-randomise button,[data-testid="stButton"]>button[kind="primary"]{height:88px!important;min-height:88px!important}
 .st-key-randomise button p,[data-testid="stButton"]>button[kind="primary"] p{font-size:3.3rem!important}
}
@media(max-width:720px){
 .st-key-randomise button,[data-testid="stButton"]>button[kind="primary"]{height:80px!important;min-height:80px!important;border-radius:14px!important}
 .st-key-randomise button p,[data-testid="stButton"]>button[kind="primary"] p{font-size:2.75rem!important}
}
</style>""")

# The countdown replaces the static page heading.
winner = st.session_state.allocation["intervention"] if st.session_state.allocation else None
config = json.dumps({
    "winner": winner,
    "sites": sites,
    "counts": counts,
    "outline": "data:image/svg+xml;base64," + outline_b64,
    "logo": "data:image/gif;base64," + logo_b64,
    "areaPaths": area_envelopes["paths"],
    "provincePath": province_path,
    "areaOpacity": area_envelopes["opacity"],
})

html = r"""
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<style>
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff;color:#18313e;font-family:system-ui,-apple-system,Segoe UI,sans-serif}
.sheet{width:100%;padding:4px 6px 0;position:relative}
.choices{display:grid;grid-template-columns:minmax(0,1fr) 70px minmax(0,1fr);gap:12px;align-items:center}
.choice{min-width:0;display:flex;flex-direction:column;align-items:center;gap:7px}
.choice-label{font-weight:800;font-size:clamp(14px,1.55vw,20px);text-align:center;color:#183c46;min-height:25px}
.map-box{position:relative;width:100%;max-width:375px;display:block;flex-shrink:0}
/* SVG is in normal document flow: its own height gives the map a real box. */
.map-box svg{position:relative;display:block;width:100%;height:auto;aspect-ratio:918/1038;overflow:visible}
.or{text-align:center;font-size:clamp(26px,3vw,42px);font-weight:900;color:#76848e}
.bottom-row{display:flex;align-items:center;justify-content:center;gap:22px;margin-top:10px}
.legend{display:flex;gap:10px;align-items:stretch;justify-content:center;flex-wrap:wrap}
.legend-card{padding:11px 16px;border:1px solid #dce4e9;border-radius:13px;background:#fafcfd;min-width:174px}
.legend-card strong{font-size:17px;line-height:1.4;display:block;white-space:nowrap}
.legend-card span{display:block;font-size:14px;color:#546c78}
.swatch{display:inline-block;width:17px;height:17px;margin-right:8px;border-radius:50%;vertical-align:middle}
.brand{max-width:152px;max-height:114px;object-fit:contain;display:block;mix-blend-mode:multiply}
/* The single-map flex item needs an explicit basis: its SVG/image are absolute
   and otherwise contribute no intrinsic width, collapsing the map to zero. */
.result-grid{display:grid;grid-template-columns:minmax(0,540px) 320px;align-items:start;justify-content:center;gap:34px;width:100%}
.result-grid .choice{width:100%;min-width:0;display:block}
.result-grid .map-box{width:100%;max-width:540px}
.sidebar{width:320px;flex:0 0 320px;display:flex;flex-direction:column;gap:14px;align-items:center}
.sidebar .brand{max-width:224px;max-height:172px}
.sidebar .legend{display:flex;flex-direction:column;gap:13px;width:100%}
.sidebar .legend-card{padding:15px 18px;min-width:0;width:100%}
.sidebar .legend-card strong{font-size:21px}
.sidebar .legend-card span{font-size:17px}
.area-shade{fill-opacity:1;stroke-width:1.8;stroke-opacity:.56;stroke-linejoin:round;fill-rule:evenodd;transition:fill .14s linear,stroke .14s linear;pointer-events:none}
.marker{stroke:#10232b;stroke-width:2.7;transition:fill .14s linear,r .14s linear,stroke .14s linear;cursor:help}
.marker.pulse{r:15;stroke-width:3}
.marker.outside{stroke:#34444c}
@media(max-height:800px) and (min-width:981px){
 .map-box{width:min(100%,305px)}
 .choice-label{font-size:15px;min-height:21px}
 .legend-card{padding:8px 12px;min-width:151px}
 .legend-card strong{font-size:15px}
 .legend-card span{font-size:12px}
 .brand{max-width:118px;max-height:82px}
 .bottom-row{margin-top:7px}
 .result-grid{grid-template-columns:minmax(0,368px) 290px;gap:18px}
 .result-grid .map-box{width:100%;max-width:368px}
 .sidebar{width:290px;flex-basis:290px;gap:8px}
 .sidebar .brand{max-width:150px;max-height:104px}
 .sidebar .legend-card{padding:11px 13px}
 .sidebar .legend-card strong{font-size:18px}
 .sidebar .legend-card span{font-size:14px}
}
@media(max-width:980px){
 .choices{grid-template-columns:minmax(0,1fr) 50px minmax(0,1fr);gap:6px}
 .map-box{width:min(100%,315px)}
 .choice-label{font-size:14px}
 .legend-card{padding:9px 11px;min-width:140px}
 .legend-card strong{font-size:14px}
 .legend-card span{font-size:12px}
 .brand{max-width:115px}
 .result-grid{gap:10px}
 .result-grid{grid-template-columns:minmax(0,425px) 235px;gap:12px}
 .result-grid .map-box{width:100%;max-width:425px}
 .sidebar{width:235px;flex-basis:235px}
 .sidebar .brand{max-width:145px}
 .sidebar .legend-card strong{font-size:17px}
 .sidebar .legend-card span{font-size:13px}
}
@media(max-width:680px){
 .choices{grid-template-columns:1fr;gap:6px}
 .or{font-size:23px}
 .bottom-row{flex-direction:column;gap:7px}
 .result-grid{grid-template-columns:minmax(0,1fr);gap:12px}
 .result-grid .choice{width:100%;max-width:425px;margin:0 auto}
 .result-grid .map-box{width:100%;max-width:425px}
 .sidebar{width:100%;flex:initial}
 .sidebar .legend{flex-direction:row;flex-wrap:wrap}
 .sidebar .legend-card{width:auto;min-width:145px;flex:1}
}
</style></head><body><main id="sheet" class="sheet"></main>
<script>
const cfg=APP_CONFIG;
const COLORS={intervention:'#7c4f96',control:'#4ea72e',nonstudy:'#969fa8'};
const ns='http://www.w3.org/2000/svg';
function makeEl(tag){return document.createElementNS(ns,tag)}
function legendCard(label,color,sub){
 const card=document.createElement('article');
 card.className='legend-card';
 const strong=document.createElement('strong');
 const dot=document.createElement('i');
 dot.className='swatch';dot.style.background=color;strong.appendChild(dot);
 strong.appendChild(document.createTextNode(label));
 card.appendChild(strong);
 if(sub){const line=document.createElement('span');line.textContent=sub;card.appendChild(line);}
 return card;
}
function newMap(id,title){
 const choice=document.createElement('section');choice.className='choice';
 if(title){const h=document.createElement('div');h.className='choice-label';h.textContent=title;choice.appendChild(h);}
 const box=document.createElement('div');box.className='map-box';
 // Use an in-flow SVG instead of absolute-positioned image/SVG layers.
 // Absolute-only contents collapsed this map after the Streamlit rerun.
 const svg=makeEl('svg');svg.setAttribute('id',id);svg.setAttribute('viewBox','0 0 918 1038');
 svg.setAttribute('width','918');svg.setAttribute('height','1038');
 svg.setAttribute('preserveAspectRatio','xMidYMid meet');
 svg.style.cssText='display:block;position:relative;width:100%;height:auto;aspect-ratio:918/1038';
 box.appendChild(svg);choice.appendChild(box);
 const dots={A:[],B:[],non_study:[]};
 const areas={};
 function path(d,kind){
   const p=makeEl('path');p.setAttribute('d',d);p.setAttribute('class',kind);
   svg.appendChild(p);return p;
 }
 function blend(color){
   return '#'+[1,3,5].map(j=>Math.round(255*(1-cfg.areaOpacity)+parseInt(color.slice(j,j+2),16)*cfg.areaOpacity).toString(16).padStart(2,'0')).join('');
 }
 const background=path(cfg.provincePath,'area-shade');background.setAttribute('fill',blend(COLORS.nonstudy));background.setAttribute('stroke','none');
 ['A','B'].forEach(area=>areas[area]=path(cfg.areaPaths[area],'area-shade'));
 const boundary=path(cfg.provincePath,'province-border');
 boundary.setAttribute('fill','none');boundary.setAttribute('stroke','#183c46');boundary.setAttribute('stroke-width','3.5');boundary.style.pointerEvents='none';
 cfg.sites.forEach(site=>{
   const dot=makeEl('circle');dot.setAttribute('cx',site.x);dot.setAttribute('cy',site.y);
   dot.setAttribute('r','13');dot.setAttribute('class','marker'+(site.area==='non_study'?' outside':''));
   const tip=makeEl('title');tip.textContent=site.id+' - '+site.area;
   dot.appendChild(tip);svg.appendChild(dot);dots[site.area].push(dot);
 });
 const paint=(area,color,pulse)=>{
   if(area!=='non_study'){
     areas[area].setAttribute('fill',blend(color));
     areas[area].setAttribute('stroke',color);
   }
   dots[area].forEach(dot=>{
     dot.setAttribute('fill',color);
     dot.setAttribute('class','marker'+(pulse?' pulse':'')+(area==='non_study'?' outside':''));
   });
 };
 const render=(interventionArea)=>{
   paint('A',interventionArea==='A'?COLORS.intervention:COLORS.control,interventionArea==='A');
   paint('B',interventionArea==='B'?COLORS.intervention:COLORS.control,interventionArea==='B');
   paint('non_study',COLORS.nonstudy,false);
 };
 return {choice,render};
}
function newLegend(){
 const legend=document.createElement('div');legend.className='legend';
 legend.appendChild(legendCard('Intervention',COLORS.intervention,'Purple'));
 legend.appendChild(legendCard('Control',COLORS.control,'Green'));
 legend.appendChild(legendCard('Non-study area',COLORS.nonstudy,cfg.counts.non_study+' grey sites'));
 return legend;
}
function newLogo(){
 const brand=document.createElement('img');brand.className='brand';brand.src=cfg.logo;brand.alt='Animated DiSrupT RR-TB logo';
 return brand;
}
function setup(){
 const sheet=document.getElementById('sheet');
 if(!cfg.winner){
   const choices=document.createElement('div');choices.className='choices';
   const left=newMap('mapA','Area A: Intervention | Area B: Control');
   const right=newMap('mapB','Area A: Control | Area B: Intervention');
   const or=document.createElement('div');or.className='or';or.textContent='OR';
   choices.appendChild(left.choice);choices.appendChild(or);choices.appendChild(right.choice);
   sheet.appendChild(choices);
   const below=document.createElement('div');below.className='bottom-row';
   below.appendChild(newLegend());below.appendChild(newLogo());sheet.appendChild(below);
   left.render('A');right.render('B');
   return null;
 }
 const result=document.createElement('div');result.className='result-grid';
 const single=newMap('mapSingle','');
 const side=document.createElement('aside');side.className='sidebar';
 side.appendChild(newLogo());side.appendChild(newLegend());
 result.appendChild(single.choice);result.appendChild(side);sheet.appendChild(result);
 return single;
}
function celebrate(){
  if(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)return;
  // Streamlit components.html runs inside an iframe. Render the particles in
  // the parent page's viewport instead of inside the iframe's clipped box.
  // Streamlit's srcdoc iframe allows scripts and same-origin access.
  let hostDoc=document,hostWindow=window;
  try{
    if(window.parent && window.parent!==window && window.parent.document.body){
      hostDoc=window.parent.document;hostWindow=window.parent;
    }
  }catch(_err){ /* Respect iframe isolation; use the local viewport as fallback. */ }
  const layer=hostDoc.createElement('div');
  layer.setAttribute('aria-hidden','true');
  layer.style.cssText='position:fixed;inset:0;overflow:hidden;pointer-events:none;z-index:2147483000';
  hostDoc.body.appendChild(layer);
  const width=hostWindow.innerWidth;
  const height=hostWindow.innerHeight;
  const particleCount=52;
  let remaining=particleCount;
  for(let i=0;i<particleCount;i++){
    const el=hostDoc.createElement('span');
    el.textContent=(i%7===0)?'🎊':'🎉';
    el.style.cssText='position:absolute;bottom:-76px;left:50%;opacity:0;white-space:nowrap;line-height:1;will-change:transform,opacity;';
    el.style.fontSize=(42+Math.random()*23)+'px';
    const launchOffset=(Math.random()-.5)*110;
    const lateral=(Math.random()-.5)*Math.min(width*.90,1100);
    const drift=-(height+150+Math.random()*100);
    const spin=(Math.random()-.5)*1100;
    layer.appendChild(el);
    const animation=el.animate([
      {transform:`translate3d(calc(-50% + ${launchOffset}px),20px,0) rotate(-18deg) scale(.65)`,opacity:0,offset:0},
      {transform:`translate3d(calc(-50% + ${launchOffset+lateral*.18}px),${drift*.18}px,0) rotate(${spin*.2}deg) scale(1)`,opacity:1,offset:.16},
      {transform:`translate3d(calc(-50% + ${launchOffset+lateral*.82}px),${drift*.80}px,0) rotate(${spin*.75}deg) scale(1.12)`,opacity:1,offset:.78},
      {transform:`translate3d(calc(-50% + ${launchOffset+lateral}px),${drift}px,0) rotate(${spin}deg) scale(1.22)`,opacity:0,offset:1},
    ],{
      duration:2700+Math.random()*1200,
      delay:Math.random()*650,
      easing:'cubic-bezier(.16,.65,.29,1)',
      fill:'forwards',
    });
    animation.finished.catch(()=>{}).finally(()=>{
      el.remove();
      remaining--;
      if(remaining===0)layer.remove();
    });
  }
}

const selected=setup();
if(selected){
 const steps=19,settleMs=400,totalMs=10000;
 const intervals=Array.from({length:steps-1},(_,i)=>0.09+Math.pow(i/(steps-2),2.55));
 const scale=(totalMs-settleMs)/intervals.reduce((x,y)=>x+y,0);
 let i=0;
 function complete(){selected.render(cfg.winner);celebrate();}
 function tick(){
   const area=(i%2===0)?cfg.winner:(cfg.winner==='A'?'B':'A');
   selected.render(area);
   if(i===steps-1){setTimeout(complete,settleMs);return;}
   setTimeout(tick,intervals[i++]*scale);
 }
 tick();
}
</script></body></html>
"""
with st.container(key="map_visual"):
    st.iframe(html.replace("APP_CONFIG", config), height="content")

# The cryptographically secure 50:50 allocation is drawn on the backend
# exactly once per Streamlit session, when the native button is clicked.
if st.session_state.allocation is None:
    if st.button("Randomise", key="randomise", type="primary", use_container_width=True):
        selected = "A" if secrets.randbelow(2) == 0 else "B"
        st.session_state.allocation = {
            "intervention": selected,
            "control": "B" if selected == "A" else "A",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "site_counts": counts,
        }
        st.rerun()

# The countdown and partner logos are rendered in one self-contained HTML
# iframe, rather than depending on separate Streamlit CSS/HTML elements.
# This prevents unstyled '10987...' and keeps the logos centered.
has_allocation = st.session_state.allocation is not None
countdown_markup = ""
if has_allocation:
    # One DOM element, whose text updates once a second. No stacked spans.
    countdown_markup = (
        '<div class="countdown" role="timer" aria-label="10 second countdown">'
        '<span id="countdown-value" class="count-number">10</span></div>'
    )

partner_png_b64 = asset_base64("disrupt_partners_compact.png")
footer_html = (
    """<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>
    *{box-sizing:border-box}
    html,body{margin:0;padding:0;background:#fff;overflow:hidden}
    .footer{display:flex;flex-direction:column;align-items:center;
            justify-content:flex-start;width:100%;height:auto;gap:2px;padding:0 8px}
    .countdown{position:relative;width:100%;height:90px;flex:0 0 90px;
               display:flex;justify-content:center;align-items:center;
               font-variant-numeric:tabular-nums}
    .count-number{display:block;position:relative;opacity:1;line-height:1;
                  color:#183c46;font-family:system-ui,-apple-system,Segoe UI,sans-serif;
                  font-size:clamp(70px,7vw,98px);font-weight:900;
                  font-variant-numeric:tabular-nums;min-width:2ch;text-align:center}
    .partners{display:block;margin:0 auto;max-width:100%;width:auto;
              height:auto;max-height:140px;object-fit:contain}

    </style></head><body><div class="footer">"""
    + countdown_markup
    + f'<img class="partners" src="data:image/png;base64,{partner_png_b64}" '
      'alt="DiSrupT RR-TB partner organisations"/>'
    + """</div>
    <script>
    (() => {
      // Drive one visible number from a monotonic clock. Previous numbers
      // vanish immediately because the same text node is updated in place.
      const value = document.getElementById('countdown-value');
      if (!value) return;
      const startTime = performance.now();
      let previous = 10;
      const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      function frame(now) {
        const next = Math.max(0, Math.ceil((10000 - (now - startTime)) / 1000));
        if (next !== previous) {
          previous = next;
          value.textContent = next ? String(next) : '';
          if (next && !reducedMotion && typeof value.animate === 'function') {
            value.animate([
              {opacity: 0.7, transform: 'scale(0.86)'},
              {opacity: 1, transform: 'scale(1)'}
            ], {duration: 210, easing: 'ease-out'});
          }
        }
        if (next > 0) requestAnimationFrame(frame);
        else {
          // Remove the 90px countdown row once the allocation is revealed.
          const timer = value.closest('.countdown');
          if (timer) timer.remove();
        }
      }
      requestAnimationFrame(frame);
    })();
    </script></body></html>"""
)
with st.container(key="control_footer"):
    st.iframe(footer_html, height="content")
