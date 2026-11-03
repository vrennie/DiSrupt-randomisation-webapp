"""DiSrupT geographic randomisation demonstration, not an allocation service."""
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="DiSrupT Randomisation", page_icon="🎯", layout="wide")
st.title("DiSrupT RR-TB | Geographic randomisation")
st.caption("Demonstration only. Validate block boundaries and use an approved audited randomisation system for trial allocations.")

if "assignment" not in st.session_state:
    st.session_state.assignment = None

if st.button("🎯 RANDOMISE", type="primary", disabled=st.session_state.assignment is not None):
    winner = "A" if secrets.randbelow(2) == 0 else "B"
    st.session_state.assignment = {
        "intervention": winner,
        "control": "B" if winner == "A" else "A",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    st.rerun()

root = Path(__file__).resolve().parent
map_path = root / "assets" / "kzn_map.webp"
if map_path.exists():
    import base64
    background = "data:image/webp;base64," + base64.b64encode(map_path.read_bytes()).decode()
else:
    background = ""

# Block polygons based on the outlines in the supplied coloured reference.
# Coordinates use the 540 x 574 original image coordinate system.
A = "M 412,12 L 518,31 L 516,158 L 507,188 L 477,224 L 455,239 L 430,271 L 405,289 L 374,301 L 346,330 L 319,345 L 307,349 L 314,326 L 310,309 L 294,285 L 274,269 L 254,253 L 240,230 L 222,211 L 200,192 L 178,191 L 163,178 L 150,161 L 139,133 L 137,105 L 146,97 L 175,99 L 218,91 L 252,92 L 275,93 L 306,95 L 349,95 L 378,84 L 396,69 L 407,48 Z"
B = "M 103,172 L 124,179 L 142,200 L 160,217 L 173,233 L 176,259 L 186,280 L 200,277 L 222,267 L 240,260 L 259,265 L 272,285 L 279,309 L 274,340 L 263,356 L 249,374 L 231,383 L 229,410 L 236,433 L 258,454 L 258,478 L 225,510 L 207,529 L 174,553 L 169,559 L 143,550 L 116,538 L 90,533 L 68,522 L 42,503 L 19,484 L 15,459 L 15,426 L 21,398 L 23,391 L 46,392 L 60,370 L 69,346 L 69,334 L 43,297 L 16,283 L -4,270 L -4,245 L 9,232 L 33,221 L 59,214 L 76,204 L 95,182 Z"
cfg = json.dumps({
    "winner": st.session_state.assignment["intervention"] if st.session_state.assignment else None,
    "background": background, "A": A, "B": B
})
page = """
<!DOCTYPE html><html><head><meta charset='utf-8'>
<style>
*{box-sizing:border-box}body{margin:0;font-family:system-ui,sans-serif;color:#183144}
.panel{display:flex;align-items:center;justify-content:center;gap:24px;background:#fff;border:1px solid #e1e8ed;border-radius:18px;padding:15px}
svg{max-height:640px;width:min(70vw,540px);height:auto}
.block{fill:#db6a9e;fill-opacity:0;stroke:#0b3341;stroke-width:2;stroke-opacity:.7;transition:fill-opacity .12s}
.legend{min-width:175px}.legend article{padding:14px;margin:10px 0;border:1px solid #dae5e9;border-radius:12px}
.legend strong{display:block}.legend span{font-size:13px}.status{text-align:center;font-weight:700;color:#416374}
@media(max-width:640px){.panel{flex-direction:column;gap:0}svg{width:100%}.legend{display:flex;gap:8px}.legend article{flex:1}}
</style></head><body>
<div class='status' id='status'>Press RANDOMISE to select an allocation</div>
<div class='panel'>
<svg viewBox='0 0 540 574' aria-label='Map of two KwaZulu-Natal randomisation blocks'>
<rect width='540' height='574' fill='#f9f8f5'/>
<image id='mapimage' x='0' y='0' width='540' height='574' preserveAspectRatio='none'/>
<path class='block' id='blockA'/><path class='block' id='blockB'/>
</svg>
<div class='legend'><article><strong>Block A</strong><span id='labelA'>North-eastern · unassigned</span></article>
<article><strong>Block B</strong><span id='labelB'>South-western · unassigned</span></article></div>
</div>
<script>
const c=CONFIG, paths=[document.getElementById('blockA'),document.getElementById('blockB')];
paths[0].setAttribute('d',c.A);paths[1].setAttribute('d',c.B);
if(c.background){document.getElementById('mapimage').setAttribute('href',c.background)}
function highlight(i){paths.forEach((p,j)=>{p.style.fill='#dd589c';p.style.fillOpacity=i===j?'.7':'0'})}
function finish(){
 const target=c.winner==='A'?0:1;
 paths.forEach((p,i)=>{p.style.fill=i===target?'#17ad7e':'#5a9fca';p.style.fillOpacity='.58'});
 document.getElementById('labelA').textContent='North-eastern · '+(target===0?'INTERVENTION':'CONTROL');
 document.getElementById('labelB').textContent='South-western · '+(target===1?'INTERVENTION':'CONTROL');
 document.getElementById('status').textContent='Allocation complete';
}
if(c.winner){
 document.getElementById('status').textContent='Randomising…';
 const target=c.winner==='A'?0:1, count=23, first=(target-(count-1)%2+2)%2;
 let n=0;
 function tick(){
   highlight((first+n)%2);
   if(n===count-1){setTimeout(finish,750);return}
   let t=n/(count-1);n++;
   setTimeout(tick,65+Math.pow(t,2.35)*610);
 }
 setTimeout(tick,300);
}
</script></body></html>
"""
components.html(page.replace("CONFIG", cfg), height=745, scrolling=False)
if st.session_state.assignment:
    result = st.session_state.assignment
    st.success(f"Intervention: Block {result['intervention']} | Control: Block {result['control']}")
    st.download_button("Download session allocation (JSON)", json.dumps(result, indent=2),
                       file_name="disrupt-allocation.json", mime="application/json")
    if st.button("Reset demonstration"):
        del st.session_state.assignment
        st.rerun()
st.caption("Session state is temporary, not an auditable randomisation record. Do not use for clinical allocation.")
