# DiSrupT RR-TB geographic randomisation — site-area visualisation

Streamlit demonstration of a 50:50 allocation between two geographic study areas, displayed using a **province-only KwaZulu-Natal outline** (no district boundaries).

## Classification update

Based on the latest user instruction, the **four northernmost previously-blue sites** (`N01`–`N04`, now `B19`–`B22`) have been reclassified as **green study area B**. The source-image positions are unchanged.

| Group | Sites | Before randomisation |
| --- | ---: | --- |
| Study area A | 24 | Purple |
| Study area B | 22 | Green |
| Non-study area | 11 | Dark blue |

The external outline is unchanged. The A and B shapes are **illustrative image-derived site envelopes** extending beyond the sites and clipped to the province. **Every remaining space inside the province is automatically filled blue as non-study**, including all gaps between the two study envelopes. The app always draws blue across the complete province first, then overlays green/purple study regions, so there are no white holes. For consistent 50%-opacity appearance on a white map, the overlay colours are preblended with white, preventing the blue base from changing the study colours. These shapes are **not official administrative boundaries**.

## Randomisation animation

- Click **RANDOMISE** to draw 50:50 from A or B using `secrets.randbelow(2)`.
- **Only study areas A and B**, including their shaded envelopes and dots, alternate **green / purple**, rapidly at first and progressively more slowly.
- The non-study area and its 11 blue dots **never change colour**.
- The full animation, including a short final settle, takes approximately **15 seconds**.
- At the end, **green = Intervention** and **purple = Control**; an allocation JSON download appears after the visual reveal.

## Source files

- `app.py` — the Streamlit application, 15-second animation and session draw
- `assets/sites.csv` — image-positioned site data and verified/edited group membership
- `assets/province_outline.svg` — outer provincial outline only
- `assets/area_envelopes.json` — precomputed A/B site envelopes and their full blue non-study complement
- `scripts/generate_areas.py` — optional reproducible generator for the A/B envelopes and blue complement

To run the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

If you edit the site coordinates or group assignments, regenerate the study envelopes and blue complement before committing:

```bash
pip install 'shapely>=2'
python scripts/generate_areas.py
```

Only Streamlit is needed to **run** the app; Shapely is only needed to **regenerate** the area-shape asset.

## Important limitations

This is a visual prototype, **not a production clinical trial randomisation service**. Site coordinates and group envelopes were digitised from supplied images and must be checked against authoritative study records. Session state is not a durable allocation ledger, and the animation provides no allocation concealment against a user inspecting the page. Approved trial use requires an auditable, persistent and protocol-approved allocation system with access controls and protection against repeat draws.
