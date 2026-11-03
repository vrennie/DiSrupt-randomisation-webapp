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

## Presentation-friendly interface and randomisation

- A **white, borderless page** intended for **16:9 projector screens** (including a compact 720p layout), with large area labels and the user-supplied **animated DiSrupT RR-TB GIF logo** above the legend at the top right.
- A **full-width, clean dark-teal rectangular Randomise button** with rounded corners and an oversized, projector-friendly label (including the nested Streamlit text element). It appears directly below the map and legend.
- The initial map shows **Study area A purple**, **Study area B green**, and the **non-study area blue**.
- Clicking Randomise makes a single secure 50:50 draw (`secrets.randbelow(2)`) before the 15-second visual animation. The Randomise button disappears immediately and is replaced by a large **15, 14, 13, …, 1** countdown in the exact same space. It starts with the post-click render and runs throughout the 15-second red/grey pinball reveal; the permanent partner footer remains below.
- The legend switches from study-area labels to **Intervention (red)** and **Control (grey)** during the animation and shows the winning study-area labels at the end. The non-study area and its **11 blue sites** remain unchanged throughout.
- The finish triggers a **slower 2.7–3.9 second burst of large 🎉 party emojis**, launched from the **bottom centre of the entire browser viewport** and spreading upward and outward (not clipped to the map frame). Reduced-motion preferences are respected. In Streamlit, the map iframe uses same-origin parent document access for this browser-level visual effect, with a local iframe fallback if access is unavailable.
- A permanent **two-row footer showing all ten partner logos** is displayed before, during and after randomisation. It sits beneath the Randomise button initially and remains on screen when the button disappears after the draw. The footer is a plain embedded HTML image, not Streamlit's image-list component, to avoid the observed `ImageList` module-loading error. On shorter projector screens the map is scaled down consistently so the footer remains visible.
- Reset, JSON download, the raw site data table, the animation status heading and the map footnote are not shown. Repeat draws in the same session are prevented.

## Source files

- `app.py` — the Streamlit application, projector-friendly UI, 15-second animation and session draw
- `assets/sites.csv` — image-positioned site data and verified/edited group membership
- `assets/Disrupt_scissor_cut_v2.gif` — animated logo (18-frame GIF) shown above the legend
- `assets/disrupt_partners_compact.png` — ten logos from the supplied partner montage, arranged for an accessible footer
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
