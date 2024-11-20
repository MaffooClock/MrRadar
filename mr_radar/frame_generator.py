# coding: utf-8

from __future__ import annotations

import re
from pathlib import Path

from loguru import logger
from matplotlib import pyplot
from matplotlib.cm import ScalarMappable
from metpy.plots import ctables
from awips.dataaccess import IGridData, DataAccessLayer

from cache_keys import RadarCacheKeys
from radar_loop_generator import RadarLoopGenerator
from rlg_exception import *


NORM, CMAP = ctables.registry.get_with_steps( 'NWSStormClearReflectivity', -20, 0.5 )

PNG_METADATA = {
    'Creation Time' : '',
    'Description'   : '',
    'Software'      : 'MrRadar, https://github.com/MaffooClock/MrRadar',
    'Source'        : 'NWS via Unidata AWIPS',
    'Copyright'     : 'Public Domain'
}

class FrameGenerator( RadarLoopGenerator ):

    def __init__( self, site_id: str, radius: int=None, path: str=None, name: str=None, frames: int=None ) -> None:
        super().__init__( site_id, radius, path )
        self.frames = frames
        self.file_name = ( name or 'frame' )
        logger.info( "→ Image frames will be saved as '{}'", self.file_path_name )


    @property
    def file_name( self ) -> str:
        return self.cache.get( RadarCacheKeys.FILE_NAME )


    @file_name.setter
    def file_name( self, name: str ) -> None:
        self.cache.set( RadarCacheKeys.FILE_NAME, f"{name}_%d.png" )


    @property
    def frames( self ) -> int:
        return self.cache.get( RadarCacheKeys.FRAMES, 12 )


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
        logger.info( 'Generating NEXRAD image frames...' )

        super().generate()

        response = self._fetch_data()

        if not response:
            raise RLGRuntimeError( 'No NEXRAD data returned; aborting.' )

        self._process_data( response )
        self._cleanup()


    def save_image( self, index: int, metadata: dict ) -> str:

        file_path_name = self.file_path_name % index

        super().save_image( file=file_path_name, transparent=True, metadata=metadata )

        return Path( file_path_name ).name


    def _fetch_data( self ) -> []:

        logger.info( 'Preparing to build NEXRAD images...' )

        request = DataAccessLayer.newDataRequest( 'radar', envelope=self.image_envelope )
        request.setLocationNames( self.site_id )
        request.setParameters( 'HZ' )   # Super Res Reflectivity
        # request.setParameters( 'CZ' ) # Composite Ref
        # request.setParameters( 'Reflectivity' )
        # request.setParameters( 'Composite Refl' )

        ###
        # available_params = DataAccessLayer.getAvailableParameters( request )
        # available_params.sort()
        # print( available_params )
        # return None

        available_levels = DataAccessLayer.getAvailableLevels( request )

        if available_levels:
            request.setLevels( available_levels[0] )

        times = DataAccessLayer.getAvailableTimes( request, True )
        logger.info( '...done.' )

        # Get the latest images
        logger.info( "Fetching latest {} NEXRAD images...", self.frames )
        response = DataAccessLayer.getGridData( request, times[-self.frames:] )
        logger.info( '...done.' )

        return response


    def _process_data( self, response: [] ) -> None:

        if not self.frames:
            raise RLGValueError( 'The quantity of frames to generate has not been set' )

        logger.info( 'Processing images...' )
        for i, grid in enumerate( response ):
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

        values = ( self.site_id.upper(), grid.getParameter(), grid.getLevel() or 'N/A' )
        frame_label = ( "%s (%s %s)" % values ).replace( ' N/A', '' )

        # Add the timestamp and product name at the bottom-center
        self.axes.text(
            text_x, text_y, "%s - %s" % ( frame_label, date_time ),
            transform=self.crs, ha='center', size='small'
        )

        PNG_METADATA['Creation Time'] = date_time
        PNG_METADATA['Description'] = "Site: %s, Product: %s, Level: %s" % values

        file_name = self.save_image( i, PNG_METADATA )

        logger.info( "    Saved {}", file_name )


    def _generate_legend( self ) -> None:

        legend_file = self.file_path_name.replace( '%d', '%s' ) % 'legend'

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
        for frame in Path( self.file_path ).glob( file_name_glob ):
            if re.match( file_name_pattern, frame.name ):
                frame_count += 1

        if self.frames >= frame_count:
            return

        logger.info( "Needed: %d, Have: %d" % ( self.frames, frame_count ) )

        start = self.frames
        stop = frame_count
        for i in range( start, stop ):
            Path( self.file_path_name % i ).unlink()

        logger.info( "→ Deleted {} extra frames", stop - start )
