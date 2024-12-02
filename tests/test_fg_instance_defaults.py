## -*- coding: utf-8 -*-

from __future__ import annotations

import pytest
from pathlib import Path

from mr_radar.rlg_defaults import RLGDefaults
from mr_radar.frame_generator import FrameGenerator

SITE_ID = 'KSJT'


@pytest.fixture( scope='class' )
def image_path() -> Path:
    return Path( RLGDefaults.output_path, SITE_ID.lower(), f"{RLGDefaults.frame_file_name}_%d" ).with_suffix('.png')


@pytest.fixture( scope='class' )
def generator() -> FrameGenerator:
    return FrameGenerator( site_id = SITE_ID )


class TestFGInstanceDefaults:

    def test_default_file_name( self, generator: FrameGenerator, image_path: Path ) -> None:
        assert generator.file_name == image_path.name

    def test_image_file_path_name( self, generator: FrameGenerator, image_path: Path ) -> None:
        """ the full image pathname should be <root>/<site_id>/frame_%d.png
        """
        assert generator.image_file_path_name == str( image_path )

    def test_default_product( self, generator: FrameGenerator ) -> None:
        assert generator.product == RLGDefaults.product

    def test_default_frames( self, generator: FrameGenerator ) -> None:
        assert generator.frames == RLGDefaults.frames
