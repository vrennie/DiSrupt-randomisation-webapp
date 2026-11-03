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
outline_b64 = base64.b64encode((ASSETS / "province_outline.svg").read_bytes()).decode("ascii")

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
    "The KwaZulu-Natal province outline, with **no district shading or internal district lines**. "
    "Sites are positioned and grouped from the colour-coded reference image."
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
        "Before the draw: **purple = Area A**, **green = Area B**, "
        "**dark blue = non-study**. During randomisation, only Area A and B dots "
        "alternate between intervention green and control light blue."
    )

winner = st.session_state.allocation["intervention"] if st.session_state.allocation else None
config = json.dumps({
    "winner": winner,
    "sites": sites,
    "counts": counts,
    "outline": "data:image/svg+xml;base64," + outline_b64,
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
.marker{stroke:#10232b;stroke-width:2.6;transition:fill .13s linear,r .13s linear,stroke .13s linear;cursor:help;}
.marker.pulse{r:16;stroke-width:3.1;}
.marker.outside{opacity:.93;stroke:#163843;}
.legend{width:198px;display:flex;flex-direction:column;gap:10px;}
.legend article{border:1px solid #e0e8ed;border-radius:12px;background:#fafcfd;padding:13px;}
.legend article.intervention{border-color:#2baf7d;background:#ecfaf4;}
.legend article.control{border-color:#73b3d8;background:#edf7fc;}
.legend article strong{display:block;font-size:13px;line-height:1.45;margin-bottom:6px;}
.legend article span{display:block;color:#516b7a;font-size:12px;}
.swatch{display:inline-block;vertical-align:middle;width:11px;height:11px;border-radius:50%;margin-right:7px;}
.foot{padding:6px 0 0 5px;font-size:12px;color:#6d7f88;}
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
  <article><strong><i class="swatch" style="background:#156082"></i>Non-study sites</strong><span id="labelNon">Dark blue · unchanged</span></article>
</div></div></div>
<div class="foot">Hover over a dot to see its site ID and classification. The image-derived positions can be reviewed in sites.csv.</div>
<script>
const cfg=APP_CONFIG;
const purple="#a02b93",initialGreen="#4ea72e",nonStudyBlue="#156082";
const interventionGreen="#21ac71",controlBlue="#66b3df";
const svg=document.getElementById('sites');
document.getElementById('outline').src=cfg.outline;
const groups={A:[],B:[],non_study:[]};
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
function initial(){
  setFill(groups.A,purple); setFill(groups.B,initialGreen); setFill(groups.non_study,nonStudyBlue);
  document.getElementById('swatchA').style.background=purple;
  document.getElementById('swatchB').style.background=initialGreen;
  document.getElementById('labelA').textContent=cfg.counts.A+' purple sites';
  document.getElementById('labelB').textContent=cfg.counts.B+' green sites';
  document.getElementById('labelNon').textContent=cfg.counts.non_study+' blue sites (unchanged)';
}
function flash(greenArea){
  setFill(groups.A,greenArea==='A'?interventionGreen:controlBlue,greenArea==='A');
  setFill(groups.B,greenArea==='B'?interventionGreen:controlBlue,greenArea==='B');
  setFill(groups.non_study,nonStudyBlue);
  document.getElementById('swatchA').style.background=greenArea==='A'?interventionGreen:controlBlue;
  document.getElementById('swatchB').style.background=greenArea==='B'?interventionGreen:controlBlue;
}
function finish(){
  flash(cfg.winner);
  for(const area of ['A','B']){
    const intervention=area===cfg.winner;
    document.getElementById('card'+area).classList.add(intervention?'intervention':'control');
    document.getElementById('label'+area).textContent=cfg.counts[area]+' sites · '+(intervention?'INTERVENTION':'CONTROL');
  }
  document.getElementById('status').textContent='Allocation complete';
}
initial();
if(cfg.winner){
  document.getElementById('status').textContent='Randomising…';
  const count=23;let i=0;
  // The draw has already been made in Python; the animation simply lands on it.
  function tick(){
    const active=(i%2===0)?cfg.winner:(cfg.winner==='A'?'B':'A');
    flash(active);
    if(i===count-1){setTimeout(finish,620);return;}
    const progress=i/(count-1);
    const delay=65+560*Math.pow(progress,2.2);
    i++;
    setTimeout(tick,delay);
  }
  setTimeout(tick,300);
}
</script></body></html>
"""
components.html(html.replace("APP_CONFIG", config), height=810, scrolling=False)

if st.session_state.allocation:
    result = st.session_state.allocation
    st.success(f"Intervention: Study area {result['intervention']} · Control: Study area {result['control']}")
    st.download_button(
        "Download session allocation (JSON)",
        data=json.dumps(result, indent=2),
        file_name="disrupt-allocation.json", mime="application/json",
    )

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