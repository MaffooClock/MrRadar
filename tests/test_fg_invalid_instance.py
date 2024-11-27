## -*- coding: utf-8 -*-

from __future__ import annotations

import pytest
from pathlib import Path

from awips.ThriftClient import ThriftRequestException

from mr_radar.rlg_exception import RLGValueError
from mr_radar.rlg_defaults import RLGDefaults
from mr_radar.frame_generator import FrameGenerator

VALID_SITE_ID = 'KSJT'

def empty_dir( path: Path ) -> None:
    for file in path.iterdir():
        if file.is_dir():
            try:
                file.rmdir()
            except OSError:
                empty_dir( file )
        else:
            file.unlink()

def cleanup() -> None:
    path = Path( RLGDefaults.output_path )
    empty_dir( path )
    try:
        path.rmdir()
    except OSError:
        pass


class TestFGInvalidInstance:

    def test_invalid_radius_string( self ) -> None:
        with pytest.raises( RLGValueError ):
            FrameGenerator( site_id=VALID_SITE_ID, frames='foobar' )

    def test_invalid_frames_range( self ) -> None:
        with pytest.raises( RLGValueError ):
            FrameGenerator( site_id=VALID_SITE_ID, frames=-1 )

    def test_invalid_product( self ) -> None:
        generator = FrameGenerator( site_id=VALID_SITE_ID, frames=1, product='foobar')
        with pytest.raises( ThriftRequestException ):
            generator.generate()

        cleanup()
