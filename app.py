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
outline_b64 = base64.b64encode(outline_svg).decode("ascii")
logo_b64 = base64.b64encode((ASSETS / "Disrupt_scissor_cut_v2.gif").read_bytes()).decode("ascii")
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

st.markdown(
    """
<style>
/* One seamless, white presentation canvas, without a framed map card. */
.stApp, [data-testid="stAppViewContainer"] {background:#ffffff!important;}
[data-testid="stHeader"] {background:transparent!important;}
.block-container {max-width:1210px!important;padding-top:.08rem;padding-bottom:.4rem;}
h1 {letter-spacing:-.035em;margin-bottom:.05rem;}
p, .stCaption {margin-bottom:.1rem;}
/* Plain always-visible footer image; bypasses Streamlit's image-list loader. */
.partner-footer{display:flex;width:100%;align-items:center;justify-content:center;margin:.15rem auto 0;padding:0;}
.partner-footer img{display:block;width:100%;max-width:1200px;height:auto;max-height:190px;object-fit:contain;}
@media(max-height:800px) and (min-width:1000px){.partner-footer img{max-height:112px!important;}}
@media(max-width:720px){.partner-footer img{max-height:120px!important;}}
/* The countdown replaces the button in the same full-width slot. */
.randomise-countdown{display:flex;position:relative;justify-content:center;align-items:center;width:100%;height:98px;min-height:98px;overflow:hidden;font-variant-numeric:tabular-nums}
.randomise-countdown .countdown-second{position:absolute;opacity:0;display:block;white-space:nowrap;color:#183c46;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-weight:900;font-size:clamp(4.5rem,6.6vw,6rem);line-height:1;animation:count-second 1s linear forwards}
@keyframes count-second{0%{opacity:1;transform:scale(.84)}15%{opacity:1;transform:scale(1)}99.9%{opacity:1;transform:scale(1)}100%{opacity:0;transform:scale(1)}}
@media(max-height:800px) and (min-width:1000px){.randomise-countdown{height:88px;min-height:88px}.randomise-countdown .countdown-second{font-size:5rem}}
@media(max-width:720px){.randomise-countdown{height:82px;min-height:82px}.randomise-countdown .countdown-second{font-size:4.2rem}}
@media(prefers-reduced-motion:reduce){.randomise-countdown .countdown-second{animation-name:count-second-static}}
@keyframes count-second-static{0%,99.9%{opacity:1;transform:none}100%{opacity:0;transform:none}}
/* Projector-friendly button: quiet visual design, bold oversized label. */
div.stButton {display:block;width:100%;}
div.stButton > button[kind="primary"] {
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    width:100%!important;
    max-width:none!important;
    min-width:0!important;
    min-height:98px!important;
    height:98px!important;
    padding:12px 24px!important;
    border-radius:16px!important;
    border:2px solid #183c46!important;
    background:#183c46!important;
    color:#ffffff!important;
    font-weight:800!important;
    font-size:clamp(3rem,4.8vw,4rem)!important;
    line-height:1.05!important;
    letter-spacing:0!important;
    box-shadow:none!important;
    text-shadow:none!important;
    transition:background-color .16s ease!important;
}
/* Streamlit renders button labels in nested Markdown <p> tags.
   Set their size explicitly: styling only the button was leaving tiny text. */
div.stButton > button[kind="primary"] [data-testid="stMarkdownContainer"],
div.stButton > button[kind="primary"] [data-testid="stMarkdownContainer"] p,
div.stButton > button[kind="primary"] [data-testid="stMarkdownContainer"] span {
    font-size:clamp(3rem,4.8vw,4rem)!important;
    line-height:1.05!important;
    font-weight:800!important;
    color:#ffffff!important;
    margin:0!important;
    padding:0!important;
}
div.stButton > button[kind="primary"]:hover {
    background:#285564!important;
    border-color:#285564!important;
}
div.stButton > button[kind="primary"]:active {background:#102f39!important;}
div.stButton > button[kind="primary"]:focus-visible {outline:3px solid #6d9da8!important;outline-offset:3px;}
@media(max-height:800px) and (min-width:1000px){
   .stApp iframe {height:430px!important;}
  .block-container {padding-top:.1rem!important;}
  div.stButton > button[kind="primary"] {height:88px!important;min-height:88px!important;}
  div.stButton > button[kind="primary"],
  div.stButton > button[kind="primary"] [data-testid="stMarkdownContainer"],
  div.stButton > button[kind="primary"] [data-testid="stMarkdownContainer"] p,
  div.stButton > button[kind="primary"] [data-testid="stMarkdownContainer"] span {font-size:3.15rem!important;}
}
@media(max-width:720px){
  div.stButton > button[kind="primary"] {height:82px!important;min-height:82px!important;border-radius:14px!important;}
  div.stButton > button[kind="primary"],
  div.stButton > button[kind="primary"] [data-testid="stMarkdownContainer"],
  div.stButton > button[kind="primary"] [data-testid="stMarkdownContainer"] p,
  div.stButton > button[kind="primary"] [data-testid="stMarkdownContainer"] span {font-size:2.6rem!important;}
}
</style>
""",
    unsafe_allow_html=True,
)

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
.legend article.intervention{border-color:#d93c4a;background:#fff1f3}
.legend article.control{border-color:#88919b;background:#f2f4f6}
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
  <article id="cardIntervention" class="intervention" hidden><strong><i class="swatch" style="background:#ce142b"></i>Intervention</strong><span id="interventionName"></span></article>
  <article id="cardControl" class="control" hidden><strong><i class="swatch" style="background:#828b94"></i>Control</strong><span id="controlName"></span></article>
  <article><strong><i class="swatch" style="background:#156082"></i>Non-study area</strong><span id="labelNon"></span></article>
</div></div></div></div>
<script>
const cfg=APP_CONFIG;
const initialPurple="#a02b93",initialGreen="#4ea72e",nonStudyBlue="#156082";
const interventionRed="#ce142b",controlGrey="#828b94";
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
// Blue background guarantees no uncoloured gaps inside the province.
const blueBase=makePath(cfg.provincePath,'area-shade');
blueBase.setAttribute('fill',blendWithWhite(nonStudyBlue,cfg.areaOpacity));
blueBase.setAttribute('stroke','none');
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
  setFill(groups.non_study,nonStudyBlue);
  document.getElementById('swatchA').style.background=initialPurple;
  document.getElementById('swatchB').style.background=initialGreen;
  document.getElementById('labelA').textContent=cfg.counts.A+' sites';
  document.getElementById('labelB').textContent=cfg.counts.B+' sites';
  document.getElementById('labelNon').textContent=cfg.counts.non_study+' blue sites';
}
function showRoles(){
  document.getElementById('cardA').hidden=true;
  document.getElementById('cardB').hidden=true;
  document.getElementById('cardIntervention').hidden=false;
  document.getElementById('cardControl').hidden=false;
}
function flash(redArea){
  paint('A',redArea==='A'?interventionRed:controlGrey,redArea==='A');
  paint('B',redArea==='B'?interventionRed:controlGrey,redArea==='B');
  // Non-study dots and the blue provincial background never change.
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
    const red=(i%2===0)?cfg.winner:(cfg.winner==='A'?'B':'A');
    flash(red);
    if(i===steps-1){setTimeout(finish,settleMs);return}
    setTimeout(tick,rawDelays[i++]*scale);
  }
  tick();
}
</script></body></html>
"""
components.html(html.replace("APP_CONFIG", config), height=665, scrolling=False)

# One permanent session-level draw, with the primary CTA underneath the map.
# Omitting the button after the draw prevents repeat allocations without a reset.
if st.session_state.allocation is None:
    if st.button("Randomise", type="primary", use_container_width=True):
        winner = "A" if secrets.randbelow(2) == 0 else "B"
        st.session_state.allocation = {
            "intervention": winner,
            "control": "B" if winner == "A" else "A",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "site_counts": counts,
        }
        st.rerun()

else:
    # On the post-click rerun, count down 15 to 1 in the former button position.
    seconds = "".join(
        f'<span class="countdown-second" style="animation-delay:{15 - n}s">{n}</span>'
        for n in range(15, 0, -1)
    )
    st.markdown(
        f'<div class="randomise-countdown" role="timer" '
        f'aria-label="15-second countdown">{seconds}</div>',
        unsafe_allow_html=True,
    )

# The footer is present in both states and does not depend on Streamlit's
# ImageList component (which failed to import on the deployed website).
partner_png_b64 = base64.b64encode(
    (ASSETS / "disrupt_partners_compact.png").read_bytes()
).decode("ascii")
st.markdown(
    f'<div class="partner-footer"><img '
    f'src="data:image/png;base64,{partner_png_b64}" '
    f'alt="DiSrupT RR-TB partner organisations" /></div>',
    unsafe_allow_html=True,
)

st.caption(
    "Visual demonstration only: this is not an audited or persistent clinical-trial allocation system."
)
