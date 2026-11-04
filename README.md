# DiSrupT RR-TB geographic randomisation — site-area visualisation

Streamlit visual demonstration of a **50:50 randomisation** between two geographic study areas in KwaZulu-Natal. The province outline, illustrated regions and 57 initiation-site positions are retained from the supplied source images.

## Site groups

| Group | Sites |
| --- | ---: |
| Study area A | 24 |
| Study area B | 22 |
| Non-study area | 11 |

The study area boundaries and site classifications are **illustrative, not official administrative or approved trial boundaries**. The grey non-study corridor is constant.

## Presentation and randomisation sequence

- **Before clicking Randomise:** Show **two complete alternative maps**, side by side, with a large **OR** between them. The left map represents **Area A = Intervention / Area B = Control**; the right shows **Area A = Control / Area B = Intervention**. A shared legend below displays **Intervention purple (`#7C4F96`)**, **Control green (`#4EA72E`)** and **Non-study grey (`#969FA8`)**.
- **After clicking Randomise:** The alternatives are replaced by **one map**, which remains visible as Areas A and B alternate purple and green for a **10-second** pinball-style reveal, gradually slowing and finishing on the backend-selected result. The map is rendered as a normal in-flow SVG with explicit intrinsic dimensions, not absolutely positioned layers, so it cannot collapse to zero size. The component frame is taller on 1080p and compact on 720p to avoid clipping.
- The former Randomise button disappears; in its place a **single large countdown** displays **10 → 9 → ... → 1** and then clears. Countdown and map reveal both run for approximately ten seconds.
- A secure backend draw selects the intervention area with **`secrets.randbelow(2)`** (equal probabilities for A and B). The animation merely reveals that selection.
- The animated DiSrupT RR-TB logo and the centred, ten-logo partner footer remain, along with the upward 🎉 celebration at the result.
- One draw per Streamlit session; no reset, raw site-data table, or allocation download in the presentation interface. The page uses a white, borderless, projector-oriented design.

## Project files

- `app.py` — Streamlit app and animated presentation
- `assets/sites.csv` — initiation-site coordinates and area classifications
- `assets/province_outline.svg` — province outline
- `assets/area_envelopes.json` — province-clipped study-area polygons
- `assets/Disrupt_scissor_cut_v2.gif` — animated project logo
- `assets/disrupt_partners_compact.png` — partner logo montage
- `scripts/generate_areas.py` — polygon generation for the visual regions

Run locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Important limitations

This is a **visual prototype, not an audited clinical trial randomisation service**. The site positions and region polygons were digitised from supplied images and require validation against authoritative study materials. Session state is not a durable allocation record, and the preselected result is accessible to a user inspecting source code. A real clinical trial requires a protocol-approved, concealed, persistent, independently auditable allocation system.
