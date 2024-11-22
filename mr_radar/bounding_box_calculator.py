## -*- coding: utf-8 -*-

from __future__ import annotations

from geopy.distance import geodesic
import shapely.geometry as sgeo


class BoundingBoxCalculator:

    def __init__( self, center_point: ( float, float ), radius_miles: int ) -> None:
        self._radius_miles = None

        self.center_point = center_point
        self.radius_miles = radius_miles


    @property
    def radius_miles( self ) -> int:
        return self._radius_miles


    @radius_miles.setter
    def radius_miles( self, radius_miles: int | float ) -> None:

        if not ( isinstance( radius_miles, int ) or isinstance( radius_miles, float ) ) or radius_miles <= 0:
            raise TypeError( 'The radius must be an integer greater than zero' )

        self._radius_miles = radius_miles


    def get_bbox( self ) -> [ float, float, float, float ]:
        """Calculates bounding box coordinates for the given radius and center point"""

        latitudes = []
        longitudes = []

        for bearing in [ 0, 90, 180, 270 ]:
            # Calculate the destination point using the given distance and bearing
            destination = geodesic( miles=self.radius_miles ).destination( self.center_point, bearing )

            latitudes.append( destination.latitude )
            longitudes.append( destination.longitude )

        coords = [
            min( longitudes ), # West
            min( latitudes ),  # South
            max( longitudes ), # East
            max( latitudes )   # North
        ]

        return coords


    def get_polygon( self ) -> sgeo.Polygon:
        """Converts bounding box to Polygon object"""
        return sgeo.box( *self.get_bbox() )
