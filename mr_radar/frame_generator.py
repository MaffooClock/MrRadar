# coding: utf-8

import numpy as np
from matplotlib import colors
from matplotlib.cm import ScalarMappable
from radar_loop_generator import *


class FrameGenerator( RadarLoopGenerator ):

    def __init__( self ):
        self.FRAMES = 0
        super().__init__()


    def set_file_path( self, path: str='', name: str='' ):

        super().set_file_path( path, (f"{name}_%d" if name else 'frame_%d') )
        
        logger.info( "→ Image frames will be saved as '{}'", self.FILE_PATH )


    def set_frames( self, quantity: int ):

        if not quantity:
            raise ValueError( 'The quantity of frames to generate must be an integer of 1 or greater' )

        self.FRAMES = quantity


    def generate( self ):
        logger.info( 'Generating NEXRAD image frames...' )

        super().generate()

        response = self._fetch_data()

        if not response:
            raise RuntimeError( 'No NEXRAD data returned; aborting.' )

        self._process_data( response )


    def _fetch_data( self ):

        logger.info( 'Preparing to build NEXRAD images...' )

        request = DataAccessLayer.newDataRequest( 'radar', envelope=self.BOUNDING_POLYGON )
        request.setLocationNames( self.SITE_ID )
        request.setParameters( 'Composite Refl' )

        available_levels = DataAccessLayer.getAvailableLevels( request )

        if available_levels:
            request.setLevels( available_levels[0] )

        times = DataAccessLayer.getAvailableTimes( request, True )
        logger.info( '...done.' )

        # Get the latest images
        logger.info( "Fetching latest {} NEXRAD images...", self.FRAMES )
        response = DataAccessLayer.getGridData( request, times[-self.FRAMES:] )
        logger.info( '...done.' )

        return response


    def _process_data( self, response ):

        if not self.FRAMES:
            raise ValueError( 'The quantity of frames to generate has not been set' )

        cmap = plt.get_cmap( 'rainbow' )

        dbz_min = None
        dbz_max = None

        logger.info( 'Processing images...' )
        for i, grid in enumerate( response ):

            logger.info( "    #{}...", ( i + 1 ) )

            lons, lats = grid.getLatLonCoords()
            data = grid.getRawData()

            flat = np.ndarray.flatten( data )
            _min = np.nanmin( flat )
            _max = np.nanmax( flat )

            if dbz_min is None or _min < dbz_min:
                dbz_min = _min

            if dbz_max is None or _max > dbz_max:
                dbz_max = _max

            self._make_image()

            self.AXES.pcolormesh( lons, lats, data, cmap=cmap, alpha=0.75 )

            # Add the timestamp and product name at the bottom-center
            text_x = ( self.AXES.viewLim.x0 + self.AXES.viewLim.x1 ) / 2.0
            text_y = self.AXES.viewLim.y0 * 1.0025
            self.AXES.text( text_x, text_y, "%s - %s" % ( grid.getParameter(), str( grid.getDataTime().getRefTime() ) ), transform=ccrs.PlateCarree(), ha='center', size='small' )

            file_path = ( self.FILE_PATH % i )
            super().save_image( file_path )

            logger.info( "    {} saved", Path( file_path ).name )

        logger.info( 'Generating dBZ legend...' )

        norm = colors.Normalize( vmin=dbz_min, vmax=dbz_max )

        fig, ax = plt.subplots( figsize=( 16, 0.1 ) )
        fig.colorbar( ScalarMappable( norm=norm, cmap=cmap ), cax=ax, orientation='horizontal', label='dBZ' )
        fig.savefig( self.FILE_PATH.replace( '%d', '%s' ) % 'legend', transparent=True, bbox_inches='tight', pad_inches=0 )

        logger.info( '...all done!' )
