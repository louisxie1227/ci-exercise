"""Tests for case1.whitespace — the Day 1 CI exercise suite.

Each test pins down a real bug from the afternoon's case: the GEOID
dtype trap, satellite rows sneaking into "served", and the whitespace
competitor rule. Small inline fixtures, no network, runs in seconds.
"""

import io

import pandas as pd

from case1.whitespace import (
    SATELLITE,
    load_locations,
    served_offers,
    whitespace_blocks,
)


def _avail():
    return pd.DataFrame(
        {
            "technology": [50, 60, 71, 61, 50],
            "business_residential_code": ["R", "R", "X", "R", "B"],
            "low_latency": [1, 0, 1, 0, 1],
            "max_download_speed": [300, 100, 1000, 100, 940],
            "max_upload_speed": [30, 20, 500, 20, 35],
        }
    )


def test_geoid_keeps_leading_zeros():
    csv = io.StringIO(
        "block_geoid,county_geoid,provider_id\n"
        "170312108001012,17031,130077\n"
        "170978645002005,17097,130404\n"
    )
    locs = load_locations(csv)
    # Read as int, a GEOID like 089... loses its leading zero. As str,
    # every census block GEOID is exactly 15 characters.
    assert locs.block_geoid.str.len().eq(15).all()
    # String dtype, not numeric — pandas may report this as `object` or the
    # newer `StringDtype` depending on version, so test the property, not the name.
    assert pd.api.types.is_string_dtype(locs.block_geoid)


def test_satellite_never_counts_as_served():
    served = served_offers(_avail(), down_min=100, up_min=20)
    assert not served.technology.isin(SATELLITE).any()
    assert len(served) == 2  # the two non-satellite residential offers


def test_business_only_offers_do_not_count():
    served = served_offers(_avail(), down_min=100, up_min=20)
    assert not served.business_residential_code.eq("B").any()


def test_whitespace_is_at_most_one_competitor():
    blk = pd.DataFrame(
        {
            "block_geoid": ["a", "b", "c", "d"],
            "served_providers": [0, 1, 2, 3],
        }
    )
    ws = whitespace_blocks(blk, max_competitors=1)
    assert set(ws.block_geoid) == {"a", "b"}
