# DiSrupT RR-TB geographic randomisation animation

Streamlit demonstration of two geographic blocks alternating rapidly, slowing down, and stopping with one assigned Intervention and the other Control.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Map artwork

The Streamlit app runs without additional image files using built-in vector block boundaries. To display the detailed map and facility markers beneath the selection animation, upload the supplied map background as `assets/kzn_map.webp` (540 × 574 pixels). This is optional; the block animation works either way. The vector outlines are illustrative approximations and must be validated against authoritative GIS boundaries before use.

## Important limitations

This repository provides a **visual prototype**, not an approved trial randomisation system. It makes a cryptographically secure 50:50 draw before the animation begins, but the assignment is only stored in the current Streamlit session. Operational use requires durable audit logs, authenticated access, allocation concealment, approved sequence-generation rules, and protection against duplicate allocations and reruns.
