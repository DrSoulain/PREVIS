# -*- coding: utf-8 -*-
"""
@author: Anthony Soulain (University of Sydney)

--------------------------------------------------------------------
PREVIS: Python Request Engine for Virtual Interferometric Survey
--------------------------------------------------------------------

This file contains general function.
"""

import time
import os
from termcolor import colored

# on windows, colorama should help making termcolor compatible
try:
    import colorama
    colorama.init()
except ImportError:
    if os.name == 'nt':  # Windows plateform detected
        print("Warning: in Windows, some prints might not work properly. Install colorama to fix this.")

def printtime(n, start_time):
    t = time.time() - start_time
    t0 = time.time()
    m = t//60
    print("==> %s (%d min %2.3f s)" % (n, m, t-m*60))
    return t0

class SurveyResults(dict):
    def __repr__(self):
        res = '\n'.join([
            colored('VLTI:', 'green'),
            colored('-----', 'green'),
            'MATISSE (AT): %s' % str(self['MATISSE']['AT']['noft']['L']['LR']),
            '        (UT): %s' % str(self['MATISSE']['UT']['noft']['L']['LR']),
            'GRAVITY (AT): %s' % str(self['GRAVITY']['AT']['HR']),
            '        (UT): %s' % str(self['GRAVITY']['UT']['HR']),
            'PIONIER (AT/UT): %s' % str(self['PIONIER']),
            '',
            colored('CHARA:', 'green'),
            colored('------', 'green'),
            'VEGA: %s' % str(self['VEGA']['LR']),
            'PAVO: %s' % str(self['PAVO']),
            'MIRC: %s' % str(self['MIRC']['H']),
            'CLIMB: %s' % str(self['CLIMB']),
            'CLASSIC: %s' % str(self['CLASSIC']['H'])
        ])
        return res
