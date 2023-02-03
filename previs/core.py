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

This file contains the core of previs: previs.search to use previs
on one or a list of targets.

--------------------------------------------------------------------
"""
import time
import warnings

import astropy.coordinates as ac
import numpy as np
from astropy import units as u
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
from termcolor import cprint
from uncertainties import ufloat

from previs.instr import chara_limit
from previs.instr import gravity_limit
from previs.instr import ivis_limit
from previs.instr import matisse_limit
from previs.instr import pionier_limit
from previs.sed import getSed
from previs.sed import sed2mag
from previs.utils import check_servers_response
from previs.utils import printtime

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", module="scipy.interpolate.interp1d")


def search(star, source="ESO", check=False, verbose=False):
    """Perform a large search to get informations about a star or a list of stars (observability, magnitude, distance, sed, etc.)

    Parameters
    ----------
    `star` : {str}
        Name of the star,\n
    `source`: {str}
        Limiting magnitudes used to constrain MATISSE observability. If 'ESO', the informations are extracted from
        the ESO website, else estimated performance are used,\n
    `check` : {bool}, (optional)
        If True, check MATISSE limiting magnitude in the ESO websites, by default False. Previs come with
        saved limiting magnitudes as in Jan. 2020 (P105). The informations are stored in data/eso_limits_matisse.json,\n
    `verbose`: {bool}
        Print some informations about the ongoing process (default: False). The verbose ability is not properly
        compatible with the progress bar print (not very fancy).


    Returns
    -------
    `data`: {dict}
        data is a dictionnary with different keys:\n
            -'Name': Name of the star,\n
            -'Simbad': If True, star is in Simbad,\n
            -'Coord': Celestial coordinates,\n
            -'Sp_type': Spectral type,\n
            -'Distance': Astrometric distance,\n
            -'SED': Spectral Energy Distribution,\n
            -'Mag': Magnitudes (V, J, H, etc.),\n
            -'Gaia_dr2': Gaia DR2 informations,\n
            -'Ins': Observability with VLTI and CHARA instruments,\n
            -'Observability': Observability from sites: VLTI and CHARA,\n
            -'Guiding_star': Guiding star informations at VLTI.\n
    """
    if check_servers_response() is None:
        return None

    start_time = time.time()
    if type(star) != str:
        raise NameError("Input need to be a target name (str).")

    star_user = star
    star = star.upper()
    if verbose:
        cprint("\n%s: search started (could take up to 30 seconds)..." % star, "cyan")
    data = {"Simbad": False}
    data["Ins"] = None
    data["Name"] = star
    # --------------------------------------
    #       Coordinates of the target
    # --------------------------------------
    coord = {}
    customSimbad = Simbad()
    customSimbad.add_votable_fields("parallax", "sptype", "id", "flux(V)", "flux(B)")

    try:
        objet = customSimbad.query_object(star)
        coord[star] = np.array([objet["RA"][0], objet["DEC"][0]])
        coordo = str(coord[star][0]) + " " + str(coord[star][1])
        c = ac.SkyCoord(coordo, unit=(u.hourangle, u.deg))
        data["Coord"] = coordo

        plx = ufloat(objet["PLX_VALUE"].data[0], objet["PLX_ERROR"].data[0])
        d = 1 / plx
        data["Distance"] = {"d": d.nominal_value, "e_d": d.std_dev}
        data["Simbad"] = True
        aa = str(objet["SP_TYPE"].data[0])
        sptype = aa.split("b")[1].split("'")[1]
        data["Sp_type"] = sptype
    except Exception:
        pass
    if not data["Simbad"]:
        raise ValueError("%s not in Simbad!" % star_user)
    # --------------------------------------
    #                 SED
    # --------------------------------------
    if verbose:
        print("Get SED from Vizier database...")
    sed = getSed(coordo)
    data["SED"] = sed

    # --------------------------------------
    #       Magnitude of the target
    # --------------------------------------
    l_bands = ["B", "V", "R", "J", "H", "K", "L", "M", "N"]

    try:
        with np.errstate(divide="ignore"):
            magB, magV, magR, magJ, magH, magK, magL, magM, magN = sed2mag(sed, l_bands)
    except TypeError:
        return None

    if np.isnan(magV):
        try:
            magV = objet["FLUX_V"][0]
            if magV is np.ma.masked:
                magV = np.nan
        except Exception:
            pass
    try:
        magB = objet["FLUX_B"][0]
        if magB is np.ma.masked:
            magB = np.nan
    except Exception:
        magB = np.nan

    data["Mag"] = {
        "magB": float(magB),
        "magV": float(magV),
        "magR": float(magR),
        "magH": float(magH),
        "magK": float(magK),
        "magL": float(magL),
        "magM": float(magM),
        "magN": float(magN),
        "magJ": float(magJ),
    }

    if verbose:
        t1 = printtime("Check SED: done", start_time)
    # --------------------------------------
    #                GAIA DR2
    # --------------------------------------
    columns = [
        "_r",
        "RA_ICRS",
        "DE_ICRS",
        "e_RA_ICRS",
        "e_DE_ICRS",
        "Gmag",
        "Plx",
        "e_Plx",
        "pmRA",
        "e_pmRA",
        "pmDE",
        "e_pmDE",
        "Teff",
    ]
    v = Vizier(columns=columns)
    data["Gaia_dr2"] = {}
    try:
        res = v.query_region(star, radius="2s", catalog="I/345/gaia2")
        data["Mag"]["magG"] = float(np.ma.getdata(res["I/345/gaia2"]["Gmag"])[0])
        data["Gaia_dr2"]["RA"] = float(np.ma.getdata(res["I/345/gaia2"]["RA_ICRS"])[0])
        data["Gaia_dr2"]["e_RA"] = float(
            np.ma.getdata(res["I/345/gaia2"]["e_RA_ICRS"])[0]
        )
        data["Gaia_dr2"]["DEC"] = float(np.ma.getdata(res["I/345/gaia2"]["DE_ICRS"])[0])
        data["Gaia_dr2"]["e_DEC"] = float(
            np.ma.getdata(res["I/345/gaia2"]["e_DE_ICRS"])[0]
        )
        data["Gaia_dr2"]["Plx"] = float(np.ma.getdata(res["I/345/gaia2"]["Plx"])[0])
        data["Gaia_dr2"]["e_Plx"] = float(np.ma.getdata(res["I/345/gaia2"]["e_Plx"])[0])
        data["Gaia_dr2"]["pmRA"] = float(np.ma.getdata(res["I/345/gaia2"]["pmRA"])[0])
        data["Gaia_dr2"]["e_pmRA"] = float(
            np.ma.getdata(res["I/345/gaia2"]["e_pmRA"])[0]
        )
        data["Gaia_dr2"]["pmDE"] = float(np.ma.getdata(res["I/345/gaia2"]["pmDE"])[0])
        data["Gaia_dr2"]["e_pmDE"] = float(
            np.ma.getdata(res["I/345/gaia2"]["e_pmDE"])[0]
        )
        data["Gaia_dr2"]["Teff"] = float(np.ma.getdata(res["I/345/gaia2"]["Teff"])[0])

        plx = ufloat(data["Gaia_dr2"]["Plx"], data["Gaia_dr2"]["e_Plx"])

        Dkpc = 1.0 / plx
        data["Gaia_dr2"]["check"] = True
        data["Gaia_dr2"]["Dkpc"] = Dkpc.nominal_value
        data["Gaia_dr2"]["e_Dkpc"] = Dkpc.std_dev
    except Exception:
        data["Gaia_dr2"]["check"] = False
        data["Gaia_dr2"]["Dkpc"] = np.nan
        data["Gaia_dr2"]["e_Dkpc"] = np.nan
        data["Gaia_dr2"]["Plx"] = np.nan
        data["Gaia_dr2"]["e_Plx"] = np.nan
        data["Gaia_dr2"]["pmRA"] = np.nan
        data["Gaia_dr2"]["pmDE"] = np.nan
        data["Mag"]["magG"] = np.nan
    if verbose:
        t2 = printtime("Check Gaia: done", t1)
    # --------------------------------------
    #             Guiding star
    # --------------------------------------
    data["Guiding_star"] = {}
    v = Vizier(columns=["*", "+<Gmag>"])

    cond_guid_1 = np.isnan(data["Mag"]["magG"]) and (np.isnan(data["Mag"]["magR"]))
    cond_guid_2 = (data["Mag"]["magG"] >= 12.5) or (data["Mag"]["magG"] <= -3)
    cond_guid_3 = np.isnan(data["Mag"]["magG"]) and (
        (data["Mag"]["magR"] >= 12.5) or (data["Mag"]["magR"] <= -3)
    )

    if cond_guid_1 or cond_guid_2 or cond_guid_3:
        res = v.query_region(star, radius="57s", catalog="I/337/gaia")

        try:
            Gmag = np.ma.getdata(res["I/337/gaia"]["__Gmag_"])
        except TypeError:
            return None
        cond1 = Gmag <= 12.5
        cond2 = (Gmag <= 15) & (Gmag > 12.5)

        gmag1 = np.ma.getdata(res["I/337/gaia"]["__Gmag_"][cond1])
        ra1 = np.ma.getdata(res["I/337/gaia"]["RA_ICRS"][cond1])
        dec1 = np.ma.getdata(res["I/337/gaia"]["DE_ICRS"][cond1])

        gmag2 = np.ma.getdata(res["I/337/gaia"]["__Gmag_"][cond2])
        ra2 = np.ma.getdata(res["I/337/gaia"]["RA_ICRS"][cond2])
        dec2 = np.ma.getdata(res["I/337/gaia"]["DE_ICRS"][cond2])

        guid1, guid2 = [], []

        for i in range(len(ra1)):
            guid1.append([float(ra1[i]), float(dec1[i]), float(gmag1[i])])
        for i in range(len(ra2)):
            guid2.append([float(ra2[i]), float(dec2[i]), float(gmag2[i])])

        data["Guiding_star"]["VLTI"] = [guid1, guid2]
    else:
        data["Guiding_star"]["VLTI"] = "Science star"

    data["Guiding_star"]["CHARA"] = bool(np.min([magV, magR]) <= 10)

    if verbose:
        t3 = printtime("Check guiding star: done,", t2)
    # --------------------------------------
    #             Observability
    # --------------------------------------
    L_paranal = -24.63  # Lattitude deg
    L_chara = 34.2236
    Obs = {"VLTI": False, "CHARA": False}

    min_elev = 40
    if c.dec.deg <= ((90 - min_elev) - abs(L_paranal)):
        Obs["VLTI"] = True
    if c.dec.deg >= (L_chara - (90 - min_elev)):
        Obs["CHARA"] = True

    data["Observability"] = Obs
    # --------------------------------------
    #       Limit interferometers
    # --------------------------------------
    tmp = {}
    tmp["PIONIER"] = pionier_limit(magH)
    tmp["CHARA"] = chara_limit(magK, magH, magR, magV)
    tmp["MATISSE"] = matisse_limit(magL, magM, magN, magK, source=source, check=check)
    tmp["GRAVITY"] = gravity_limit(magV, magK)
    tmp["VISION"] = ivis_limit(magR)
    data["Ins"] = tmp
    data["Name"] = star
    if verbose:
        printtime("Check Instruments: done", t3)
        cprint("Done (%2.2f s)." % (time.time() - start_time), "cyan")
    return data


def f(out, star):
    out[star] = search(star, check=False, verbose=False)
    return out


def survey(list_star):
    """Perform previs search on a list of stars.
    Parameters
    ----------
    `list_star` : {list}
        List of stars.\n
    Returns
    -------
    `survey`: {dict}
        Dictionnary containing previs search for all stars.
    """
    if check_servers_response() is None:
        return None

    if len(list_star) == 0:
        raise ValueError("The target list is empty.")

    cprint("\nStarting survey on %i stars:" % len(list_star), "cyan")
    cprint("-------------------------", "cyan")

    from multiprocess import Process, Manager

    manager = Manager()
    d = manager.dict()
    job = [Process(target=f, args=(d, list_star[i])) for i in range(len(list_star))]
    _ = [p.start() for p in job]
    _ = [p.join() for p in job]
    return d
