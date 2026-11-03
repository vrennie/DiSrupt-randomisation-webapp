# DiSrupT RR-TB geographic randomisation — site-area visualisation

Streamlit demonstration of a 50:50 allocation between two geographic study areas, displayed using a **province-only KwaZulu-Natal outline** (no district boundaries).

## Classification update

Based on the latest user instruction, the **four northernmost previously-blue sites** (`N01`–`N04`, now `B19`–`B22`) have been reclassified as **green study area B**. The source-image positions are unchanged.

| Group | Sites | Before randomisation |
| --- | ---: | --- |
| Study area A | 24 | Purple |
| Study area B | 22 | Green |
| Non-study area | 11 | Dark blue |

The external provincial outline and site classifications are unchanged. The **green area B reaches the western and southern border**, while **purple area A reaches the northern and eastern border**. The **blue non-study corridor** separates them from north to the coastal blue site cluster. There is no uncoloured space inside the province. All three shapes form a non-overlapping visual partition, with 50% appearance on a white map. The Streamlit app draws the full province blue first as a fallback, and then overlays the green and purple regions without colour contamination. These are **illustrative shapes, not official administrative or trial boundaries**.

## Streamlined interface and randomisation animation

- The initial map displays **Area A in purple**, **Area B in green**, and the **non-study corridor in blue**.
- A bold red rectangular **Randomise** button with rounded corners sits **below** the map. A single click selects A or B with a cryptographically secure 50:50 draw (`secrets.randbelow(2)`); it is hidden after the draw to prevent repeating allocations in the same session.
- The legend changes from the study-area labels to **Intervention (red)** and **Control (grey)** when the animation starts.
- **Only areas A and B**, including their shaded regions and site dots, alternate **red / grey**, initially quickly and then more slowly for approximately **15 seconds**. The non-study region and its **11 blue sites** remain unchanged.
- Once the animation stops, the legend displays which study area was assigned intervention or control, and a short shower of **🎉 party emojis** celebrates the result. The effect respects reduced-motion preferences.
- Removed redundant on-map status headings, reset controls, JSON allocation downloads, the site-classification data table, and the long explanatory map footer.

## Source files

- `app.py` — the Streamlit application, 15-second animation and session draw
- `assets/sites.csv` — image-positioned site data and verified/edited group membership
- `assets/province_outline.svg` — outer provincial outline only
- `assets/area_envelopes.json` — precomputed province-clipped purple/green partitions and central blue corridor
- `scripts/generate_areas.py` — reproducible generator for the boundary-reaching areas and blue corridor

To run the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

If you change the manual border control points in the generator, regenerate the shaded regions before committing:

```bash
pip install 'shapely>=2'
python scripts/generate_areas.py
```

Only Streamlit is needed to **run** the app; Shapely is only needed to **regenerate** the area-shape asset.

## Important limitations

This is a visual prototype, **not a production clinical trial randomisation service**. Site coordinates and group envelopes were digitised from supplied images and must be checked against authoritative study records. Session state is not a durable allocation ledger, and the animation provides no allocation concealment against a user inspecting the page. Approved trial use requires an auditable, persistent and protocol-approved allocation system with access controls and protection against repeat draws.
