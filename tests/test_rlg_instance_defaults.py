## -*- coding: utf-8 -*-

from __future__ import annotations

import pytest
from pathlib import Path

from cartopy.crs import PlateCarree
from mr_radar.rlg_defaults import RLGDefaults
from mr_radar.radar_loop_generator import RadarLoopGenerator

SITE_ID   = 'KSJT'


@pytest.fixture( scope='class' )
def default_output_path() -> str:
    path = Path( RLGDefaults.output_path )
    return str( path )


@pytest.fixture( scope='class' )
def default_image_path( default_output_path: str ) -> str:
    path = Path( default_output_path, SITE_ID.lower() )
    return str( path )


@pytest.fixture( scope='class' )
def default_json_path( default_output_path: str ) -> str:
    path = Path( default_output_path, SITE_ID.lower() ).with_suffix( '.json' )
    return str( path )


@pytest.fixture( scope='class' )
def generator() -> RadarLoopGenerator:
    return RadarLoopGenerator( site_id = SITE_ID )


class TestRLGInstanceDefaults:

    def test_site_id( self, generator: RadarLoopGenerator ) -> None:
        """ site_id should be an upper-case version of whatever was supplied
        """
        assert generator.site_id == SITE_ID

    def test_default_radius( self, generator: RadarLoopGenerator ) -> None:
        """ default radius is 150 miles
        """
        assert generator.radius == RLGDefaults.radius

    def test_empty_site_coords( self, generator: RadarLoopGenerator ) -> None:
        """ the site coordinates shouldn't be set yet
        """
        assert generator.site_coords is None

    def test_empty_image_bbox( self, generator: RadarLoopGenerator ) -> None:
        """ the bounding box shouldn't be set yet
        """
        assert generator.image_bbox is None

    def test_empty_image_envelope( self, generator: RadarLoopGenerator ) -> None:
        """ the envelope shouldn't be set yet
        """
        assert generator.image_envelope is None

    def test_empty_axes( self, generator: RadarLoopGenerator ) -> None:
        """ the axes shouldn't be set yet
        """
        assert generator.axes is None

    def test_empty_figure( self, generator: RadarLoopGenerator ) -> None:
        """ the figure shouldn't be set yet
        """
        assert generator.figure is None

    def test_default_output_path( self, generator: RadarLoopGenerator ) -> None:
        """ default output root is './out'
        """
        assert generator.output_path == RLGDefaults.output_path

    def test_default_image_path( self, generator: RadarLoopGenerator, default_image_path: str ) -> None:
        """ default image output is a directory named from the site_id, relative to the output root
        """
        assert generator.image_path == default_image_path

    def test_default_file_name( self, generator: RadarLoopGenerator ) -> None:
        """ file name should be blank (this happens in child classes)
        """
        assert not generator.file_name

    def test_file_name_setter( self, generator: RadarLoopGenerator ) -> None:
        """ file name is set in child classes, so in the parent, the setter does nothing
        """
        generator.file_name = 'foobar'
        self.test_default_file_name( generator )

    def test_image_file_path_name( self, generator: RadarLoopGenerator, default_image_path: str ) -> None:
        """ the full image pathname would be
              - <root>/<site_id>/map.png
              - <root>/<site_id>/frame_<i>.png
            ...but since the parent class has an empty `file_name` attribute, the path will be incomplete
        """
        assert generator.image_file_path_name == default_image_path

    def test_json_path( self, generator: RadarLoopGenerator, default_json_path: str ) -> None:
        """ JSON file should be named from site_id relative to the output root
        """
        assert generator.json_path == default_json_path

    def test_crs( self, generator: RadarLoopGenerator ) -> None:
        """ the coordinate reference system should be an equirectangular projection
            a.k.a. Plate Carrée
        """
        assert isinstance( generator.crs, PlateCarree )

    def test_attribute_frames( self, generator: RadarLoopGenerator ) -> None:
        """ the parent class does not have the 'frames' attribute
        """
        assert not hasattr( generator, 'frames' )

    def test_attribute_product( self, generator: RadarLoopGenerator ) -> None:
        """ the parent class does not have the 'product' attribute
        """
        assert not hasattr( generator, 'product' )

