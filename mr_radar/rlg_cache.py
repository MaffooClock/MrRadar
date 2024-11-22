## -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Any

import pickledb
from pathlib import Path


class RLGCache:
    """
    An abstraction of pickledb that allows a default value for get()
    See: https://github.com/patx/pickledb/issues/3
         https://github.com/patx/pickledb/pull/23
    """

    def __init__( self ) -> None:
        self._pickledb = None
        self._dirty = False
        self._json_file = None

    def __contains__( self, key ) -> bool:
        return self._pickledb.exists( key )

    @property
    def is_dirty( self ) -> bool:
        return self._dirty

    @property
    def exists( self ) -> bool:
        path_exists = Path( self._json_file ).exists()
        is_file = Path( self._json_file ).is_file()
        return path_exists and is_file

    def load( self, name ) -> None:
        self._json_file = f"{name.lower()}.json"
        self._pickledb = pickledb.load( self._json_file, False )

    def get( self, key, default=None ) -> Any | None:
        if not self._pickledb.exists( key ):
            self._pickledb.set( key, default )
        return self._pickledb.get( key )

    def set( self, key: str, value: Any | None ) -> bool:

        if value is None and self._pickledb.exists( key ):
            return self.rem( key )

        if not self._pickledb.exists( key ) or self._pickledb.get( key ) != value :
            self._dirty = True
            return self._pickledb.set( key, value )

        return False

    def rem( self, key ) -> bool:
        self._dirty = True
        return self._pickledb.rem( key )

    def dump( self, force=False ) -> bool:

        if not self._json_file:
            return False

        if self.is_dirty or force:
            self._dirty = False
            return self._pickledb.dump()

        return True

