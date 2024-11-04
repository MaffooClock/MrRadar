from geopy.distance import geodesic
from shapely.geometry import Polygon

class BoundingBoxCalculator:

    def __init__( self, center_point: (float, float), radius_miles: float ):
        self.center_point = center_point
        self.radius_miles = radius_miles


    def get_bounding_coordinates( self ):
        """Calculates bounding coordinates using geopy library."""

        latitudes = []
        longitudes = []

        for bearing in [ 0, 180, 90, 270 ]:
            # Calculate the destination point using the given distance and bearing
            destination = geodesic( miles=self.radius_miles ).destination( self.center_point, bearing )

            latitudes.append( destination.latitude )
            longitudes.append( destination.longitude )

        return [ min( longitudes ), max( longitudes ), min( latitudes ), max( latitudes ) ]


    def get_bounding_polygon( self ):
        """Converts bounding box into a Shapely Polygon object."""

        coords = self.get_bounding_coordinates()

        # Create a list of the corners for the bounding box
        polygon_points = [
            ( coords[0], coords[2] ),   # Southwest corner (lon, lat)
            ( coords[0], coords[3] ),   # Northwest corner
            ( coords[1], coords[3] ),   # Northeast corner
            ( coords[1], coords[2] ),   # Southeast corner
            ( coords[0], coords[2] )    # Closing the polygon by returning to the start
        ]
        
        return Polygon( polygon_points )
