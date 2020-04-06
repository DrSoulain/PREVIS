# -*- coding: utf-8 -*-
"""
@author: Anthony Soulain (University of Sydney)

--------------------------------------------------------------------
PREVIS: Python Request Engine for Virtual Interferometric Survey
--------------------------------------------------------------------

previs is a module to easely get the observability of a target or a
list of targets with the different beam combiners from the VLTI and 
CHARA interferometers. Previs perform a research in the Virtual
Observatory (OV) to get useful informations as:
- Spectral Energy Distribution (SED), used to extract magnitudes 
(especially L, M, and N mag which are not often included in the 
standard catalogs),
- Gaia DR2 distances.

Previs compare these magnitudes to the current limiting magnitudes
of each instruments. It also use the V or G magnitudes to check the
guiding issues or the tip/tilt correction limit. For the VLTI: If 
the star is too faint in G mag, Previs research the list of stars around
the target (57 arcsec) with the appropriate magnitude and give the
list of celestial coordinates usable as guiding star. Of course,
previs check also the on-site observability given the latitude of 
both observatory.

This file contains the core of previs: previs_search to use previs
on one target, and previs_survey to use it on a list of targets.

-------------------------------------------------------------------- 
"""

import pickle
import sys
import time
import warnings

import astropy.coordinates as ac
import numpy as np
from astropy import units as u
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
from previs.instr import (chara_limit, gravity_limit, matisse_limit,
                          pionier_limit)
from previs.sed import getSed, sed2mag
from previs.utils import printtime
from termcolor import cprint
from uncertainties import ufloat

warnings.filterwarnings('ignore')
warnings.filterwarnings('ignore', module='scipy.interpolate.interp1d')


def previs_search(star, source='ESO', check=False, verbose=True):
    """Perform a large research to get informations about target (observability, magnitude, distance, sed, etc.)

    Parameters
    ----------
    `star` : {str}
        Name of the star,\n
    `source`: {str}
        Limiting magnitudes used to constrain MATISSE observability. If 'ESO', the informations are extracted from
        the ESO website, else estimated performance are used,\n
    `check` : {bool}, (optional)
        If True, check MATISSE limiting magnitude in the ESO websites, by default False. Previs come with
        saved limiting magnitudes as in Jan. 2020 (P105). The informations are stored in files/eso_limits_matisse.dpy.

    Returns
    -------
    `data`: {dict}
        Dictionnary contains keys:\n
        -'Name': Name of the star,\n
        -'Simbad': If True, star is in Simbad,\n
        -'Coord': Celestial coordinates,\n
        -'sp_type': Spectral type,\n
        -'Distance': Astrometric distance,\n
        -'SED': Spectral Energy Distribution,\n
        -'Mag': Magnitudes (V, J, H, etc.),\n
        -'Gaia_dr2': Gaia DR2 informations,\n
        -'Ins': Observability with VLTI and CHARA instruments,\n
        -'Observability': Observability from sites: VLTI and CHARA,\n
        -'Guiding_star': Guiding star informations at VLTI.\n
    """

    start_time = time.time()
    star = star.upper()

    if verbose:
        cprint('\n%s: Research started (could take up to 30 seconds)...' %
               star, 'cyan')
    data = {'Simbad': False}
    data['Ins'] = None
    data['Name'] = star
    # --------------------------------------
    #       Coordinates of the target
    # --------------------------------------
    coord = {}
    customSimbad = Simbad()
    customSimbad.add_votable_fields(
        'parallax', 'sptype', 'id', 'flux(V)',  'flux(B)')

    try:
        objet = customSimbad.query_object(star)
        coord[star] = np.array([objet['RA'][0], objet['DEC'][0]])
        coordo = str(coord[star][0]) + ' ' + str(coord[star][1])
        c = ac.SkyCoord(coordo, unit=(u.hourangle, u.deg))
        data['Coord'] = coordo

        plx = ufloat(objet['PLX_VALUE'].data[0], objet['PLX_ERROR'].data[0])
        d = 1/plx
        data['Distance'] = {'d': d.nominal_value, 'e_d': d.std_dev}
        data['Simbad'] = True
        # if data['sp_type'] == None:
        aa = str(objet['SP_TYPE'].data[0])
        sptype = aa.split('b')[1].split("'")[1]
        data['sp_type'] = sptype
        # else:
        #    pass
    except:
        pass

    if not data['Simbad']:
        return data
    # --------------------------------------
    #                 SED
    # --------------------------------------
    sed = getSed(star, coord=coordo, upload=True)
    data['SED'] = sed

    # --------------------------------------
    #       Magnitude of the target
    # --------------------------------------
    l_bands = ['B', 'V', 'R', 'J', 'H', 'K', 'L', 'M', 'N']

    with np.errstate(divide='ignore'):
        magB, magV, magR, magJ, magH, magK, magL, magM, magN = sed2mag(
            sed, l_bands)

    if np.isnan(magV):
        try:
            magV = objet['FLUX_V'][0]
            if magV is np.ma.masked:
                magV = np.nan
        except:
            pass
    try:
        magB = objet['FLUX_B'][0]
        if magB is np.ma.masked:
            magB = np.nan
    except:
        magB = np.nan

    data['Mag'] = {'magB': float(magB),
                   'magV': float(magV),
                   'magR': float(magR),
                   'magH': float(magH),
                   'magK': float(magK),
                   'magL': float(magL),
                   'magM': float(magM),
                   'magN': float(magN),
                   'magJ': float(magJ)
                   }

    if verbose:
        t1 = printtime('Check SED: done', start_time)
    # --------------------------------------
    #                GAIA DR2
    # --------------------------------------
    columns = ['_r', 'RA_ICRS', 'DE_ICRS', 'e_RA_ICRS', 'e_DE_ICRS',
               'Gmag', 'Plx', 'e_Plx', 'pmRA', 'e_pmRA', 'pmDE', 'e_pmDE', 'Teff']
    v = Vizier(columns=columns)
    data['Gaia_dr2'] = {}
    try:
        res = v.query_region(star, radius="1s", catalog='I/345/gaia2')
        data['Mag']['magG'] = float(
            np.ma.getdata(res['I/345/gaia2']['Gmag'])[0])
        data['Gaia_dr2']['RA'] = float(
            np.ma.getdata(res['I/345/gaia2']['RA_ICRS'])[0])
        data['Gaia_dr2']['e_RA'] = float(
            np.ma.getdata(res['I/345/gaia2']['e_RA_ICRS'])[0])
        data['Gaia_dr2']['DEC'] = float(
            np.ma.getdata(res['I/345/gaia2']['DE_ICRS'])[0])
        data['Gaia_dr2']['e_DEC'] = float(
            np.ma.getdata(res['I/345/gaia2']['e_DE_ICRS'])[0])
        data['Gaia_dr2']['Plx'] = float(
            np.ma.getdata(res['I/345/gaia2']['Plx'])[0])
        data['Gaia_dr2']['e_Plx'] = float(
            np.ma.getdata(res['I/345/gaia2']['e_Plx'])[0])
        data['Gaia_dr2']['pmRA'] = float(
            np.ma.getdata(res['I/345/gaia2']['pmRA'])[0])
        data['Gaia_dr2']['e_pmRA'] = float(
            np.ma.getdata(res['I/345/gaia2']['e_pmRA'])[0])
        data['Gaia_dr2']['pmDE'] = float(
            np.ma.getdata(res['I/345/gaia2']['pmDE'])[0])
        data['Gaia_dr2']['e_pmDE'] = float(
            np.ma.getdata(res['I/345/gaia2']['e_pmDE'])[0])
        data['Gaia_dr2']['Teff'] = float(
            np.ma.getdata(res['I/345/gaia2']['Teff'])[0])

        plx = ufloat(data['Gaia_dr2']['Plx'],  data['Gaia_dr2']['e_Plx'])

        Dkpc = 1./plx
        data['Gaia_dr2']['check'] = True
        data['Gaia_dr2']['Dkpc'] = Dkpc.nominal_value
        data['Gaia_dr2']['e_Dkpc'] = Dkpc.std_dev
    except:
        data['Gaia_dr2']['check'] = False
        data['Gaia_dr2']['Dkpc'] = np.nan
        data['Gaia_dr2']['e_Dkpc'] = np.nan
        data['Gaia_dr2']['Plx'] = np.nan
        data['Gaia_dr2']['e_Plx'] = np.nan
        data['Gaia_dr2']['pmRA'] = np.nan
        data['Gaia_dr2']['pmDE'] = np.nan
        data['Mag']['magG'] = np.nan
    if verbose:
        t2 = printtime('Check Gaia: done', t1)
    # --------------------------------------
    #             Guiding star
    # --------------------------------------

    v = Vizier(columns=['*', '+<Gmag>'])
    if np.isnan(data['Mag']['magR']) or (data['Mag']['magG'] >= 12.5) or (data['Mag']['magG'] <= -3):
        try:
            res = v.query_region(star, radius='57s', catalog='I/337/gaia')

            Gmag = np.ma.getdata(res['I/337/gaia']['__Gmag_'])
            cond1 = (Gmag <= 12.5)
            cond2 = (Gmag <= 15)

            gmag1 = np.ma.getdata(res['I/337/gaia']['__Gmag_'][cond1])
            ra1 = np.ma.getdata(res['I/337/gaia']['RA_ICRS'][cond1])
            dec1 = np.ma.getdata(res['I/337/gaia']['DE_ICRS'][cond1])

            gmag2 = np.ma.getdata(res['I/337/gaia']['__Gmag_'][cond2])
            ra2 = np.ma.getdata(res['I/337/gaia']['RA_ICRS'][cond2])
            dec2 = np.ma.getdata(res['I/337/gaia']['DE_ICRS'][cond2])

            guid1, guid2 = [], []

            for i in range(len(ra1)):
                guid1.append([ra1[i], dec1[i], gmag1[i]])
            for i in range(len(ra2)):
                guid2.append([ra2[i], dec2[i], gmag2[i]])

            data['Guiding_star'] = [np.array(guid1), np.array(guid2)]
        except:
            data['Guiding_star'] = 'ERROR'
    else:
        data['Guiding_star'] = 'Science star'

    if verbose:
        t3 = printtime('Check guiding star: done,', t2)
    # --------------------------------------
    #             Observability
    # --------------------------------------
    L_paranal = -24.63  # Lattitude deg
    L_chara = 34.2236
    Obs = {'VLTI': False, 'CHARA': False}

    min_elev = 40

    if c.dec.deg <= ((90 - min_elev) - abs(L_paranal)):
        Obs['VLTI'] = True
    if c.dec.deg >= (L_chara - (90 - min_elev)):
        Obs['CHARA'] = True

    data['Observability'] = Obs
    # --------------------------------------
    #       Limit interferometers
    # --------------------------------------
    tmp = {}
    tmp['PIONIER'] = pionier_limit(magH, magV)
    tmp['CHARA'] = chara_limit(magK, magH, magR, magV)
    tmp['MATISSE'] = matisse_limit(magL, magM, magN, magK,
                                   source=source, check=check)
    tmp['GRAVITY'] = gravity_limit(magV, magK)
    data['Ins'] = tmp
    data['Name'] = star
    if verbose:
        printtime('Check Instruments: done', t3)
    return data


def previs_survey(list_star, namelist='survey', upload=True):
    """ Perform previs research on a list of stars.

    Parameters
    ----------
    `list_star` : {list}
        List of stars,\n
    `namelist` : {str}, (optional)
        Name of the file to save as .dpy, by default 'survey',\n
    `upload` : {bool}, (optional)
        If True, perform the survey, else load the .dpy file, by default True.

    Returns
    -------
    `out`: {dict}
        Dictionnary containing previs research for all stars.
    """
    if upload:
        cprint('\nBegin survey on %i stars:' % len(list_star), 'cyan')
        cprint('-------------------------', 'cyan')
        out = {}
        n = float(len(list_star))
        i = 0
        for star in list_star:
            size_str = 'Progress: %2.1f %% (%s)        ' % (100.*(i+1)/n, star)
            sys.stdout.flush()
            sys.stdout.write('%s\r' % size_str)
            out[star] = previs_search(star, verbose=False)
            i += 1
        file = open(namelist + '.dpy', 'wb')
        pickle.dump(out, file, 2)
        file.close()
        print('\nDone.')
    else:
        file = open(namelist + '.dpy', 'rb')
        out = pickle.load(file)
        file.close()

    return out
