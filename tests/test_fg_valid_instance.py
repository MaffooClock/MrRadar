## -*- coding: utf-8 -*-

from __future__ import annotations

import pytest
from pathlib import Path

from mr_radar.rlg_defaults import RLGDefaults
from mr_radar.frame_generator import FrameGenerator

SITE_ID    = 'KSJT'
RADIUS     = 200
IMAGE_NAME = 'foobar'
FRAMES     = 2


@pytest.fixture( scope='class' )
def site_id() -> str:
    return SITE_ID


@pytest.fixture( scope='class' )
def image_name() -> str:
    return f"{IMAGE_NAME}_%d"


@pytest.fixture( scope='class' )
def generator( temp_path: str, image_path: str, expected_json_file: Path ) -> FrameGenerator:
    return FrameGenerator(
        site_id     = SITE_ID,
        radius      = RADIUS,
        output_path = temp_path,
        image_dir   = image_path,
        name        = IMAGE_NAME,
        frames      = FRAMES
    )


class TestFGValidInstance:

    def test_file_name( self, generator: FrameGenerator ) -> None:
        assert generator.file_name != RLGDefaults.map_file_name

    ### TODO: expected_indexed_image_file() doesn't work yet
    # def test_generator( self, generator: FrameGenerator, expected_image_file: Path, expected_indexed_image_file: callable, check ) -> None:
    def test_generator( self, generator: FrameGenerator, expected_image_file: Path ) -> None:
        generator.generate()

        assert generator.image_file_path_name == str( expected_image_file )

        ### TODO: expected_indexed_image_file() doesn't work yet
        # for i in range( FRAMES ):
        #     file_path_name = expected_indexed_image_file( i )
        #     print('==========')
        #     print(str(file_path_name))
        #     print('==========')
        #
        #     with check:
        #         assert file_path_name.exists()
        #
        #     with check:
        #         assert file_path_name.is_file()
        #
        #     with check:
        #         assert file_path_name.stat().st_size > 0
