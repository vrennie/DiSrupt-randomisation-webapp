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
import streamlit.components.v1 as components

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
 .st-key-map_visual iframe{height:418px!important}
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
body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:transparent;color:#18313e}
/* No card: the entire Streamlit page is the white canvas. */
.panel{position:relative;padding:0;border:0;border-radius:0;background:transparent;overflow:visible}
.stage{display:flex;align-items:center;justify-content:center;gap:30px}
.map{position:relative;aspect-ratio:918/1038;width:min(100%,570px);flex:0 1 570px}
.map img,.map svg{position:absolute;inset:0;width:100%;height:100%}
.area-shade{fill-opacity:1;stroke-width:1.8;stroke-opacity:.56;stroke-linejoin:round;fill-rule:evenodd;transition:fill .13s linear,stroke .13s linear;pointer-events:none}
.marker{stroke:#10232b;stroke-width:2.6;transition:fill .13s linear,r .13s linear,stroke .13s linear;cursor:help}
.marker.pulse{r:15;stroke-width:2.9}
.marker.outside{opacity:.93;stroke:#163843}
.sidebar{width:340px;flex:0 0 340px;display:flex;flex-direction:column;align-items:center;gap:10px}
.brand-logo{width:232px;max-height:188px;object-fit:contain;display:block;margin:0 auto 8px;mix-blend-mode:multiply}
.legend{width:100%;display:flex;flex-direction:column;gap:12px}
.legend article{border:1px solid #e0e8ed;border-radius:15px;background:#fafcfd;padding:16px 18px}
.legend article.intervention{border-color:#ae90bf;background:#f5eff8}
.legend article.control{border-color:#a4a7d2;background:#f1f2fa}
.legend article strong{display:block;font-size:20px;line-height:1.3;margin-bottom:6px}
.legend article span{display:block;color:#516b7a;font-size:17px;line-height:1.35}
.legend article span:empty{display:none}
.swatch{display:inline-block;vertical-align:middle;width:18px;height:18px;border-radius:50%;margin-right:10px}
[hidden]{display:none !important}

@media(max-width:980px){
 .stage{gap:12px}
 .map{width:min(100%,485px);flex:0 1 485px}
 .sidebar{width:265px;flex-basis:265px}
 .brand-logo{width:175px;max-height:146px}
 .legend article{padding:14px}
 .legend article strong{font-size:17px}
 .legend article span{font-size:14px}
}
@media(max-height:530px) and (min-width:760px){
 .stage{gap:23px}
 .map{width:min(100%,425px);flex:0 1 425px}
 .sidebar{width:300px;flex-basis:300px;gap:6px}
 .brand-logo{width:162px;max-height:128px;margin:0 auto 3px}
 .legend{gap:7px}
 .legend article{padding:10px 13px;border-radius:12px}
 .legend article strong{font-size:18px;margin-bottom:4px}
 .legend article span{font-size:15px}
}
@media(max-width:740px){
 .stage{flex-direction:column;gap:10px}
 .map{flex:auto;width:100%;max-width:315px}
 .sidebar{width:100%;flex:initial;gap:6px}
 .brand-logo{width:112px;max-height:91px;margin:0 auto 2px}
 .legend{width:100%;flex-direction:row;flex-wrap:wrap;gap:8px}
 .legend article{flex:1;min-width:145px;padding:10px}
 .legend article strong{font-size:16px}
 .legend article span{font-size:13px}
 .panel{padding:0}
}

@media(max-height:530px) and (min-width:760px){
 .map{width:min(100%,365px);flex:0 1 365px}
 .sidebar{width:270px;flex-basis:270px}
 .brand-logo{width:150px;max-height:113px}
}
</style></head><body>
<div class="panel">
<div class="stage"><div class="map" aria-label="Province outline and colour-coded initiation sites">
<img id="outline" alt="KwaZulu-Natal provincial outline without internal district boundaries"/>
<svg id="sites" viewBox="0 0 918 1038" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Initiation sites in Area A, Area B and non-study area"></svg>
</div>
<div class="sidebar">
  <img id="brand" class="brand-logo" alt="Animated DiSrupT RR-TB logo" />
  <div class="legend">
  <article id="cardA"><strong><i class="swatch" id="swatchA"></i>Study area A</strong><span id="labelA"></span></article>
  <article id="cardB"><strong><i class="swatch" id="swatchB"></i>Study area B</strong><span id="labelB"></span></article>
  <article id="cardIntervention" class="intervention" hidden><strong><i class="swatch" style="background:#7c4f96"></i>Intervention</strong><span id="interventionName"></span></article>
  <article id="cardControl" class="control" hidden><strong><i class="swatch" style="background:#6266ab"></i>Control</strong><span id="controlName"></span></article>
  <article><strong><i class="swatch" style="background:#e4313e"></i>Non-study area</strong><span id="labelNon"></span></article>
</div></div></div></div>
<script>
const cfg=APP_CONFIG;
const initialPurple="#a02b93",initialGreen="#4ea72e",nonStudyRed="#e4313e";
const interventionPurple="#7c4f96",controlBlue="#6266ab";
// Restore large native button styling even if a separate CSS widget is delayed.
try {
 const parentDoc=window.parent.document;
 if(parentDoc && parentDoc.head && !parentDoc.getElementById('disrupt-page-style')){
   const sheet=parentDoc.createElement('style');
   sheet.id='disrupt-page-style';
   sheet.textContent="\n.stApp,[data-testid=\"stAppViewContainer\"]{background:#fff!important}\n[data-testid=\"stHeader\"]{background:transparent!important}\n.block-container{max-width:1210px!important;padding-top:.1rem!important;padding-bottom:.4rem!important}\n.block-container [data-testid=\"stVerticalBlock\"]{gap:.35rem!important}\n.st-key-randomise button,[data-testid=\"stButton\"]>button[kind=\"primary\"],div.stButton>button[kind=\"primary\"]{\n width:100%!important;max-width:none!important;min-width:0!important;\n display:flex!important;align-items:center!important;justify-content:center!important;\n height:94px!important;min-height:94px!important;padding:10px 24px!important;\n border:2px solid #183c46!important;border-radius:16px!important;\n color:#fff!important;background:#183c46!important;box-shadow:none!important;\n font-family:system-ui,-apple-system,Segoe UI,sans-serif!important;\n font-weight:850!important;font-size:clamp(3rem,5vw,4rem)!important;\n line-height:1.05!important;text-shadow:none!important\n}\n.st-key-randomise button p,[data-testid=\"stButton\"]>button[kind=\"primary\"] p,\ndiv.stButton>button[kind=\"primary\"] p,.st-key-randomise button span{\n font-size:clamp(3rem,5vw,4rem)!important;font-weight:850!important;\n color:#fff!important;line-height:1.05!important;margin:0!important\n}\n.st-key-randomise button:hover,[data-testid=\"stButton\"]>button[kind=\"primary\"]:hover{background:#285564!important}\n.st-key-map_visual iframe,.st-key-control_footer iframe{display:block;border:0!important}\n@media(max-height:800px) and (min-width:1000px){\n .st-key-map_visual iframe{height:418px!important}\n .st-key-randomise button,[data-testid=\"stButton\"]>button[kind=\"primary\"]{height:88px!important;min-height:88px!important}\n .st-key-randomise button p,[data-testid=\"stButton\"]>button[kind=\"primary\"] p{font-size:3.3rem!important}\n}\n@media(max-width:720px){\n .st-key-randomise button,[data-testid=\"stButton\"]>button[kind=\"primary\"]{height:80px!important;min-height:80px!important;border-radius:14px!important}\n .st-key-randomise button p,[data-testid=\"stButton\"]>button[kind=\"primary\"] p{font-size:2.75rem!important}\n}";
   parentDoc.head.appendChild(sheet);
 }
}catch(_error){ /* Streamlit style widget is the fallback. */ }
const svg=document.getElementById('sites');
document.getElementById('outline').src=cfg.outline;
document.getElementById('brand').src=cfg.logo;
const groups={A:[],B:[],non_study:[]};
const shaded={};
function blendWithWhite(hex,opacity){
  // Opaque equivalent of a semi-transparent fill on white. This prevents
  // the blue fallback beneath A and B from changing their perceived colours.
  const parts=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
  return '#'+parts.map(v=>Math.round(255*(1-opacity)+v*opacity).toString(16).padStart(2,'0')).join('');
}
function makePath(d,cls){
  const p=document.createElementNS('http://www.w3.org/2000/svg','path');
  p.setAttribute('d',d);p.setAttribute('class',cls);svg.appendChild(p);return p;
}
// The red non-study base guarantees no uncoloured gaps inside the province.
const nonStudyBase=makePath(cfg.provincePath,'area-shade');
nonStudyBase.setAttribute('fill',blendWithWhite(nonStudyRed,cfg.areaOpacity));
nonStudyBase.setAttribute('stroke','none');
for(const area of ['A','B']) shaded[area]=makePath(cfg.areaPaths[area],'area-shade');
const border=makePath(cfg.provincePath,'province-border');
border.setAttribute('fill','none');border.setAttribute('stroke','#183c46');
border.setAttribute('stroke-width','3.5');border.setAttribute('stroke-linejoin','round');
border.style.pointerEvents='none';
for(const site of cfg.sites){
  const c=document.createElementNS('http://www.w3.org/2000/svg','circle');
  c.setAttribute('cx',site.x);c.setAttribute('cy',site.y);c.setAttribute('r','13');
  c.setAttribute('class','marker'+(site.area==='non_study'?' outside':''));
  const title=document.createElementNS('http://www.w3.org/2000/svg','title');
  title.textContent=site.id+' — '+(site.area==='non_study'?'Non-study':'Study area '+site.area);
  c.appendChild(title);svg.appendChild(c);groups[site.area].push(c);
}
const setFill=(list,colour,pulse=false)=>list.forEach(el=>{
  el.setAttribute('fill',colour);
  el.setAttribute('class','marker'+(pulse?' pulse':'')+(list===groups.non_study?' outside':''));
});
function paint(area,colour,pulse=false){
  shaded[area].setAttribute('fill',blendWithWhite(colour,cfg.areaOpacity));
  shaded[area].setAttribute('stroke',colour);
  setFill(groups[area],colour,pulse);
}
function initial(){
  paint('A',initialPurple);paint('B',initialGreen);
  setFill(groups.non_study,nonStudyRed);
  document.getElementById('swatchA').style.background=initialPurple;
  document.getElementById('swatchB').style.background=initialGreen;
  document.getElementById('labelA').textContent=cfg.counts.A+' sites';
  document.getElementById('labelB').textContent=cfg.counts.B+' sites';
  document.getElementById('labelNon').textContent=cfg.counts.non_study+' red sites';
}
function showRoles(){
  document.getElementById('cardA').hidden=true;
  document.getElementById('cardB').hidden=true;
  document.getElementById('cardIntervention').hidden=false;
  document.getElementById('cardControl').hidden=false;
}
function flash(interventionArea){
  paint('A',interventionArea==='A'?interventionPurple:controlBlue,interventionArea==='A');
  paint('B',interventionArea==='B'?interventionPurple:controlBlue,interventionArea==='B');
  // Non-study dots and the red provincial background never change.
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
function finish(){
  flash(cfg.winner);
  const loser=cfg.winner==='A'?'B':'A';
  document.getElementById('interventionName').textContent='Study area '+cfg.winner+' · '+cfg.counts[cfg.winner]+' sites';
  document.getElementById('controlName').textContent='Study area '+loser+' · '+cfg.counts[loser]+' sites';
  celebrate();
}
initial();
if(cfg.winner){
  showRoles();
  const steps=23,settleMs=500,totalMs=15000;
  const rawDelays=Array.from({length:steps-1},(_,i)=>0.08+Math.pow(i/(steps-2),2.7));
  const scale=(totalMs-settleMs)/rawDelays.reduce((a,b)=>a+b,0);
  let i=0;
  // Python performed the 50:50 draw already. This is a non-random visual reveal.
  function tick(){
    const interventionArea=(i%2===0)?cfg.winner:(cfg.winner==='A'?'B':'A');
    flash(interventionArea);
    if(i===steps-1){setTimeout(finish,settleMs);return}
    setTimeout(tick,rawDelays[i++]*scale);
  }
  tick();
}
</script></body></html>
"""
with st.container(key="map_visual"):
    components.html(html.replace("APP_CONFIG", config), height=650, scrolling=False)

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
# This prevents unstyled '151413...' and keeps the logos centered.
has_allocation = st.session_state.allocation is not None
countdown_markup = ""
if has_allocation:
    # One DOM element, whose text updates once a second. No stacked spans.
    countdown_markup = (
        '<div class="countdown" role="timer" aria-label="15 second countdown">'
        '<span id="countdown-value" class="count-number">15</span></div>'
    )

partner_png_b64 = asset_base64("disrupt_partners_compact.png")
footer_html = (
    """<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>
    *{box-sizing:border-box}
    html,body{margin:0;padding:0;background:#fff;overflow:hidden}
    .footer{display:flex;flex-direction:column;align-items:center;
            justify-content:flex-start;width:100%;height:100%;gap:2px;padding:0 8px}
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
      let previous = 15;
      const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      function frame(now) {
        const next = Math.max(0, Math.ceil((15000 - (now - startTime)) / 1000));
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
      }
      requestAnimationFrame(frame);
    })();
    </script></body></html>"""
)
with st.container(key="control_footer"):
    components.html(footer_html, height=235 if has_allocation else 145, scrolling=False)
