"""DiSrupT geographic randomisation visualisation — demonstration only."""
import base64
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="DiSrupT | Randomisation", page_icon="🎯", layout="wide")
st.title("DiSrupT RR-TB | Geographic randomisation")
st.caption("Illustrative site grouping traced from the two supplied block maps.")

# Coordinates in the 540 x 574 pixel version of the supplied uncoloured map.
# Sites were located using the pink facility dots, then assigned to one of the
# two groups by their positions inside the highlighted block outlines.
# Verify site membership against authoritative site and geographic records.
SITES = {
    "north_east": [
        [512, 34], [262, 89], [279, 272], [296, 247], [413, 215],
        [338, 195], [190, 167], [321, 339], [368, 152], [303, 239],
        [417, 110], [163, 167], [345, 281], [399, 185], [152, 154],
        [331, 221], [337, 313], [415, 53], [310, 289], [255, 251],
        [313, 247], [380, 233], [394, 173], [160, 135], [328, 247],
        [389, 230]
    ],
    "south_west": [
        [141, 298], [137, 394], [165, 447], [124, 238], [79, 496],
        [232, 304], [251, 463], [74, 316], [175, 481], [157, 323],
        [119, 428], [141, 500], [151, 494], [266, 341], [133, 488]
    ]
}

if "assignment" not in st.session_state:
    st.session_state.assignment = None

st.markdown("""
<style>
.block-container {max-width: 1110px; padding-top: 2rem;}
.stApp {background-color: #f8fafb;}
div.stButton > button[kind="primary"] {
    background: #116c7b; color: white; border-radius: 12px;
    padding: .8rem 1.5rem; font-weight: 750;
}
</style>
""", unsafe_allow_html=True)

left, right = st.columns([1, 2], vertical_alignment="bottom")
with left:
    locked = st.session_state.assignment is not None
    if st.button("🎯 RANDOMISE", type="primary", use_container_width=True, disabled=locked):
        # The 50:50 result is drawn exactly once before the visual animation.
        selected = "north_east" if secrets.randbelow(2) == 0 else "south_west"
        st.session_state.assignment = {
            "intervention": selected,
            "control": "south_west" if selected == "north_east" else "north_east",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        st.rerun()
    if locked and st.button("Reset demonstration", use_container_width=True):
        st.session_state.assignment = None
        st.rerun()
    st.caption("50:50 random draw. Animation does not determine the outcome.")
with right:
    st.write("Site dots alternate between **green** and **blue**—fast at first, then slower—before intervention (green) and control (blue) are revealed.")

map_path = Path(__file__).parent / "assets" / "kzn_map.webp"
background = (
    "data:image/webp;base64," + base64.b64encode(map_path.read_bytes()).decode("ascii")
    if map_path.exists() else ""
)

config = json.dumps({
    "winner": st.session_state.assignment["intervention"] if st.session_state.assignment else None,
    "background": background,
    "sites": SITES,
})
page = r"""
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<style>
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,sans-serif;color:#183144}
.panel{border:1px solid #e0e8ed;border-radius:16px;background:white;padding:15px}
.status{text-align:center;font-size:15px;font-weight:700;margin-bottom:10px;min-height:24px}
.stage{display:flex;justify-content:center;align-items:center;gap:22px}
.map{position:relative;flex:0 1 540px;aspect-ratio:540/574;max-width:540px;width:100%}
.map img,.map svg{position:absolute;width:100%;height:100%;inset:0}
.map img{object-fit:fill}
.site{stroke:#fff;stroke-width:1.2;transition:fill .12s, r .12s}
.site.selected{r:5.7;stroke-width:1.6}
.legend{display:flex;flex-direction:column;gap:14px;min-width:180px}
.legend article{padding:14px;border-radius:12px;border:1px solid #e0e7ed;background:#f7fafb}
.legend strong{display:block;font-size:14px;margin-bottom:5px}
.legend span{font-size:13px}
.legend article.intervention{border-color:#22a579;background:#e9f8f3}
.legend article.control{border-color:#609fc2;background:#edf6fc}
@media(max-width:680px){.stage{flex-direction:column;gap:8px}.legend{flex-direction:row;min-width:0;width:100%}.legend article{flex:1;padding:10px}}
</style></head><body>
<div class="panel">
  <div class="status" id="status">Press RANDOMISE to start</div>
  <div class="stage">
    <div class="map" aria-label="KwaZulu-Natal map with initiation sites highlighted by allocation group">
      <img id="background" alt="KwaZulu-Natal district map with facility locations" />
      <svg viewBox="0 0 540 574" preserveAspectRatio="none" id="dots"></svg>
    </div>
    <div class="legend">
      <article id="cardNorth"><strong>Block A · North-east</strong><span id="labelNorth">Unassigned</span></article>
      <article id="cardSouth"><strong>Block B · South-west</strong><span id="labelSouth">Unassigned</span></article>
    </div>
  </div>
</div>
<script>
const cfg=APP_CONFIG;
const green="#16aa7c",blue="#589bc4";
const svg=document.getElementById("dots");
if(cfg.background){document.getElementById("background").src=cfg.background;}
const makeSite=(p,group)=>{
  const dot=document.createElementNS("http://www.w3.org/2000/svg","circle");
  dot.setAttribute("cx",p[0]);dot.setAttribute("cy",p[1]);
  dot.setAttribute("r",4.6);dot.setAttribute("class","site");
  dot.dataset.group=group;svg.appendChild(dot);return dot;
};
const north=cfg.sites.north_east.map(p=>makeSite(p,"north"));
const south=cfg.sites.south_west.map(p=>makeSite(p,"south"));
function colour(northGreen,chosen){
  for(const c of north){c.setAttribute("fill",northGreen?green:blue);c.setAttribute("class","site"+(chosen==="north"?" selected":""));}
  for(const c of south){c.setAttribute("fill",northGreen?blue:green);c.setAttribute("class","site"+(chosen==="south"?" selected":""));}
}
function finish(){
  const northWins=cfg.winner==="north_east";
  colour(northWins,northWins?"north":"south");
  const ncard=document.getElementById("cardNorth"),scard=document.getElementById("cardSouth");
  ncard.classList.add(northWins?"intervention":"control");
  scard.classList.add(northWins?"control":"intervention");
  document.getElementById("labelNorth").textContent=(northWins?"INTERVENTION":"CONTROL")+" · "+north.length+" sites";
  document.getElementById("labelSouth").textContent=(northWins?"CONTROL":"INTERVENTION")+" · "+south.length+" sites";
  document.getElementById("status").textContent="Allocation complete";
}
colour(true,null); // No pink highlighting at any stage
if(cfg.winner){
  document.getElementById("status").textContent="Randomising…";
  const northWins=cfg.winner==="north_east";
  const steps=23;let i=0;
  // Odd number of steps ensures final highlighted group matches the draw.
  const firstGreen=northWins;
  function tick(){
    const greenOnNorth=(i%2===0)?firstGreen:!firstGreen;
    colour(greenOnNorth,greenOnNorth?"north":"south");
    if(i===steps-1){setTimeout(finish,700);return;}
    const progress=i/(steps-1);
    const delay=65+620*Math.pow(progress,2.25);
    i++;
    setTimeout(tick,delay);
  }
  setTimeout(tick,280);
}
</script></body></html>
"""
components.html(page.replace("APP_CONFIG", config), height=730, scrolling=False)

if st.session_state.assignment:
    record = st.session_state.assignment
    names = {"north_east": "Block A — North-east", "south_west": "Block B — South-west"}
    st.success(
        f"Intervention: {names[record['intervention']]}  |  Control: {names[record['control']]}"
    )
    st.download_button(
        "Download session allocation (JSON)", data=json.dumps(record, indent=2),
        file_name="disrupt-allocation.json", mime="application/json",
    )
st.caption("Visual prototype only: image-derived site groupings require validation, and allocations are not kept in a durable audit log.")
