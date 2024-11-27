## -*- coding: utf-8 -*-

from __future__ import annotations

import pytest
from pathlib import Path

from mr_radar.radar_loop_generator import RadarLoopGenerator

SITE_ID = 'KSJT'
RADIUS  = 200


@pytest.fixture( scope='class' )
def site_id() -> str:
    return SITE_ID


@pytest.fixture( scope='class' )
def image_dir( image_path: str ) -> str:
    return Path( image_path ).name


@pytest.fixture( scope='class' )
def generator( temp_path: str, image_dir: str ) -> RadarLoopGenerator:
    return RadarLoopGenerator(
        site_id     = SITE_ID,
        radius      = RADIUS,
        output_path = temp_path,
        image_dir   = image_dir
    )


class TestRLGValidInstance:

    def test_radius( self, generator: RadarLoopGenerator ) -> None:
        assert generator.radius == RADIUS

    def test_output_path( self, generator: RadarLoopGenerator, temp_path: str ) -> None:
        assert generator.output_path == temp_path

    def test_image_dir( self, generator: RadarLoopGenerator, image_path: str ) -> None:
        assert generator.image_path == image_path

    def test_json_path( self, generator: RadarLoopGenerator, expected_json_file: Path ) -> None:
        assert generator.json_path == str( expected_json_file )

    def test_generator( self, generator: RadarLoopGenerator, expected_json_file: Path, check ) -> None:
        generator.generate()

        with check:
            assert expected_json_file.exists()

        with check:
            assert expected_json_file.is_file()

