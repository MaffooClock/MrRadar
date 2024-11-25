## -*- coding: utf-8 -*-

import argparse, sys
from pathlib import Path
from os import environ

from loguru import logger

from .rlg_exception import *


def is_dockerized():
    return environ.get( 'RLG_DOCKERIZED', False )

def main():

    parser = argparse.ArgumentParser(
        description='Generate a base map or series of NEXRAD radar frames that can be overlayed on the base map'
    )

    parser.add_argument(
        'command',
        choices=[ 'map', 'frames', 'dump-products', 'dump-vars' ],
        help='The command to specify whether to generate the base map or NEXRAD radar imagery frames, or dump a list of available radar products for the given site'
    )

    parser.add_argument(
        'site_id',
        metavar='SITE',
        help='The four-letter site ID on which to center the imagery'
    )

    parser.add_argument(
        '-r', '--radius',
        type=int,
        dest='radius',
        help='The distance in miles around the radar site to map'
    )

    output_path_default = '/data' if is_dockerized() else './out'
    parser.add_argument(
        '-D', '--root',
        type=Path,
        dest='output_path',
        help=f'The root path for all output, including JSON cache file and images.  A non-absolute path will be relative to current working directory.  Default: {output_path_default}'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        dest='image_dir',
        help=f'The destination path for the generated images.  A non-absolute path will be relative to that specified by "--root".  Default: {output_path_default}/<SITE>'
    )

    parser.add_argument(
        '-f', '--file',
        dest='name',
        help='The name of the output file.  Default is "map.png" for the map command, or "frame_<i>.png" for the frames command.'
    )

    parser.add_argument(
        '-n', '--frames',
        type=int,
        dest='frames',
        help='The number of NEXRAD radar image frames to generate. Default: 12'
    )

    parser.add_argument(
        '-p', '--product',
        type=str,
        dest='product',
        help='The radar product to use for generating NEXRAD frames.  Default: Reflectivity'
    )

    args = vars( parser.parse_args( args=None if sys.argv[2:] else ['--help'] ) )
    command = args.pop( 'command' )
    generator = None

    try:
        if command == 'dump-vars':
            from .radar_loop_generator import RadarLoopGenerator
            generator = RadarLoopGenerator( **args )
            generator.dump( 'Dumping variables:', logger.debug )
            generator = None

        elif command == 'map':
            args.pop( 'frames' )
            args.pop( 'product' )

            from .map_generator import MapGenerator
            generator = MapGenerator( **args )

        elif command in [ 'frames', 'dump-products' ]:
            from .frame_generator import FrameGenerator
            generator = FrameGenerator( **args )

            if command == 'dump-products':
                generator.dump_products()
                generator = None

        if generator:
            generator.generate()

    except RLGException as e:
        logger.error( "Image generation aborted: {}", e )

    except Exception:
        if generator:
            generator.dump( '💥 KA-BOOM! 💥', logger.error )

        raise

if __name__ == '__main__':
    main()
