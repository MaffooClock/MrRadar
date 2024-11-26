## -*- coding: utf-8 -*-

import pytest

from cartopy.crs import PlateCarree
from mr_radar.radar_loop_generator import RadarLoopGenerator

VALID_SITE_ID = 'KSJT'
LOWER_SITE_ID = VALID_SITE_ID.lower()
generator = RadarLoopGenerator( site_id=VALID_SITE_ID )

class TestInstanceDefaults:

    def test_site_id( self ):
        """ site_id should be an upper-case version of whatever was supplied
        """
        assert generator.site_id == VALID_SITE_ID

    def test_default_radius( self ):
        """ default radius is 150 miles
        """
        assert generator.radius == 150

    def test_empty_site_coords( self ):
        """ the site coordinates shouldn't be set yet
        """
        assert generator.site_coords is None

    def test_empty_image_bbox( self ):
        """ the bounding box shouldn't be set yet
        """
        assert generator.image_bbox is None

    def test_empty_image_envelope( self ):
        """ the envelope shouldn't be set yet
        """
        assert generator.image_envelope is None

    def test_empty_axes( self ):
        """ the axes shouldn't be set yet
        """
        assert generator.axes is None

    def test_empty_figure( self ):
        """ the figure shouldn't be set yet
        """
        assert generator.figure is None

    def test_default_output_path( self ):
        """ default output root is './out'
        """
        assert generator.output_path == './out'

    def test_default_image_path( self ):
        """ default image output is a directory named from the site_id, relative to the output root
        """
        assert generator.image_path == f"out/{LOWER_SITE_ID}"

    def test_default_file_name( self ):
        """ file name should be blank (this happens in child classes)
        """
        assert generator.file_name == ''

    def test_file_name_setter( self ):
        """ file name is set in child classes, so in the parent, the setter does nothing
        """
        generator.file_name = 'foobar'
        self.test_default_file_name()

    def test_image_file_path_name( self ):
        """ the full image pathname would be
            - <root>/<site_id>/map.png
            - <root>/<site_id>/frame_<i>.png
            ...but since the parent class has an empty `file_name` attribute,
            the path will be incomplete
        """
        assert generator.image_file_path_name == f"out/{LOWER_SITE_ID}"

    def test_json_path( self ):
        """ JSON file should be named from site_id relative to the output root
        """
        assert generator.json_path == f"out/{LOWER_SITE_ID}.json"

    def test_crs( self ):
        """ the coordinate reference system should be an equirectangular projection
            a.k.a. Plate Carrée
        """
        assert isinstance( generator.crs, PlateCarree )

    def test_attribute_frames( self ):
        """ the parent class does not have the 'frames' attribute
        """
        assert not hasattr( generator, 'frames' )

    def test_attribute_product( self ):
        """ the parent class does not have the 'product' attribute
        """
        assert not hasattr( generator, 'product' )

