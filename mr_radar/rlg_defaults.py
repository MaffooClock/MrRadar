## -*- coding: utf-8 -*-

from __future__ import annotations

from os import environ
from pathlib import Path

class _RLGDefaults:

    def __init__( self ):
        self._dockerized = environ.get( 'RLG_DOCKERIZED', False )

    @property
    def output_path( self ) -> str:
        cwd_out = str( Path( Path.cwd(), 'out' ) )
        return '/data' if self.dockerized else cwd_out

    @property
    def map_file_name( self ) -> str:
        return 'map'

    @property
    def frame_file_name( self ) -> str:
        return 'frame'

    @property
    def radius( self ) -> int:
        return 150

    @property
    def product( self ) -> str:
        return 'Reflectivity'

    @property
    def frames( self ) -> int:
        return 12

    @property
    def dockerized( self ):
        return self._dockerized


RLGDefaults = _RLGDefaults()
