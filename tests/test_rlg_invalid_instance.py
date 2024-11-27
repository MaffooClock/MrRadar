## -*- coding: utf-8 -*-

from __future__ import annotations

import pytest
from pathlib import Path

from mr_radar.rlg_exception import RLGValueError
from mr_radar.radar_loop_generator import RadarLoopGenerator

VALID_SITE_ID = 'KSJT'


@pytest.fixture
def existing_file( tmp_path: Path ) -> str:
    existing_file = Path( tmp_path, VALID_SITE_ID )
    with open( existing_file, 'a' ) as f:
        Path( f.name ).touch()
    return str( existing_file )


class TestRLGInvalidInstance:

    def test_empty_site_id( self ) -> None:
        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id='' )

    def test_invalid_site_id( self ) -> None:
        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id='foobar' )

    def test_invalid_radius_string( self ) -> None:
        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id=VALID_SITE_ID, radius='foobar' )

    def test_invalid_radius_range( self ) -> None:
        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id=VALID_SITE_ID, radius=-1 )

    def test_invalid_output_path( self ) -> None:
        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id=VALID_SITE_ID, output_path=0 )

    def test_existing_output_path( self, tmp_path: Path, existing_file: str ) -> None:
        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id=VALID_SITE_ID, output_path=existing_file )

