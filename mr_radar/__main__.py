# coding: utf-8

import argparse
from pathlib import Path

from radar_loop_generator import RadarLoopGenerator


parser = argparse.ArgumentParser(
    description='Generate a base map or series of NEXRAD radar frames that can be overlayed on the base map'
)

parser.add_argument(
    'command',
    choices=[ 'map', 'frames' ],
    help='The command to specify whether to generate the base map or NEXRAD radar imagery frames'
)

parser.add_argument(
    '-s', '--site',
    required=True,
    help='The four-letter site ID on which to center the imagery'
)

parser.add_argument(
    '-r', '--radius',
    type=int,
    default=250,
    help='The distance in miles around the radar site to map'
)

parser.add_argument(
    '-p', '--path',
    type=Path,
    help='The destination path to the generated images.  Defaults to current working directory.'
)

parser.add_argument(
    '-f', '--file',
    help='The name of the output file.  Default is "<site>.png" for the map command, or "frame_<i>.png" for the frames command.'
)

parser.add_argument(
    '-n', '--frames',
    type=int,
    default=12,
    help="The number of NEXRAD radar image frames to generate (default: %(default)s)"
)

args = parser.parse_args()

generator = None

if args.command == 'map':
    from map_generator import MapGenerator
    generator = MapGenerator()
    generator.set_site_id( args.site )
    generator.set_radius( args.radius )
    generator.set_file_path( args.path, args.file )

elif args.command == 'frames':
    from frame_generator import FrameGenerator
    generator = FrameGenerator()
    generator.set_site_id( args.site )
    generator.set_radius( args.radius )
    generator.set_file_path( args.path, args.file )
    generator.set_frames( args.frames )

if generator:
    generator.generate()
