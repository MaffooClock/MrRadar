# coding: utf-8

import numpy as np
from PIL import Image
from radar_loop_generator import *


class FrameGenerator( RadarLoopGenerator ):

    def __init__( self ):
        self.FRAMES = 0
        super().__init__()


    def set_file_path( self, path: str='', name: str='' ):

        super().set_file_path( path, (f"{name}_%d" if name else 'frame_%d') )


        with Path( self.FILE_PATH ) as p:
            path = p.parent
            name = p.name
        
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

        logger.info( "Preparing to build NEXRAD images..." )

        request = DataAccessLayer.newDataRequest( 'radar' )
        request.setLocationNames( self.SITE_ID )
        request.setParameters( 37 ) # Composite Ref (Z)

        available_levels = DataAccessLayer.getAvailableLevels( request )

        if available_levels:
            request.setLevels( available_levels[0] )

        times = DataAccessLayer.getAvailableTimes( request, True )
        logger.info( "...done." )

        # Get the latest images
        logger.info( "Fetching latest {} NEXRAD images...", self.FRAMES )
        response = DataAccessLayer.getGridData( request, times[-self.FRAMES:] )
        logger.info( '...done.' )

        return response


    def _process_data( self, response ):

        if not self.FRAMES:
            raise ValueError( 'The quantity of frames to generate has not been set' )

        # dbz_min = 0
        # dbz_max = 0

        logger.info( 'Processing images...' )
        for i, grid in enumerate( response ):

            logger.info( "    #{}...", ( i + 1 ) )

            data = grid.getRawData()
            lons, lats = grid.getLatLonCoords()

            flat = np.ndarray.flatten( data )
            _min = np.nanmin( flat )
            _max = np.nanmax( flat )

            # if _min < dbz_min:
            #     dbz_min = _min
            #
            # if _max > dbz_max:
            #     dbz_max = _max

            self._make_image()

            self.AXES.pcolormesh( lons, lats, data, cmap=plt.get_cmap( 'rainbow' ), alpha=0.65 )

            text_x = ( self.AXES.viewLim.x0 + self.AXES.viewLim.x1 ) / 2.0
            text_y = self.AXES.viewLim.y0 * 1.0025
            self.AXES.text( text_x, text_y, str( grid.getDataTime().getRefTime() ), transform=ccrs.PlateCarree(), ha='center', size='small' )

            file_path = ( self.FILE_PATH % i )
            super().save_image( file_path )

            logger.info( "    {} saved", Path( file_path ).name )

        logger.info( '...all done!' )


    ## TODO: figure out how to generate a color bar from the dbzMin/dbzMax

    #cbar = self.FIGURE.colorbar( cs, extend='both', shrink=0.25, orientation='horizontal' )
    #cbar.set_label( "%s %s (%s) %s" % ( grid.getParameter(), grid.getLevel(), grid.getUnit(),  str( grid.getDataTime().getRefTime() ) ) )

