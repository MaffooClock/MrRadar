## -*- coding: utf-8 -*-

from __future__ import annotations

import pytest
from pathlib import Path

from mr_radar.rlg_defaults import RLGDefaults
from mr_radar.map_generator import MapGenerator

SITE_ID    = 'KSJT'
RADIUS     = 200
IMAGE_NAME = 'foobar'


@pytest.fixture( scope='class' )
def site_id() -> str:
    return SITE_ID


@pytest.fixture( scope='class' )
def image_name() -> str:
    return IMAGE_NAME


@pytest.fixture( scope='class' )
def generator( temp_path: str, image_path: str, expected_json_file: Path ) -> MapGenerator:
    return MapGenerator(
        site_id     = SITE_ID,
        radius      = RADIUS,
        output_path = temp_path,
        image_dir   = image_path,
        name        = IMAGE_NAME
    )


class TestMGValidInstance:

    def test_file_name( self, generator: MapGenerator ) -> None:
        assert generator.file_name != RLGDefaults.map_file_name

    def test_generator( self, generator: MapGenerator, expected_image_file, check ) -> None:
        generator.generate()

        assert generator.image_file_path_name == str( expected_image_file )

        with check:
            assert expected_image_file.exists()

        with check:
            assert expected_image_file.is_file()

        with check:
            assert expected_image_file.stat().st_size > 0
