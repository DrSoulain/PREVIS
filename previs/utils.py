# -*- coding: utf-8 -*-
"""
@author: Anthony Soulain (University of Sydney)

--------------------------------------------------------------------
PREVIS: Python Request Engine for Virtual Interferometric Survey
--------------------------------------------------------------------

This file contains general function.
"""

import time


def printtime(n, start_time):
    t = time.time() - start_time
    t0 = time.time()
    m = t//60
    print("==> %s (%d min %2.3f s)" % (n, m, t-m*60))
    return t0
