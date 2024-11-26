## -*- coding: utf-8 -*-

from __future__ import annotations

import warnings
import re
from pathlib import Path

from loguru import logger
from awips.dataaccess import DataAccessLayer
from matplotlib import pyplot
import cartopy.crs as ccrs
import shapely.geometry as sgeo

from .rlg_defaults import RLGDefaults
from .rlg_cache import RLGCache
from .cache_keys import RadarCacheKeys
from .bounding_box_calculator import BoundingBoxCalculator
from .rlg_exception import *

# suppress a few warnings that come from plotting
warnings.filterwarnings( 'ignore', category=RuntimeWarning )
warnings.filterwarnings( 'ignore', category=UserWarning )


EDEX_HOST = 'edex-cloud.unidata.ucar.edu'


class RadarLoopGenerator:

    def __init__( self, site_id: str, radius: int=None, output_path: str=None, image_dir: str=None, **kwargs ) -> None:

        DataAccessLayer.changeEDEXHost( EDEX_HOST )

        self._site_id     = None
        self._output_path = None
        self._axes        = None
        self._figure      = None

        self.cache = RLGCache()

        self.site_id     = site_id
        self.radius      = radius
        self.output_path = output_path
        self.image_path  = image_dir


    @property
    def site_id( self ) -> str:
        return self._site_id


    @site_id.setter
    def site_id( self, site_id: str ) -> None:
        self._validate_site_id( site_id )
        self._site_id = site_id.upper()
        self.cache.load( str( self.json_path ) )
        logger.info( "→ Site ID is '{}'", self.site_id )


    @property
    def radius( self ) -> int:
        return self.cache.get( RadarCacheKeys.RADIUS, RLGDefaults.radius )


    @radius.setter
    def radius( self, radius: int ) -> None:

        if radius is None:
            return

        self._validate_radius( radius )

        if self.radius != radius:
            self.cache.rem( RadarCacheKeys.BBOX )
            self.cache.rem( RadarCacheKeys.ENVELOPE )

        self.cache.set( RadarCacheKeys.RADIUS, radius )
        logger.info( "→ Radius is {} miles", radius )


    @property
    def site_coords( self ) -> ( float, float ):
        return self.cache.get( RadarCacheKeys.SITE_COORDS )


    @site_coords.setter
    def site_coords( self, coords: ( float, float ) ) -> None:
        self.cache.set( RadarCacheKeys.SITE_COORDS, coords )
        logger.info( "Coordinates for {}: {}", self.site_id, coords )


    @property
    def image_bbox( self ) -> [ float, float, float, float ]:
        return self.cache.get( RadarCacheKeys.BBOX )


    @image_bbox.setter
    def image_bbox( self, coords: ( float, float ) ) -> None:
        self.cache.set( RadarCacheKeys.BBOX, coords )


    @property
    def image_envelope( self ) -> sgeo.Polygon | None:
        envelope = self.cache.get( RadarCacheKeys.ENVELOPE )
        return sgeo.shape( envelope ) if envelope else None


    @image_envelope.setter
    def image_envelope( self, envelope: sgeo.Polygon ) -> None:
        self.cache.set( RadarCacheKeys.ENVELOPE, envelope )


    @property
    def crs( self ) -> ccrs.Projection:
        return ccrs.PlateCarree()


    @property
    def file_name( self ) -> str:
        return ''


    @file_name.setter
    def file_name( self, name ) -> None:
        pass


    @property
    def output_path( self ) -> str:
        if not self._output_path:
            self._output_path = RLGDefaults.output_path
        return self._output_path


    @output_path.setter
    def output_path( self, path: str ) -> None:

        if path is None:
            return

        path = Path( path ).resolve()
        self._validate_file_path( path )
        self._output_path = str( path )


    @property
    def json_path( self ) -> str:
        return '%s.json' % str( Path( self.output_path, self.site_id.lower() ) )


    @property
    def image_path( self ) -> str:
        image_dir = self.cache.get( RadarCacheKeys.IMAGE_PATH, self.site_id.lower() )
        image_path =  Path( image_dir )
        if not image_path.is_absolute():
            image_path = Path( self.output_path, image_path )
        return str( image_path )


    @image_path.setter
    def image_path( self, path: str ) -> None:

        if path is None:
            return

        path = Path( path )
        self._validate_file_path( path )
        self.cache.set( RadarCacheKeys.IMAGE_PATH, str( path ) )


    @property
    def image_file_path_name( self ) -> str:
        image_file_path = Path( self.image_path, self.file_name )
        return str( image_file_path )


    @property
    def axes( self ) -> pyplot.Axes:
        return self._axes


    @axes.setter
    def axes( self, axes ) -> None:
        self._axes = axes


    @property
    def figure( self ) -> pyplot.Figure:
        return self._figure


    @figure.setter
    def figure( self, figure ) -> None:
        self._figure = figure


    def dump( self, message: str, _logger: logger ) -> None:

        self._check_site_coords()
        self._check_image_bounds()

        _logger( message + "\n"
            "\tSite:        {site_id}       \n"
            "\tSite Coords: {site_coords}   \n"
            "\tRadius:      {radius}        \n"
            "\tBBox:        {image_bbox}    \n"
            "\tEnvelope:    {image_envelope}\n"
            "\tOutput Root: {output_path}   \n"
            "\tJSON Path:   {json_path}     \n"
            "\tImage Path:  {image_path}/   \n",

            site_id        = self.site_id,
            site_coords    = self.site_coords,
            radius         = self.radius,
            image_bbox     = self.image_bbox,
            image_envelope = self.image_envelope,
            output_path    = self.output_path,
            json_path      = self.json_path,
            image_path     = self.image_path
        )


    def generate( self ) -> None:

        self._check_site_coords()
        self._check_image_bounds()

        path = Path( self.output_path )
        path.mkdir( parents=True, exist_ok=True )

        self.cache.dump()


    def save_image( self, **kwargs ) -> None:
        path = Path( self.image_path )
        path.mkdir( parents=True, exist_ok=True )

        figure = kwargs.pop( 'figure' ) if 'figure' in kwargs else self.figure
        file_path_name = kwargs.pop( 'file' ) if 'file' in kwargs else self.image_file_path_name
        figure.savefig( file_path_name, bbox_inches='tight', pad_inches=0, **kwargs )


    def make_figure( self ) -> None:

        self.figure, self.axes = pyplot.subplots( figsize=( 16, 16 ), subplot_kw=dict( projection=self.crs ) )

        # Don't draw borders
        for spine in self.axes.spines:
            self.axes.spines[spine].set_visible( False )


    @classmethod
    def _validate_site_id( cls, site_id: str ) -> None:

        if not site_id:
            raise RLGValueError( 'The site ID is not set' )

        if re.fullmatch( r'^[KPRT][A-Z]{3}$', site_id, re.IGNORECASE ) is None:
            raise RLGValueError( f"The site ID '{site_id}' does not match expected format" )

    @classmethod
    def _validate_radius( cls, radius: int ) -> None:
        if not isinstance( radius, int ) or radius < 1 or radius > 500:
            raise RLGValueError( 'The radius must be an integer between 1 and 500 miles' )


    @classmethod
    def _validate_file_path( cls, path: str | Path ) -> None:

        if not ( isinstance( path, str ) or isinstance( path, Path ) ):
            raise RLGValueError( 'The file path must be a string representing a relative or absolute filesystem directory' )

        if Path( path ).exists() and not Path( path ).is_dir():
            raise RLGValueError( 'The file path provided exists, but it is not a directory' )


    r'''
    ### This method is sooooooo slooooooow, and I'm not sure why ¯\_(ツ)_/¯
    @classmethod
    def _verify_site_id( cls, site_id: str ):

        cls._validate_site_id( site_id )

        logger.info( f"Checking to see if {site_id.upper()} is valid..." )

        request = DataAccessLayer.newDataRequest( 'radar' )
        locations = DataAccessLayer.getAvailableLocationNames( request )

        if site_id not in locations:
            raise RLGValueError( f"The site ID '{site_id}' is not a valid radar site" )

        logger.info( '...done' )
    '''


    def _check_site_coords( self ) -> None:

        if self.site_coords:
            return

        logger.info( "Retrieving coordinates for {}...", self.site_id )

        request = DataAccessLayer.newDataRequest( 'obs', parameters=[ 'longitude', 'latitude' ], locationNames=[ self.site_id ] )
        response = DataAccessLayer.getGeometryData( request, None )

        if not response:
            raise RLGRuntimeError( f"Empty response while requesting coordinates for site {self.site_id}" )

        data = response[0]

        self.site_coords = ( data.getNumber( 'latitude' ), data.getNumber( 'longitude' ) )

        logger.info( '...done' )


    def _check_image_bounds( self ) -> None:

        if not self.radius:
            raise RLGRuntimeError( 'Radius not specified' )

        if self.image_bbox and self.image_envelope:
            return

        logger.info( "Calculating image bounds for {}...", self.site_id )

        bbox_calc = BoundingBoxCalculator( self.site_coords, self.radius )
        self.image_bbox = bbox_calc.get_bbox()
        self.image_envelope = sgeo.mapping( bbox_calc.get_polygon() )

        logger.info( f"...done.  Bounds for {self.site_id} at {self.radius} miles: {self.image_bbox}" )
