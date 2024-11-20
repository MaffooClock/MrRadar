# coding: utf-8

from __future__ import annotations

from loguru import logger
import numpy as np
from awips.dataaccess import DataAccessLayer
from matplotlib import pyplot
from cartopy.feature import ShapelyFeature, NaturalEarthFeature

from cache_keys import RadarCacheKeys
from radar_loop_generator import RadarLoopGenerator


# See https://www.naturalearthdata.com/
SCALE = dict(
    large  = '10m',  # Most detailed
    medium = '50m',  # Moderate detail
    small  = '110m', # Coarse detail
)

# See https://www.naturalearthdata.com/downloads/50m-cultural-vectors/
COUNTRY_BORDERS = 'admin_0_boundary_lines_land'
STATE_BORDERS   = 'admin_1_states_provinces_lines'


class MapGenerator( RadarLoopGenerator ):

    def __init__( self, site_id: str, radius: int=None, path: str=None, name: str=None, **kwargs ) -> None:
        super().__init__( site_id, radius, path )
        self.file_name = ( name or 'map' )
        logger.info( "→ Map file will be saved as '{}'", self.file_path_name )


    @property
    def file_name( self ) -> str:
        return self.cache.get( RadarCacheKeys.FILE_NAME )


    @file_name.setter
    def file_name( self, name: str ) -> None:
        self.cache.set( RadarCacheKeys.FILE_NAME, f"{name}.png" )


    def generate( self ) -> None:
        logger.info( 'Generating map...' )

        super().generate()

        self.make_figure()

        self._generate_topography()
        self._generate_borders()
        self._generate_highways()
        self._generate_lakes()
        self._generate_rivers()
        self._generate_cities()

        self.save_image()


    def save_image( self ) -> None:
        super().save_image()
        logger.info( '...map saved' )


    def _generate_topography( self ) -> None:
        logger.info( 'Generating layer 1 of 6: topography...' )

        # Define request for topography
        request = DataAccessLayer.newDataRequest( 'topo', envelope=self.image_envelope )
        request.addIdentifier( 'group', '/' )
        request.addIdentifier( 'dataset', 'full' )

        # Get topography
        grid_data = DataAccessLayer.getGridData( request )
        grid = grid_data[0]

        topo = np.ma.masked_invalid( grid.getRawData() )
        lons, lats = grid.getLatLonCoords()

        # Add topography (with 90% transparency so that it's not so bold)
        self.axes.contourf( lons, lats, topo, 80, cmap=pyplot.get_cmap( 'terrain' ), alpha=0.1, extend='both' )

        logger.info( '...done' )


    def _generate_borders( self ) -> None:
        logger.info( 'Generating layer 2 of 6: borders...' )

        # We only need the last three characters, upper-case
        identifier = self.site_id[len( self.site_id ) - 3:].upper()

        request = DataAccessLayer.newDataRequest( 'maps', locationNames=[identifier], envelope=self.image_envelope )

        # Specify the necessary identifiers for requesting the CWA for a given site
        request.addIdentifier( 'table', 'mapdata.county' )
        request.addIdentifier( 'geomField', 'the_geom' )

        # Get response and create list of county geometries
        response = DataAccessLayer.getGeometryData( request, None )
        all_counties = []
        for county in response:
            all_counties.append( county.getGeometry() )

        # Request counties again, but filter down to CWA counties only
        request.addIdentifier( 'cwa', identifier )
        request.addIdentifier( 'inLocation', 'true' )
        request.addIdentifier( 'locationField', 'cwa' )

        # Get response and create list of CWA geometries
        response = DataAccessLayer.getGeometryData( request, None )
        cwa_counties = []
        for county in response:
            cwa_counties.append( county.getGeometry() )

        self.axes.coastlines( resolution=SCALE['medium'] )

        # Plot country boundaries handled by Cartopy
        country_boundaries = NaturalEarthFeature( category='cultural', name=COUNTRY_BORDERS, scale=SCALE['medium'], facecolor='none' )
        self.axes.add_feature( country_boundaries, linestyle='-', edgecolor='black' )
        logger.info( ' • added country borders' )

        # Plot state boundaries handled by Cartopy
        state_boundaries = NaturalEarthFeature( category='cultural', name=STATE_BORDERS, scale=SCALE['medium'], facecolor='none' )
        self.axes.add_feature( state_boundaries, linestyle='-', edgecolor='black' )
        logger.info( ' • added state borders' )

        # Plot CWA counties
        county_boundaries = ShapelyFeature( all_counties, self.crs, facecolor='none', linestyle='-', edgecolor='#CCCCCC' )
        self.axes.add_feature( county_boundaries )
        logger.info( ' • added {} county borders', len( all_counties ) )

        # Plot CWA counties
        cwa_boundaries = ShapelyFeature( cwa_counties, self.crs, facecolor='none', linestyle='-', edgecolor='#C4887C' )
        self.axes.add_feature( cwa_boundaries )
        logger.info( ' • highlighted {} CWA borders', len( cwa_counties ) )

        logger.info( '...done' )


    def _generate_highways( self ) -> None:
        logger.info( 'Generating layer 3 of 6: major highways...' )

        # Define the request for the interstate highways
        request = DataAccessLayer.newDataRequest( 'maps', envelope=self.image_envelope )
        request.addIdentifier( 'table', 'mapdata.interstate' )
        request.addIdentifier( 'geomField', 'the_geom' )

        # Get interstate highway geometries
        interstates = DataAccessLayer.getGeometryData( request, None )
        logger.info( "\tUsing %d interstate MultiLineStrings" % len( interstates ) )

        # Plot interstate highways
        for highway in interstates:
            shape_feature = ShapelyFeature( highway.getGeometry(), self.crs, facecolor='none', linestyle='-', edgecolor='orange' )
            self.axes.add_feature( shape_feature )

        logger.info( '...done' )


    def _generate_lakes( self ) -> None:
        logger.info( 'Generating layer 4 of 6: lakes...' )

        # Define request for lakes
        request = DataAccessLayer.newDataRequest( 'maps', envelope=self.image_envelope )
        request.addIdentifier( 'table', 'mapdata.lake' )
        request.addIdentifier( 'geomField', 'the_geom' )

        # Get lake geometries
        lakes = DataAccessLayer.getGeometryData( request, None )
        logger.info( "\tUsing %d lake MultiPolygons" % len( lakes ) )

        # Plot lakes
        shape_feature = ShapelyFeature( [ lake.getGeometry() for lake in lakes ], self.crs, facecolor='blue', linestyle='-', edgecolor='#20B2AA', alpha=0.25 )
        self.axes.add_feature( shape_feature )

        logger.info( '...done' )


    def _generate_rivers( self ) -> None:
        logger.info( 'Generating layer 5 of 6: major rivers...' )

        # Define request for rivers
        request = DataAccessLayer.newDataRequest( 'maps', envelope=self.image_envelope )
        request.addIdentifier( 'table', 'mapdata.majorrivers' )
        request.addIdentifier( 'geomField', 'the_geom' )

        # Get river geometries
        rivers = DataAccessLayer.getGeometryData( request, None )
        logger.info( "\tUsing %d river MultiLineStrings" % len( rivers ) )

        # Plot rivers
        shape_feature = ShapelyFeature( [ river.getGeometry() for river in rivers ], self.crs, facecolor='none', linestyle=":", edgecolor='#20B2AA', alpha=0.25 )
        self.axes.add_feature( shape_feature )

        logger.info( '...done' )


    def _generate_cities( self ) -> None:
        logger.info( 'Generating layer 6 of 6: cities...' )

        # Define the request for the cities
        request = DataAccessLayer.newDataRequest( 'maps', parameters=[ 'name', 'population', 'prog_disc', 'lat', 'lon' ], envelope=self.image_envelope.buffer( -0.5 ) )
        request.addIdentifier( 'table', 'mapdata.city' )
        request.addIdentifier( 'geomField', 'the_geom' )

        # Get city geometries
        cities = DataAccessLayer.getGeometryData( request, None )
        logger.info( "\tQueried %d total cities" % len( cities ) )

        # Set aside two arrays - one for the geometry of the cities and one for their names
        city_coords = []
        city_names = []

        for city in cities:
            if city.getString( 'population' ) != 'None':
                if city.getNumber( 'prog_disc' ) > 8000 and int( city.getString( 'population' ) ) > 5000:
                    city_coords.append( city.getGeometry() )
                    city_names.append( city.getString( 'name' ) )

        logger.info( "\tPlotting %d cities" % len( city_names ) )

        # Plot city markers
        self.axes.scatter( [point.x for point in city_coords], [point.y for point in city_coords], transform=self.crs, marker='.', facecolor='black' )

        # Plot city names
        for i, name in enumerate( city_names ):
            self.axes.annotate( name, ( city_coords[i].x, city_coords[i].y ), xytext=( 3, -8 ), textcoords='offset points', transform=self.crs )

        logger.info( '...done' )
