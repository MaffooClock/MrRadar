# coding: utf-8

import warnings
import re
import inspect

from pathlib import Path

from PIL import Image
from loguru import logger
from awips.dataaccess import DataAccessLayer
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from bounding_box_calculator import BoundingBoxCalculator

# suppress a few warnings that come from plotting
warnings.filterwarnings( 'ignore', category=RuntimeWarning )
warnings.filterwarnings( 'ignore', category=UserWarning )

class RadarLoopGenerator:

    def __init__( self ):

        DataAccessLayer.changeEDEXHost( 'edex-cloud.unidata.ucar.edu' )

        self.SITE_ID = ''
        self.SITE_COORDS = ()

        self.RADIUS = 0
        self.BOUNDING_BOX = []
        self.BOUNDING_POLYGON = []
        self.ENVELOPE =  None

        self.FILE_PATH = ''

        self.FIGURE = None
        self.AXES = None


    def set_site_id( self, site_id: str ):
        self._validate_site_id( site_id )
        self.SITE_ID = site_id.lower()
        logger.info( f"→ Site ID is '{self.SITE_ID}'" )


    def set_radius( self, radius: int ):

        if not radius or radius < 1 or radius > 500:
            raise ValueError( 'The radius must be an integer between 1 and 500 miles' )

        self.RADIUS = radius

        logger.info( f"→ Radius is {self.RADIUS} miles" )


    def set_file_path( self, path: str='', name: str='' ):

        if not path:
            path = Path( Path.cwd(), 'out' )
       
        path = Path.resolve( path )

        Path.mkdir( path, parents=True, exist_ok=True )
        
        self.FILE_PATH = str( Path( path, f"%s.png" % name ) )


    def generate( self ):
        self._set_site_coordinates()
        self._set_bounds()


    def save_image( self, file_path=None ):

        # used for determining which class called this method (MapGenerator or FrameGenerator)
        prev_frame = inspect.currentframe().f_back
        calling_class = prev_frame.f_locals['self'].__class__.__name__

        if not file_path:
            file_path = self.FILE_PATH

        # Save the image as PNG (transparent for radar frames, white for others)
        self.FIGURE.savefig( file_path, transparent=( calling_class == 'FrameGenerator' ), bbox_inches='tight', pad_inches=0 )

        # Use Pillow to squash the PNG file
        with Image.open( file_path ) as image:
            image.save( file_path, compress_level=9 )


    def _make_image( self ):

        figure, axes = plt.subplots( figsize=( 16, 16 ), subplot_kw=dict( projection=ccrs.PlateCarree() ) )

        # Don't draw borders
        for spine in axes.spines:
            axes.spines[spine].set_visible( False )

        axes.set_extent( self.BOUNDING_BOX )

        self.FIGURE = figure
        self.AXES = axes


    @classmethod
    def _validate_site_id( cls, site_id: str ):

        if not site_id:
            raise ValueError( 'The site ID is not set' )

        if re.fullmatch( r'^[KPRT][A-Z]{3}$', site_id, re.IGNORECASE ) is None:
            raise ValueError( f"The site ID '{site_id}' does not match expected format" )

    r'''
    ### This method is sooooooo slooooooow, and I'm not sure why ¯\_(ツ)_/¯
    @classmethod
    def _verify_site_id( cls, site_id: str ):

        cls._validate_site_id( site_id )

        logger.info( f"Checking to see if {site_id.upper()} is valid..." )

        request = DataAccessLayer.newDataRequest( 'radar' )
        locations = DataAccessLayer.getAvailableLocationNames( request )

        if site_id not in locations:
            raise ValueError( f"The site ID '{site_id}' is not a valid radar site" )

        logger.info( '...done' )
    '''

    def _set_site_coordinates( self ):

        self._validate_site_id( self.SITE_ID )

        site_id = self.SITE_ID.upper()

        request = DataAccessLayer.newDataRequest( 'obs' )
        request.setParameters( *(['stationName', 'longitude', 'latitude']) )
        request.setLocationNames( *([site_id]) )

        response = DataAccessLayer.getGeometryData( request, None )

        if not response:
            raise RuntimeError( f"Empty response while requesting coordinates for site {site_id}" )

        data = response[0]

        self.SITE_COORDS = ( data.getNumber( 'latitude' ), data.getNumber( 'longitude' ) )

        logger.info( f"Coordinates for {site_id}: {self.SITE_COORDS}" )


    def _set_bounds( self ):

        if not self.SITE_COORDS:
            self._set_site_coordinates()

        bbox_calc = BoundingBoxCalculator( self.SITE_COORDS, self.RADIUS )
        self.BOUNDING_BOX = bbox_calc.get_bounding_coordinates()
        self.BOUNDING_POLYGON = bbox_calc.get_bounding_polygon()

        logger.info( f"Bounds for {self.SITE_ID.upper()} at {self.RADIUS} miles: {self.BOUNDING_BOX}" )
