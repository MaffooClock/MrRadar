## -*- coding: utf-8 -*-

from __future__ import annotations

import string
import random
import pytest

from mr_radar.rlg_cache import RLGCache


def random_filename() -> str:
    return ''.join( random.choices( string.ascii_letters, k=8 ) )


@pytest.fixture( scope='class' )
def cache_instance() -> RLGCache:
    return RLGCache()


@pytest.fixture( scope='class' )
def cache_obj( cache_instance, tmp_path_factory ) -> RLGCache:
    json_path = tmp_path_factory.getbasetemp()
    json_file = json_path.with_name( 'mr_radar' )
    cache_instance.load( str( json_file ) )
    yield cache_instance
    json_file.with_suffix( '.json' ).unlink()



class TestCache:

    def test_not_loaded( self, cache_instance: RLGCache ) -> None:

        assert not cache_instance.is_loaded

        with pytest.raises( RuntimeError ):
            assert cache_instance.exists

        with pytest.raises( RuntimeError ):
            assert cache_instance.get( 'foobar' )

        with pytest.raises( RuntimeError ):
            assert cache_instance.set( 'foo', 'bar' )

        with pytest.raises( RuntimeError ):
            assert cache_instance.rem( 'boofar' )

        assert not cache_instance.dump()


    def test_dump( self, cache_instance: RLGCache, tmp_path_factory ) -> None:
        json_path = tmp_path_factory.getbasetemp()
        json_file = json_path.with_name( random_filename() )
        cache_instance.load( str( json_file ) )

        assert not cache_instance.exists

        assert cache_instance.dump( force=True )

        assert cache_instance.exists

        json_file.with_suffix( '.json' ).unlink()


    def test_exists_after_dump( self, cache_obj: RLGCache ) -> None:
        assert cache_obj.dump( force=True )
        assert cache_obj.exists


    def test_set_none( self, cache_obj: RLGCache ) -> None:
        assert cache_obj.set( 'someKey', 'someValue' )
        assert cache_obj.set( 'someKey', None )
        assert not cache_obj.set( 'notSet', None )


    def test_invalid_get( self, cache_obj: RLGCache ) -> None:
        assert cache_obj.get( 'foobar' ) is None


    def test_contains( self, cache_obj: RLGCache ) -> None:
        cache_obj.set( 'testKey', 'testValue' )
        assert not 'unobtanium' in cache_obj
        assert 'testKey' in cache_obj


    def test_set_get_rm( self, cache_obj: RLGCache ) -> None:
        assert cache_obj.set( 'foo', 'bar' )
        assert cache_obj.get( 'foo' ) == 'bar'
        assert cache_obj.rem( 'foo' )


    def test_invalid_rm( self, cache_obj: RLGCache ) -> None:
        assert not cache_obj.rem( 'notSet' )

