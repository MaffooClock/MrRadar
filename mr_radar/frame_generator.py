## -*- coding: utf-8 -*-

from __future__ import annotations

import re
from pathlib import Path

from loguru import logger
from matplotlib import pyplot
from matplotlib.cm import ScalarMappable
from metpy.plots import ctables
from awips.dataaccess import IGridData, IDataRequest, DataAccessLayer

from .rlg_defaults import RLGDefaults
from .cache_keys import RadarCacheKeys
from .radar_loop_generator import RadarLoopGenerator
from .rlg_exception import *


NORM, CMAP = ctables.registry.get_with_steps( 'NWSStormClearReflectivity', -20, 0.5 )

PNG_METADATA = {
    'Creation Time' : '',
    'Description'   : '',
    'Software'      : 'MrRadar, https://github.com/MaffooClock/MrRadar',
    'Source'        : 'NWS via Unidata AWIPS',
    'Copyright'     : 'Public Domain'
}

class FrameGenerator( RadarLoopGenerator ):

    def __init__( self, name: str=None, product: str=None, frames: int=None, **kwargs ) -> None:
        super().__init__( **kwargs )
        self.product = product
        self.frames = frames
        self.file_name = ( name or RLGDefaults.frame_file_name )


    @property
    def file_name( self ) -> str:
        return self.cache.get( RadarCacheKeys.FILE_NAME )


    @file_name.setter
    def file_name( self, name: str ) -> None:
        file_name = self._sanitize_file_name( f"{name}_%d" )
        self.cache.set( RadarCacheKeys.FILE_NAME, file_name )


    @property
    def product( self ) -> int:
        return self.cache.get( RadarCacheKeys.PRODUCT, RLGDefaults.product )


    @product.setter
    def product( self, product: int ) -> None:

        if product is None:
            return

        self.cache.set( RadarCacheKeys.PRODUCT, product )


    @property
    def frames( self ) -> int:
        return self.cache.get( RadarCacheKeys.FRAMES, RLGDefaults.frames )


    @frames.setter
    def frames( self, quantity: int ) -> None:

        if quantity is None:
            return

        self._validate_frames( quantity )
        self.cache.set( RadarCacheKeys.FRAMES, quantity )


    @classmethod
    def _validate_frames( cls, frames: int ) -> None:
        if not isinstance( frames, int ) or frames < 1 or frames > 100:
            raise RLGValueError( 'The quantity of frames to generate must be an integer between 1 and 100' )


    def generate( self ) -> None:
        logger.info( "→ Image frames will be saved as '{}'", self.image_file_path_name )
        logger.info( 'Generating NEXRAD image frames...' )

        super().generate()

        response = self._fetch_data()

        if not response:
            raise RLGRuntimeError( 'No NEXRAD data returned; aborting.' )

        self._process_data( response )
        self._cleanup()


    def dump_products( self ) -> None:

        super().generate()

        products = self._fetch_product_list()

        if not products:
            logger.warning( "No radar products for {}", self.site_id )
            return

        logger.info( "The following {} radar products are available for {}:", len( products ), self.site_id )
        for i, product in enumerate( products ):
            index = str( i+1 ).rjust( 2 )
            print( f"\t{index}. {product}" )


    def save_image( self, index: int, metadata: dict ) -> str:

        file_path_name = self.image_file_path_name % index

        super().save_image( file=file_path_name, transparent=True, metadata=metadata )

        return Path( file_path_name ).name


    def _prepare_request( self ) -> IDataRequest:
        logger.info( 'Preparing NEXRAD data request...' )

        request = DataAccessLayer.newDataRequest( 'radar', envelope=self.image_envelope )
        request.addIdentifier( 'icao', self.site_id.lower() )

        return request


    def _fetch_product_list( self ) -> [ str ]:
        request = self._prepare_request()
        available_parameters = DataAccessLayer.getAvailableParameters( request )
        return DataAccessLayer.getRadarProductNames( available_parameters )


    def _fetch_data( self ) -> [ IGridData ]:

        request = self._prepare_request()

        request.setParameters( self.product )
        logger.info( "→ Product: {}", self.product )

        available_levels = DataAccessLayer.getAvailableLevels( request )
        logger.info( "→ Available levels: {}", len( available_levels ) )

        if available_levels:
            level = available_levels[0]
            request.setLevels( level )
            logger.info( "    ...using {}", level )

        logger.info( '→ Fetching available times...' )
        times = DataAccessLayer.getAvailableTimes( request, True )
        logger.info( "    ...got {}, but we only need {}", len( times ), self.frames )

        logger.info( '...done.' )

        # Get the latest images
        logger.info( "Fetching latest {} NEXRAD images...", self.frames )
        response = DataAccessLayer.getGridData( request, times[-self.frames:] )
        logger.info( '...done.' )

        return response


    def _process_data( self, response: [ IGridData ] ) -> None:

        if not self.frames:
            raise RLGValueError( 'The quantity of frames to generate has not been set' )

        logger.info( 'Processing images...' )

        # The response list is in order from oldest to newest, so we
        # should iterate backwards to make `frame_0.png` the latest
        for i, grid in enumerate( response[::-1] ):
            self._process_frame( i, grid )

        self._generate_legend()

        logger.info( '...done!' )


    def _process_frame( self, i: int, grid: IGridData ) -> None:

        lons, lats = grid.getLatLonCoords()
        data = grid.getRawData()

        self.make_figure()

        self.axes.pcolormesh( lons, lats, data, cmap=CMAP, norm=NORM, alpha=0.75 )

        text_x = ( self.axes.viewLim.x0 + self.axes.viewLim.x1 ) / 2.0
        text_y = self.axes.viewLim.y0 * 1.0025
        date_time = f"%s GMT" % str( grid.getDataTime().getRefTime() )

        values = ( self.site_id, grid.getParameter(), grid.getLevel() or 'N/A' )
        frame_label = ( "%s (%s %s)" % values ).replace( ' N/A', '' )

        # Add the timestamp and product name at the bottom-center
        self.axes.text(
            text_x, text_y, "%s - %s" % ( frame_label, date_time ),
            transform=self.crs, ha='center', size='small'
        )

        PNG_METADATA['Creation Time'] = date_time
        PNG_METADATA['Description'] = "Site: %s, Product: %s, Level: %s" % values

        file_name = self.save_image( i, PNG_METADATA )

        logger.info( "→ Saved {}", file_name )


    def _generate_legend( self ) -> None:

        legend_file = self.image_file_path_name.replace( '%d', '%s' ) % 'legend'

        if Path( legend_file ).exists():
            return

        logger.info( 'Generating dBZ legend...' )

        fig, ax = pyplot.subplots( figsize=( 16, 0.2 ) )
        fig.colorbar( ScalarMappable( norm=NORM, cmap=CMAP ), cax=ax, orientation='horizontal', label='dBZ' )
        super().save_image( file=legend_file, figure=fig, transparent=True )


    def _cleanup( self ) -> None:

        file_name_glob    = self.file_name.replace( '%d', '*' )
        file_name_pattern = self.file_name.replace( '%d', '[0-9]+' )

        frame_count = 0
        for frame in Path( self.image_path ).glob( file_name_glob ):
            if re.match( file_name_pattern, frame.name ):
                frame_count += 1

        if self.frames >= frame_count:
            return

        logger.info( "Needed: %d, Have: %d" % ( self.frames, frame_count ) )

        start = self.frames
        stop = frame_count
        for i in range( start, stop ):
            Path( self.image_file_path_name % i ).unlink()

        logger.info( "→ Deleted {} extra frames", stop - start )
