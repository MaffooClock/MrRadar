# coding: utf-8

from __future__ import annotations


class RLGException( Exception ):

    def __init__( self, message ):
        self.message = message
        super().__init__( self.message )


class RLGValueError( RLGException ):

    def __init__( self, message ):
        self.message = message
        super().__init__( self.message )


class RLGTypeError( RLGException ):

    def __init__( self, message ):
        self.message = message
        super().__init__( self.message )


class RLGRuntimeError( RLGException ):

    def __init__( self, message ):
        self.message = message
        super().__init__( self.message )
