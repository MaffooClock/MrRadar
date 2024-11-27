## -*- coding: utf-8 -*-

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.fixture( scope='class' )
def temp_path() -> str:
    temp_path = tempfile.mkdtemp()
    yield temp_path
    try:
        Path( temp_path ).rmdir()
    except OSError:
        pass


@pytest.fixture( scope='class' )
def image_path( temp_path: str ) -> str:
    image_path = tempfile.mkdtemp( dir=temp_path )
    yield image_path
    try:
        Path( image_path ).rmdir()
    except OSError:
        pass


@pytest.fixture( scope='class' )
def expected_image_file( image_path: str, image_name: str ) -> Path:
    image_file = Path( image_path, image_name ).with_suffix( '.png' )
    yield image_file
    image_file.unlink( missing_ok=True )

### TODO: currently broken
# @pytest.fixture( scope='class' )
# def expected_indexed_image_file( image_path: str, image_name: str ) -> callable:
#     def _indexed_image_file( i: int ):
#         _image_file = Path( image_path, image_name % i ).with_suffix( '.png' )
#         yield _image_file
#         _image_file.unlink( missing_ok=True )
#     yield _indexed_image_file


@pytest.fixture( scope='class' )
def expected_legend_file( image_path, image_name ) -> Path:
    legend_file = Path( image_path, f"{image_name}_legend" ).with_suffix( '.png' )
    yield legend_file
    legend_file.unlink( missing_ok=True )


@pytest.fixture( scope='class' )
def expected_json_file( temp_path: str, site_id: str ) -> Path:
    json_file = Path( temp_path, site_id.lower() ).with_suffix( '.json' )
    yield json_file
    json_file.unlink( missing_ok=True )
