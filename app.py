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
.stApp {background:#f8fafb;}
.block-container {max-width:1120px;padding-top:1.3rem;}
h1 {letter-spacing:-.035em;}
/* Bright-red, rounded rectangular button reminiscent of STAPLES branding. */
div.stButton > button[kind="primary"] {
    background:#ce142b !important;
    color:#fff !important;
    border:0 !important;
    border-radius:12px !important;
    min-height:58px;
    font-size:1.14rem;
    font-weight:800;
    box-shadow:0 5px 14px rgba(160,0,30,.16);
}
div.stButton > button[kind="primary"]:hover {background:#a90c21 !important;}
div.stButton > button[kind="primary"]:focus-visible {outline:3px solid #f3a6b0;outline-offset:2px;}
</style>
""",
    unsafe_allow_html=True,
)

st.caption("DiSrupT RR-TB")
st.title("Randomisation")

winner = st.session_state.allocation["intervention"] if st.session_state.allocation else None
config = json.dumps({
    "winner": winner,
    "sites": sites,
    "counts": counts,
    "outline": "data:image/svg+xml;base64," + outline_b64,
    "areaPaths": area_envelopes["paths"],
    "provincePath": province_path,
    "areaOpacity": area_envelopes["opacity"],
})

html = r"""
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<style>
*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:transparent;color:#18313e}
.panel{position:relative;isolation:isolate;overflow:hidden;padding:14px;border:1px solid #dfe8ed;border-radius:17px;background:#fff}
.stage{display:flex;align-items:center;justify-content:center;gap:18px}
.map{position:relative;aspect-ratio:918/1038;width:min(100%,640px);flex:0 1 640px}
.map img,.map svg{position:absolute;inset:0;width:100%;height:100%}
.area-shade{fill-opacity:1;stroke-width:1.8;stroke-opacity:.56;stroke-linejoin:round;fill-rule:evenodd;transition:fill .13s linear,stroke .13s linear;pointer-events:none}
.marker{stroke:#10232b;stroke-width:2.6;transition:fill .13s linear,r .13s linear,stroke .13s linear;cursor:help}
.marker.pulse{r:15;stroke-width:2.9}
.marker.outside{opacity:.93;stroke:#163843}
.legend{width:198px;display:flex;flex-direction:column;gap:10px}
.legend article{border:1px solid #e0e8ed;border-radius:12px;background:#fafcfd;padding:13px}
.legend article.intervention{border-color:#d93c4a;background:#fff1f3}
.legend article.control{border-color:#88919b;background:#f2f4f6}
.legend article strong{display:block;font-size:13px;line-height:1.45;margin-bottom:6px}
.legend article span{display:block;color:#516b7a;font-size:12px}
.legend article span:empty{display:none}
.swatch{display:inline-block;vertical-align:middle;width:11px;height:11px;border-radius:50%;margin-right:7px}
[hidden]{display:none !important}
.celebration{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:5}
.celebration .party{position:absolute;top:-42px;display:block;opacity:0;font-size:24px;line-height:1;will-change:transform,opacity;animation:party-fall var(--time) cubic-bezier(.2,.65,.55,1) forwards;animation-delay:var(--delay)}
@keyframes party-fall{
  0%{transform:translate3d(0,-16px,0) rotate(-25deg) scale(.55);opacity:0}
  12%{opacity:1}
  78%{opacity:1}
  100%{transform:translate3d(var(--sway),810px,0) rotate(var(--spin)) scale(1.15);opacity:0}
}
@media(max-width:680px){
 .stage{flex-direction:column;gap:2px}
 .map{flex:auto;width:100%;max-width:500px}
 .legend{width:100%;flex-direction:row;flex-wrap:wrap;gap:6px}
 .legend article{flex:1;min-width:95px;padding:9px}
 .panel{padding:8px}
}
@media(prefers-reduced-motion:reduce){.party{animation:none!important;display:none!important}}
</style></head><body>
<div class="panel">
<div class="stage"><div class="map" aria-label="Province outline and colour-coded initiation sites">
<img id="outline" alt="KwaZulu-Natal provincial outline without internal district boundaries"/>
<svg id="sites" viewBox="0 0 918 1038" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Initiation sites in Area A, Area B and non-study area"></svg>
</div>
<div class="legend">
  <article id="cardA"><strong><i class="swatch" id="swatchA"></i>Study area A</strong><span id="labelA"></span></article>
  <article id="cardB"><strong><i class="swatch" id="swatchB"></i>Study area B</strong><span id="labelB"></span></article>
  <article id="cardIntervention" class="intervention" hidden><strong><i class="swatch" style="background:#ce142b"></i>Intervention</strong><span id="interventionName"></span></article>
  <article id="cardControl" class="control" hidden><strong><i class="swatch" style="background:#828b94"></i>Control</strong><span id="controlName"></span></article>
  <article><strong><i class="swatch" style="background:#156082"></i>Non-study area</strong><span id="labelNon"></span></article>
</div></div><div class="celebration" id="celebration" aria-hidden="true"></div></div>
<script>
const cfg=APP_CONFIG;
const initialPurple="#a02b93",initialGreen="#4ea72e",nonStudyBlue="#156082";
const interventionRed="#ce142b",controlGrey="#828b94";
const svg=document.getElementById('sites');
document.getElementById('outline').src=cfg.outline;
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
  if(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  const sky=document.getElementById('celebration');
  // Self-contained Messenger-style emoji rain, no external animation library.
  for(let i=0;i<38;i++){
    const span=document.createElement('span');span.className='party';
    span.textContent=i%6===0?'🎊':'🎉';
    span.style.left=(3+Math.random()*94)+'%';
    span.style.fontSize=(19+Math.random()*15)+'px';
    span.style.setProperty('--delay',Math.round(Math.random()*900)+'ms');
    span.style.setProperty('--time',Math.round(2100+Math.random()*1050)+'ms');
    span.style.setProperty('--sway',(Math.random()*140-70)+'px');
    span.style.setProperty('--spin',(Math.random()*1080-540)+'deg');
    sky.appendChild(span);
    span.addEventListener('animationend',()=>span.remove(),{once:true});
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
components.html(html.replace("APP_CONFIG", config), height=755, scrolling=False)

# One permanent session-level draw, with the primary CTA underneath the map.
# Omitting the button after the draw prevents repeat allocations without a reset.
if st.session_state.allocation is None:
    left, centre, right = st.columns([1, 0.75, 1])
    with centre:
        if st.button("Randomise", type="primary", use_container_width=True):
            winner = "A" if secrets.randbelow(2) == 0 else "B"
            st.session_state.allocation = {
                "intervention": winner,
                "control": "B" if winner == "A" else "A",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "site_counts": counts,
            }
            st.rerun()

st.caption(
    "Visual demonstration only: this is not an audited or persistent clinical-trial allocation system."
)
