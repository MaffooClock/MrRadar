## -*- coding: utf-8 -*-

from __future__ import annotations
import inspect


class CacheKeys:

    @property
    def SITE_COORDS( self ) -> str:
        return 'site_coords'

    @property
    def RADIUS( self ) -> str:
        return 'radius'

    @property
    def BBOX( self ) -> str:
        return 'bbox'

    @property
    def ENVELOPE( self ) -> str:
        return 'envelope'

    @property
    def OUTPUT_PATH( self ) -> str:
        return 'output_path'

    @property
    def IMAGE_PATH( self ) -> str:
        return 'image_path'

    @property
    def FILE_NAME( self ) -> str | None:

        prev_frame = inspect.currentframe().f_back
        calling_class = prev_frame.f_locals['self'].__class__.__name__

        if calling_class == 'MapGenerator':
            return 'map_file_name'

        elif calling_class == 'FrameGenerator':
            return 'frames_file_name'

        else:
            return None

    @property
    def PRODUCT( self ) -> str:
        return 'product'

    @property
    def FRAMES( self ) -> str:
        return 'frames'


RadarCacheKeys = CacheKeys()
