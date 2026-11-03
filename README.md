# DiSrupT geographic randomisation — initiation-site map

Streamlit demonstration for a 50:50 allocation of two KwaZulu-Natal study areas using a clean **province-only outline** and individually positioned initiation-site dots.

## Site map

The map is built from the supplied annotated source image; no internal district boundaries, filled choropleth colours or district shading are shown.

- **Study area A:** 24 purple-labelled sites (north-eastern grouping in source)
- **Study area B:** 18 green-labelled sites (south-western grouping in source)
- **Non-study:** 15 blue-labelled sites

The app's starting colours mirror the annotated source. During the animation, study-area dots alternate between **green** (candidate intervention) and **light blue** (candidate control), first rapidly and progressively slower. Non-study dots remain **dark blue**, unchanged throughout. The result is a secure 50:50 draw made in Python before the animation starts.

## Files

- `app.py` — Streamlit app and animation.
- `assets/sites.csv` — editable site coordinates and area classifications, referenced to the 918×1038 source image.
- `assets/province_outline.svg` — vectorised external provincial outline only.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Validation and limitations

The dot centres and provincial outline were **digitised from the reference image**, not extracted from authoritative GIS data or an official study site roster. **Review and correct any site identities/coordinates/classification before using them for study decisions.**

This is a visual demonstrator, **not a clinical-trial allocation service**. Session state and the downloadable JSON file are not a durable, access-controlled audit log. Operational use requires an approved allocation algorithm, access controls, pre-specified handling of repeat requests, persistent audit logging, and protocol-validated site definitions.