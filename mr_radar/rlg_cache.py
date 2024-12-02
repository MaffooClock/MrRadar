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


    def __contains__( self, key: str ) -> bool:
        return self._pickledb.exists( key )


    @property
    def is_dirty( self ) -> bool:
        return self._dirty


    @property
    def is_loaded( self ) -> bool:
        return self._json_file and self._pickledb


    @property
    def exists( self ) -> bool:
        self._check_loaded()
        path_exists = Path( self._json_file ).exists()
        is_file = Path( self._json_file ).is_file()
        return path_exists and is_file


    def load( self, name: str ) -> str:
        if name[-5:].lower() != '.json':
            name += '.json'
        self._json_file = name
        self._pickledb = pickledb.load( self._json_file, False )
        return self._json_file


    def get( self, key: str, default=None ) -> Any | None:
        self._check_loaded()

        if not self._pickledb.exists( key ):
            self._pickledb.set( key, default )

        return self._pickledb.get( key )


    def set( self, key: str, value: Any | None ) -> bool:
        self._check_loaded()

        if value is None:
            if self._pickledb.exists( key ):
                return self.rem( key )
            return False

        if not self._pickledb.exists( key ) or self._pickledb.get( key ) != value :
            self._dirty = True
            return self._pickledb.set( key, value )

        return False


    def rem( self, key: str ) -> bool:
        self._check_loaded()

        if not self._pickledb.exists( key ):
            return False

        self._dirty = True

        return self._pickledb.rem( key )


    def dump( self, force: bool=False ) -> bool:

        if not self._json_file:
            return False

        if self.is_dirty or force:
            self._dirty = False
            return self._pickledb.dump()

        return True


    def _check_loaded( self ):
        if not self.is_loaded:
            raise RuntimeError( 'JSON has not been loaded' )
