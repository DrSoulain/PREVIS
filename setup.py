#!/usr/bin/env python

from setuptools import setup
project_name = "previs"                                                                                         
                                                                                                                  
setup(                                                                                                            
    name=project_name,                                                                                            
    version=__import__(project_name).__version__,
    packages=['previs'],
    author='Anthony Soulain',
    author_email='anthony.soulain@sydney.edu.au.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Professional Astronomers',
        'Topic :: High Angular Resolution Astronomy :: Interferometry',
        'Programming Language :: Python :: 3.7'
    ],
    package_data={'previs': ['data/eso_limits_matisse.json']},
)
