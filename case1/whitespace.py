"""Case 1 helpers — broadband whitespace analysis.

The small, testable core of the afternoon's case: load FCC availability
rows, decide which offers count as "served", and find whitespace blocks.
This is the library the Day 1 CI exercise pushes through GitHub Actions.
"""

import pandas as pd

# FCC technology codes for satellite service. Satellite covers everywhere
# on paper, so counting it as "served" would erase the whitespace signal.
SATELLITE = {60, 61}

# Technologies we treat as low-latency enough to compete for home broadband.
LOW_LATENCY = 1


def load_locations(path):
    """Load an FCC availability extract, keeping GEOIDs as strings.

    Census GEOIDs can start with 0 (Illinois is '17...', but county and
    block codes inside the GEOID carry leading zeros). Reading them as
    integers silently corrupts them, so every geoid column is forced to str.
    """
    df = pd.read_csv(path, dtype={"block_geoid": str, "county_geoid": str})
    return df


def served_offers(avail, down_min=100, up_min=20):
    """Return the rows that count as a real served offer.

    A row counts when it is a residential offer (R or X), is not
    satellite, is low-latency, and meets the speed thresholds.
    """
    out = avail[
        avail["business_residential_code"].isin(["R", "X"])
        & ~avail["technology"].isin(SATELLITE)
        & (avail["low_latency"] == LOW_LATENCY)
        & (avail["max_download_speed"] >= down_min)
        & (avail["max_upload_speed"] >= up_min)
    ]
    return out


def whitespace_blocks(blk, max_competitors=1):
    """Blocks with at most `max_competitors` served providers.

    `blk` is a per-block frame with a `served_providers` count column.
    """
    return blk[blk["served_providers"] <= max_competitors]
