# DiSrupT RR-TB geographic randomisation map

Interactive Streamlit visualisation of a 50:50 random assignment between two predefined KwaZulu-Natal geographic groups.

## What happens

1. Click **RANDOMISE**. Python uses `secrets.randbelow(2)` to pick the intervention group **before** the visual effect begins.
2. The map's initiation-site dots (not entire polygons) alternate **green / blue** quickly at first and then progressively more slowly.
3. The animation stops with the randomly selected group's dots **green = Intervention** and the other group's dots **blue = Control**.
4. The session result is shown below the map and can be downloaded as JSON.

The district boundaries and site locations remain visible using `assets/kzn_map.webp`, derived from the uncoloured reference image provided for this app.

## Current demonstration groups

- **Block A · North-east** — 26 image-detected initiation-site dots
- **Block B · South-west** — 15 image-detected initiation-site dots

Dots were located on the map and assigned to one of the two groups using the highlighted block regions in the supplied reference. These **image-based detections and group memberships are approximate**, not a validated authoritative site register. Please verify all site identities and their block memberships against the approved study list/GIS data before use.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files

- `app.py` — Streamlit UI, secure draw, site groups, animation, and session record
- `assets/kzn_map.webp` — reference district/facility background map
- `requirements.txt` — Python packages

## Important

This is a **visual prototype**, not a production clinical-trial randomisation system. The draw is 50:50 and generated before the animation, but Streamlit session state is not a durable allocation ledger. Operational trial use requires verified cluster assignments, preapproved allocation procedures, secure authentication, idempotence, audit logs, allocation concealment where required, and persistent storage.
