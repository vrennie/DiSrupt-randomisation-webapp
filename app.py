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
.block-container {max-width:1120px;padding-top:2rem;}
h1 {letter-spacing:-.035em;}
div.stButton > button[kind="primary"] {background:#116f80;color:white;border:0;
    border-radius:12px;font-size:1.03rem;padding:.75rem 1.5rem;font-weight:750;}
</style>
""",
    unsafe_allow_html=True,
)

st.caption("DiSrupT RR-TB  /  GEOGRAPHIC AREA RANDOMISATION")
st.title("Randomisation")
st.write(
    "KwaZulu-Natal provincial outline with three **50%-opacity site-group areas**, "
    "extending beyond the marked initiation sites. There are no district boundaries."
)

col_action, col_info = st.columns([1, 2], vertical_alignment="center")
with col_action:
    locked = st.session_state.allocation is not None
    if st.button("🎯 RANDOMISE", type="primary", use_container_width=True, disabled=locked):
        # A single cryptographically secure 50:50 draw, before starting the animation.
        winner = "A" if secrets.randbelow(2) == 0 else "B"
        st.session_state.allocation = {
            "intervention": winner,
            "control": "B" if winner == "A" else "A",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "site_counts": counts,
        }
        st.rerun()
    if locked and st.button("Reset demonstration", use_container_width=True):
        st.session_state.allocation = None
        st.rerun()
with col_info:
    st.caption(
        "**Purple = Area A** and **green = Area B** initially; "
        "**blue = non-study** stays unchanged. The A/B areas and dots swap "
        "green and purple for ~15 seconds, finishing with **green = intervention** "
        "and **purple = control**."
    )

winner = st.session_state.allocation["intervention"] if st.session_state.allocation else None
config = json.dumps({
    "winner": winner,
    "sites": sites,
    "counts": counts,
    "outline": "data:image/svg+xml;base64," + outline_b64,
    "areaPaths": area_envelopes["paths"],
    "provincePath": province_path,
    "areaOpacity": area_envelopes["opacity"],
    "allocation": st.session_state.allocation,
})

html = r"""
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<style>
*{box-sizing:border-box}body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:transparent;color:#18313e}
.panel{padding:14px;border:1px solid #dfe8ed;border-radius:17px;background:#fff;}
.status{text-align:center;font-size:15px;font-weight:750;min-height:24px;margin-bottom:7px;}
.stage{display:flex;align-items:center;justify-content:center;gap:18px;}
.map{position:relative;aspect-ratio:918/1038;width: min(100%, 640px);flex:0 1 640px;}
.map img,.map svg{position:absolute;inset:0;width:100%;height:100%;}
.area-shade{fill-opacity:1;stroke-width:1.8;stroke-opacity:.56;stroke-linejoin:round;fill-rule:evenodd;transition:fill .13s linear,stroke .13s linear;pointer-events:none;}
.marker{stroke:#10232b;stroke-width:2.6;transition:fill .13s linear,r .13s linear,stroke .13s linear;cursor:help;}
.marker.pulse{r:15;stroke-width:2.9;}
.marker.outside{opacity:.93;stroke:#163843;}
.legend{width:198px;display:flex;flex-direction:column;gap:10px;}
.legend article{border:1px solid #e0e8ed;border-radius:12px;background:#fafcfd;padding:13px;}
.legend article.intervention{border-color:#2baf7d;background:#ecfaf4;}
.legend article.control{border-color:#73b3d8;background:#edf7fc;}
.legend article strong{display:block;font-size:13px;line-height:1.45;margin-bottom:6px;}
.legend article span{display:block;color:#516b7a;font-size:12px;}
.swatch{display:inline-block;vertical-align:middle;width:11px;height:11px;border-radius:50%;margin-right:7px;}
.foot{padding:6px 0 0 5px;font-size:12px;color:#6d7f88;}
.download{display:none;border:1px solid #b5c6ce;border-radius:8px;padding:9px 12px;color:#125b6d;font-size:12px;text-decoration:none;text-align:center;background:#f6fafc;}
.download.visible{display:block;}
@media(max-width:680px){.stage{flex-direction:column;gap:2px}.map{flex:auto;width:100%;max-width:600px}.legend{width:100%;flex-direction:row;flex-wrap:wrap;gap:6px}.legend article{flex:1;min-width:95px;padding:9px}.panel{padding:8px}}
</style></head><body>
<div class="panel"><div class="status" id="status">Study-area classification</div>
<div class="stage"><div class="map" aria-label="Province outline and colour-coded initiation sites">
<img id="outline" alt="KwaZulu-Natal provincial outline without internal district boundaries"/>
<svg id="sites" viewBox="0 0 918 1038" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Initiation sites in Area A, Area B and non-study area"></svg>
</div>
<div class="legend">
  <article id="cardA"><strong><i class="swatch" id="swatchA"></i>Study area A</strong><span id="labelA">Purple · awaiting draw</span></article>
  <article id="cardB"><strong><i class="swatch" id="swatchB"></i>Study area B</strong><span id="labelB">Green · awaiting draw</span></article>
  <article><strong><i class="swatch" style="background:#156082"></i>Non-study area</strong><span id="labelNon">Blue · unchanged</span></article>
  <a id="download" class="download" download="disrupt-allocation.json">Download allocation (JSON)</a>
</div></div></div>
<div class="foot">All space outside Areas A and B is blue non-study, with no uncoloured gaps. Illustrative boundaries only; hover over dots for IDs.</div>
<script>
const cfg=APP_CONFIG;
const purple="#a02b93",initialGreen="#4ea72e",nonStudyBlue="#156082";
const interventionGreen="#34a853",controlPurple="#a02b93";
const svg=document.getElementById('sites');
document.getElementById('outline').src=cfg.outline;
const groups={A:[],B:[],non_study:[]};
const shaded={};
function blendWithWhite(hex,opacity){
  // Visually identical to a 50%-opacity fill on the white map background,
  // but opaque so the blue base never tints A and B beneath their polygons.
  const parts=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
  return '#'+parts.map(v=>Math.round(255*(1-opacity)+v*opacity).toString(16).padStart(2,'0')).join('');
}
function makePath(d,cls){
  const p=document.createElementNS('http://www.w3.org/2000/svg','path');
  p.setAttribute('d',d);p.setAttribute('class',cls);svg.appendChild(p);return p;
}
// Guarantee there is never an uncoloured space inside the province.
// The blue non-study area is the full province minus the opaque A/B overlays.
const blueBase=makePath(cfg.provincePath,'area-shade');
blueBase.setAttribute('fill',blendWithWhite(nonStudyBlue,cfg.areaOpacity));
blueBase.setAttribute('stroke','none');
for(const area of ['A','B']){
  shaded[area]=makePath(cfg.areaPaths[area],'area-shade');
}
// Redraw the external boundary on top of all fills so it stays crisp.
const provinceOutline=makePath(cfg.provincePath,'province-border');
provinceOutline.setAttribute('fill','none');
provinceOutline.setAttribute('stroke','#183c46');
provinceOutline.setAttribute('stroke-width','3.5');
provinceOutline.setAttribute('stroke-linejoin','round');
provinceOutline.style.pointerEvents='none';
for(const site of cfg.sites){
  const c=document.createElementNS('http://www.w3.org/2000/svg','circle');
  c.setAttribute('cx',site.x); c.setAttribute('cy',site.y);
  c.setAttribute('r','13'); c.setAttribute('class','marker'+(site.area==='non_study'?' outside':''));
  const title=document.createElementNS('http://www.w3.org/2000/svg','title');
  title.textContent=site.id+' — '+(site.area==='non_study'?'Non-study':'Study area '+site.area);
  c.appendChild(title);svg.appendChild(c);groups[site.area].push(c);
}
const setFill=(list,colour,pulse=false)=>list.forEach(el=>{
  el.setAttribute('fill',colour);
  el.setAttribute('class','marker'+(pulse?' pulse':'')+(list===groups.non_study?' outside':''));
});
function paint(area,colour,pulse=false){
  if(area==='non_study'){
    // Blue provincial background remains unchanged during animation.
    setFill(groups.non_study,nonStudyBlue);
    return;
  }
  shaded[area].setAttribute('fill',blendWithWhite(colour,cfg.areaOpacity));
  shaded[area].setAttribute('stroke',colour);
  setFill(groups[area],colour,pulse);
}
function initial(){
  paint('A',purple); paint('B',initialGreen); paint('non_study',nonStudyBlue);
  document.getElementById('swatchA').style.background=purple;
  document.getElementById('swatchB').style.background=initialGreen;
  document.getElementById('labelA').textContent=cfg.counts.A+' purple sites';
  document.getElementById('labelB').textContent=cfg.counts.B+' green sites';
  document.getElementById('labelNon').textContent=cfg.counts.non_study+' blue sites (unchanged)';
}
function flash(greenArea){
  paint('A',greenArea==='A'?interventionGreen:controlPurple,greenArea==='A');
  paint('B',greenArea==='B'?interventionGreen:controlPurple,greenArea==='B');
  // Neither the non-study dots nor their blue area ever change colour.
  document.getElementById('swatchA').style.background=greenArea==='A'?interventionGreen:controlPurple;
  document.getElementById('swatchB').style.background=greenArea==='B'?interventionGreen:controlPurple;
}
function finish(){
  flash(cfg.winner);
  for(const area of ['A','B']){
    const intervention=area===cfg.winner;
    document.getElementById('card'+area).classList.add(intervention?'intervention':'control');
    document.getElementById('label'+area).textContent=cfg.counts[area]+' sites · '+(intervention?'INTERVENTION':'CONTROL');
  }
  document.getElementById('status').textContent='Allocation complete';
  const link=document.getElementById('download');
  link.href='data:application/json;charset=utf-8,'+encodeURIComponent(JSON.stringify(cfg.allocation,null,2));
  link.classList.add('visible');
}
initial();
if(cfg.winner){
  document.getElementById('status').textContent='Randomising… (~15 seconds)';
  const steps=23; // Odd number of flashes ensures the animation ends on the Python draw.
  const settleMs=500;
  const totalMs=15000;
  const rawDelays=Array.from({length:steps-1},(_,i)=>0.08+Math.pow(i/(steps-2),2.7));
  const scale=(totalMs-settleMs)/rawDelays.reduce((a,b)=>a+b,0);
  let i=0;
  // The draw was already made in Python; this deliberately non-random reveal lands on it.
  function tick(){
    const active=(i%2===0)?cfg.winner:(cfg.winner==='A'?'B':'A');
    flash(active);
    if(i===steps-1){setTimeout(finish,settleMs);return;}
    const delay=rawDelays[i]*scale;
    i++;
    setTimeout(tick,delay);
  }
  tick();
}
</script></body></html>
"""
components.html(html.replace("APP_CONFIG", config), height=810, scrolling=False)

# Display the final assignment and enable its download in the iframe AFTER
# the 15-second visual reveal, so the result isn't exposed under the animation.

with st.expander("Site positions and classification data"):
    st.write(
        f"**Study area A:** {counts['A']} sites · **Study area B:** {counts['B']} sites · "
        f"**Non-study:** {counts['non_study']} sites."
    )
    st.dataframe(sites, hide_index=True, use_container_width=True)
    st.download_button(
        "Download site classification (CSV)",
        data=(ASSETS / "sites.csv").read_bytes(),
        file_name="disrupt_site_classification.csv", mime="text/csv",
    )

st.caption(
    "Visual demonstration only. Site coordinates and categories were extracted from the "
    "user-supplied labelled map and should be verified. Allocations are temporary "
    "browser-session state, not an approved or durable clinical-trial randomisation record."
)
