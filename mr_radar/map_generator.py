# coding: utf-8

import numpy as np
from cartopy.feature import ShapelyFeature, NaturalEarthFeature
from shapely.ops import unary_union
from radar_loop_generator import *


class MapGenerator( RadarLoopGenerator ):

    def __init__( self ):
        self.COUNTY_BOUNDS = []
        self.ENVELOPE =  None
        super().__init__()


    def set_file_path( self, path: str='', name: str='' ):

        super().set_file_path( path, ( name or self.SITE_ID ) )
        
        logger.info( "→ Map file will be saved as '{}'", self.FILE_PATH )


    def generate( self ):
        logger.info( 'Generating map...' )

        super().generate()

        self._generate_base()
        self._generate_topography()
        self._generate_highways()
        self._generate_lakes()
        self._generate_rivers()
        self._generate_cities()

        super().save_image()

        logger.info( '...map saved' )


    def _generate_base( self ):
        logger.info( 'Generating layer 1 of 6: base map...' )

        identifier = self.SITE_ID[len( self.SITE_ID ) - 3:].upper()

        request = DataAccessLayer.newDataRequest( 'maps' )

        # Specify the necessary identifiers for requesting the San Angelo CWA
        request.addIdentifier( 'table', 'mapdata.county' )
        request.setLocationNames( identifier )
        request.addIdentifier( 'cwa', identifier )

        # enable location filtering (inLocation)
        # locationField is tied to the above cwa definition (SJT)
        request.addIdentifier( 'geomField', 'the_geom' )
        request.addIdentifier( 'inLocation', 'true' )
        request.addIdentifier( 'locationField', 'cwa' )

        # Get response and create dict of county geometries
        response = DataAccessLayer.getGeometryData( request )
        counties = []
        for county in response:
            counties.append( county.getGeometry() )

        logger.info( "Using %d county MultiPolygons" % len( counties ) )

        # All WFO counties merged to a single Polygon
        merged_counties = unary_union( counties )
        self.ENVELOPE = merged_counties.buffer( 2 )
        self.COUNTY_BOUNDS = merged_counties.bounds

        # Create the map based on the boundaries of the CWA
        self._make_image()

        self.AXES.coastlines( resolution='50m' )

        # Plot country boundaries handled by Cartopy
        political_boundaries = NaturalEarthFeature(
            category='cultural', name='admin_0_boundary_lines_land', scale='50m', facecolor='none'
        )
        self.AXES.add_feature( political_boundaries, linestyle='-', edgecolor='black' )
        logger.info( ' • added country borders' )

        # Plot state boundaries handled by Cartopy
        state_boundaries = NaturalEarthFeature(
            category='cultural', name='admin_1_states_provinces_lines', scale='50m', facecolor='none'
        )
        self.AXES.add_feature( state_boundaries, linestyle='-', edgecolor='black' )
        logger.info( ' • added state borders' )

        # Plot CWA counties
        county_boundaries = ShapelyFeature(
            counties, ccrs.PlateCarree(), facecolor='none', linestyle='-', edgecolor='#86989B'
        )
        self.AXES.add_feature( county_boundaries )
        logger.info( ' • added county borders' )

        logger.info( '...done' )


    def _generate_topography( self ):
        logger.info( 'Generating layer 2 of 6: topography...' )

        # Define request for topography
        request = DataAccessLayer.newDataRequest( 'topo', envelope=self.BOUNDING_POLYGON )
        request.addIdentifier( 'group', '/' )
        request.addIdentifier( 'dataset', 'full' )

        # Get topography
        grid_data = DataAccessLayer.getGridData( request )
        grid = grid_data[0]

        # print( "Number of grid records: %d" % len( gridData ) )
        # print( "Sample grid data shape:\n%s\n" % str( grid.getRawData().shape ) )
        # print( "Sample grid data:\n%s\n" % str( grid.getRawData() ) )

        topo = np.ma.masked_invalid( grid.getRawData() )
        lons, lats = grid.getLatLonCoords()

        # Add topography (with 90% transparency so that it's not so bold)
        self.AXES.contourf( lons, lats, topo, 80, cmap=plt.get_cmap( 'terrain' ), alpha=0.1, extend='both' )

        logger.info( '...done' )


    def _generate_highways( self ):
        logger.info( 'Generating layer 3 of 6: major highways...' )

        # Define the request for the interstate highways
        request = DataAccessLayer.newDataRequest( 'maps', envelope=self.ENVELOPE )
        request.addIdentifier( 'table', 'mapdata.interstate' )
        request.addIdentifier( 'geomField', 'the_geom' )

        # Get interstate highway geometries
        interstates = DataAccessLayer.getGeometryData( request )
        logger.info( "\tUsing %d interstate MultiLineStrings" % len( interstates ) )

        # Plot interstate highways
        for highway in interstates:
            shape_feature = ShapelyFeature( highway.getGeometry(), ccrs.PlateCarree(), facecolor='none', linestyle='-', edgecolor='orange' )
            self.AXES.add_feature( shape_feature )

        logger.info( '...done' )


    def _generate_lakes( self ):
        logger.info( 'Generating layer 4 of 6: lakes...' )

        # Define request for lakes
        request = DataAccessLayer.newDataRequest( 'maps', envelope=self.ENVELOPE )
        request.addIdentifier( 'table', 'mapdata.lake' )
        request.addIdentifier( 'geomField', 'the_geom' )

        # Get lake geometries
        lakes = DataAccessLayer.getGeometryData( request )
        logger.info( "\tUsing %d lake MultiPolygons" % len( lakes ) )

        # Plot lakes
        shape_feature = ShapelyFeature( [ lake.getGeometry() for lake in lakes ], ccrs.PlateCarree(), facecolor='blue', linestyle='-', edgecolor='#20B2AA', alpha=0.25 )
        self.AXES.add_feature( shape_feature )

        logger.info( '...done' )


    def _generate_rivers( self ):
        logger.info( 'Generating layer 5 of 6: major rivers...' )

        # Define request for rivers
        request = DataAccessLayer.newDataRequest( 'maps', envelope=self.ENVELOPE )
        request.addIdentifier( 'table', 'mapdata.majorrivers' )
        request.addIdentifier( 'geomField', 'the_geom' )

        # Get river geometries
        rivers = DataAccessLayer.getGeometryData( request )
        logger.info( "\tUsing %d river MultiLineStrings" % len( rivers ) )

        # Plot rivers
        shape_feature = ShapelyFeature( [ river.getGeometry() for river in rivers ], ccrs.PlateCarree(), facecolor='none', linestyle=":", edgecolor='#20B2AA', alpha=0.25 )
        self.AXES.add_feature( shape_feature )

        logger.info( '...done' )


    def _generate_cities( self ):
        logger.info( 'Generating layer 6 of 6: cities...' )

        # Define the request for the cities
        request = DataAccessLayer.newDataRequest( 'maps', envelope=self.ENVELOPE )
        request.addIdentifier( 'table', 'mapdata.city' )
        request.addIdentifier( 'geomField', 'the_geom' )
        request.setParameters( 'name', 'population', 'prog_disc', 'lat', 'lon' )

        # Get city geometries
        cities = DataAccessLayer.getGeometryData( request )
        logger.info( "\tQueried %d total cities" % len( cities ) )

        # Set aside two arrays - one for the geometry of the cities and one for their names
        city_coords = []
        city_names = []

        # `bounds` is the area around the counties in the CWA
        lon_min, lat_min, lon_max, lat_max = self.COUNTY_BOUNDS

        for city in cities:
            # Ignore cities outside the CWA
            if lat_min <= city.getNumber( 'lat' ) <= lat_max and lon_min <= city.getNumber( 'lon' ) <= lon_max:
                if city.getString( 'population' ) != 'None':
                    if city.getNumber( 'prog_disc' ) > 5000 and int( city.getString( 'population' ) ) > 5000:
                        city_coords.append( city.getGeometry() )
                        city_names.append( city.getString( 'name' ) )

        logger.info( "\tPlotting %d cities" % len( city_names ) )

        # Plot city markers
        self.AXES.scatter( [point.x for point in city_coords], [point.y for point in city_coords], transform=ccrs.PlateCarree(), marker='.', facecolor='black' )

        # Plot city names
        for i, name in enumerate( city_names ):
            self.AXES.annotate( name, (city_coords[i].x, city_coords[i].y), xytext=(3, 3), textcoords='offset points', transform=ccrs.PlateCarree() )

        logger.info( '...done' )
