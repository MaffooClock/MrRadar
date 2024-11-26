## -*- coding: utf-8 -*-

import pytest
from pathlib import Path

from mr_radar.rlg_exception import RLGValueError
from mr_radar.radar_loop_generator import RadarLoopGenerator


generator = RadarLoopGenerator(
    site_id     = 'KSJT',
    radius      = 200,
    output_path = 'foo',
    image_dir   = 'bar'
)

class TestValidInstance:

    def test_radius( self ):
        assert generator.radius == 200

    def test_output_path( self ):
        path = Path( 'foo' ).resolve()
        assert generator.output_path == str( path )

    def test_image_dir( self ):
        path = Path( 'foo', 'bar' ).resolve()
        assert generator.image_path == str( path )
