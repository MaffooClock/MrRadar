# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='MrRadar',
    version='0.1.0',
    description='A Python utility for generating map and NEXRAD imagery files for use in an animated loop',
    long_description=readme,
    author='Matthew Clark',
    url='https://github.com/MaffooClock/MrRadar',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)