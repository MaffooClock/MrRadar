## -*- coding: utf-8 -*-

from __future__ import annotations

import pytest
from pathlib import Path

from mr_radar.rlg_defaults import RLGDefaults
from mr_radar.map_generator import MapGenerator

SITE_ID = 'KSJT'


@pytest.fixture( scope='class' )
def image_path() -> Path:
    return Path( RLGDefaults.output_path, SITE_ID.lower(), RLGDefaults.map_file_name ).with_suffix('.png')


@pytest.fixture( scope='class' )
def generator() -> MapGenerator:
    return MapGenerator( site_id = SITE_ID )


class TestMGInstanceDefaults:

    def test_default_file_name( self, generator: MapGenerator, image_path: Path ) -> None:
        assert generator.file_name == image_path.name

    def test_image_file_path_name( self, generator: MapGenerator, image_path: Path ) -> None:
        """ the full image pathname should be <root>/<site_id>/map.png
        """
        assert generator.image_file_path_name == str( image_path )
