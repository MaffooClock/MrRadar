## -*- coding: utf-8 -*-

import pytest
from pathlib import Path

from mr_radar.rlg_exception import RLGValueError
from mr_radar.radar_loop_generator import RadarLoopGenerator

VALID_SITE_ID = 'KSJT'

class TestInvalidInstance:

    def test_empty_site_id( self ):
        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id='' )

    def test_invalid_site_id( self ):
        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id='foobar' )

    def test_invalid_radius_string( self ):
        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id=VALID_SITE_ID, radius='foobar' )

    def test_invalid_radius_range( self ):
        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id=VALID_SITE_ID, radius=-1 )

    def test_invalid_output_path( self ):
        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id=VALID_SITE_ID, output_path=0 )

    def test_existing_output_path( self, tmp_path ):
        existing_file = Path( tmp_path, VALID_SITE_ID )
        with open( existing_file, 'a' ) as f:
            Path( f.name ).touch()

        with pytest.raises( RLGValueError ):
            RadarLoopGenerator( site_id=VALID_SITE_ID, output_path=str( existing_file ) )

