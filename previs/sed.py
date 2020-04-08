# -*- coding: utf-8 -*-
"""
Created on Thur Mar 26 14:49:19 2020

@author: asoulain
"""

import os
import urllib.parse
import urllib.request
import warnings

import astropy.io.votable as vo
import numpy as np
from scipy.interpolate import interp1d

warnings.filterwarnings("ignore", module='astropy.io.votable.tree')
warnings.filterwarnings("ignore", module='astropy.io.votable.xmlutil')
warnings.filterwarnings('ignore', module='scipy.interpolate.interp1d')


def getSed(coord):
    r"""
    Short Summary
    -------------

    Extract SED from Vizier database.

    Parameters.
    -----------

    `coord` : {str}
        Coordinates of the target (format: RA DEC).

    Returns:
    --------

    `sed` : {dict}
        Dictionnary containing the SED information (keys: 'Flux', 'wl', 'Freq', 'Err')

        - Flux [Jy]
        - wl [:math:`\mu m`]

    """
    try:
        c = coord.replace(' ', '+').replace('+-', '-')
        response = urllib.request.urlopen(
            'http://vizier.u-strasbg.fr/viz-bin/sed?-c=' + c + '&-c.rs=2')

        name_file = 'sed.vot'
        output = open(name_file, 'wb')
        output.write(response.read())
        output.close()

        tab = np.ma.getdata(vo.parse_single_table(name_file).array)

        tab_name = tab['_tabname']
        ins_name = getInstr(tab_name)

        cond = tab['sed_flux'] >= 0
        freq = tab['sed_freq'][cond]
        c = 299792458.
        wl = c/(freq*1e9)*1e6
        flux = tab['sed_flux'][cond].astype(float)
        err = tab['sed_eflux'][cond].astype(float)

        data = {'Flux': list(flux),
                'Err': list(err),
                'Freq': list(freq),
                'wl': list(wl),
                'name': list(ins_name)
                }
        os.remove(name_file)
    except Exception:
        data = None
    return data


def sed2mag(sed, bands):
    """
    Extract magnitude from interpolated SED.
    """
    conv_flux = {
        'B': {'wl': 0.44, 'F0': 4260},
        'V': {'wl': 0.5556, 'F0': 3540},  # Allen's astrophysical quantities
        'R': {'wl': 0.64, 'F0': 3080},
        'I': {'wl': 0.79, 'F0': 2550},
        'J': {'wl': 1.215, 'F0': 1630},
        'H': {'wl': 1.654, 'F0': 1050},
        'K': {'wl': 2.179, 'F0': 655},
        'L': {'wl': 3.547, 'F0': 276},
        'M': {'wl': 4.769, 'F0': 160},
        # 10.2, 42.7 Johnson N (https://www.gemini.edu/?q=node/11119)
        'N': {'wl': 10.2, 'F0': 42.7},
        'Q': {'wl': 20.13, 'F0': 9.7},
    }

    l_m = []
    with np.errstate(divide='ignore'):
        f_sed = interp1d(sed['wl'], np.log10(
            sed['Flux']), bounds_error=False)
    for b in bands:
        try:
            F = 10**(f_sed(conv_flux[b]['wl']))
            F0 = conv_flux[b]['F0']
            m = -2.5*np.log10(F/F0)
            l_m.append(m)
        except Exception:
            l_m.append(np.nan)
    return l_m


def getInstr(l_tabname):
    """Get the appropriate name of the Vizier database.

    Parameters
    ----------
    `l_tabname` : {array}
        List of label used in SED vizier database.

    Returns
    -------
    `l_ins`: {array}
        Convenient naming convention for list of SED points.
    """
    known_entries = {b'I/320/spm4': 'SPM+11',
                     b'II/7A/catalog': 'Morel+78',
                     b'II/336/apass9': 'APASS+16',
                     b'I/327/cmc15': 'CMC+15',
                     b'J/A+A/514/A2/table4': 'AKARI+10',
                     b'I/345/gaia2': 'GAIA+18',
                     b'J/MNRAS/463/4210/ucac4rpm': 'UCAC4+16',
                     b'I/305/out': 'GSC+06',
                     b'II/125/main': 'IRAS+96',
                     b'II/225/psc': 'IRAS+99',
                     b'II/297/irc': 'ISAS+10',
                     b'I/289/out': 'UCAC2+04',
                     b'I/340/ucac5': 'UCAC5+17',
                     b'V/114/msx6_gp': 'MSX+03',
                     b'I/339/hsoy': 'HSOY+17',
                     b'I/322A/out': 'UCAC4+12',
                     b'IV/34/epic': 'EPIC+17',
                     b'J/A+A/446/949/pm': 'DIAS+06',  # 2MASS
                     b'J/ApJS/112/557/table1': 'IRAS+97',
                     b'II/348/vvv2': 'VISTA+17',
                     b'II/328/allwise': 'ALLWISE+13',  # 2MASS
                     b'I/337/gaia': 'GAIA+16',
                     b'I/297/out': 'NOMAD+05',
                     b'II/246/out': '2MASS+03',  # 2MASS
                     b'I/317/sample': 'PPMXL+10',
                     b'II/349/ps1': 'PANSTAR+16',
                     b'I/343/gps1': 'TIAN+17',
                     b'II/338/catalog': 'IRAS+15',
                     b'J/ApJS/154/673/DIRBE': 'COBE+04',
                     b'J/MNRAS/398/221/table2': 'BAUME+09',
                     b'I/280B/ascc': 'ASCC+09',
                     b'II/346/jsdc_v2': 'JSDC+17',
                     b'I/239/hip_main': 'HIPP+97',
                     b'I/312/sample': 'ROESER+08',
                     b'I/342/f3': 'ANDRUK+16',
                     b'V/137D/XHIP': 'ANDERSON+12',
                     b'J/PASP/120/1128/catalog': 'OFEK+08',
                     b'J/ApJ/768/25/table2': 'Herschel+13',
                     b'II/311/wise': 'WISE+12',
                     b'J/AJ/155/30/table1': 'NPOI+18',
                     b'J/A+A/413/1037/table1': 'Kimeswenger+04',
                     b'J/ApJS/190/203/table3': 'Price+10',
                     b'I/276/supplem': 'Fabricius+02',
                     }

    l_ins = [known_entries.get(name, name.decode("utf-8")) for name in l_tabname]
    return l_ins
