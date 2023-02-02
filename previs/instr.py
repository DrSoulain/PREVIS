"""
@author: Anthony Soulain (University of Sydney)

--------------------------------------------------------------------
PREVIS: Python Request Engine for Virtual Interferometric Survey
--------------------------------------------------------------------

This file contains function to check the star observability with
each VLTI and CHARA instruments. The limiting magnitudes are extracted
from the ESO website or the CHARA website. In the case of MATISSE,
the limiting magnitude can be extracted automaticaly from the actual
performances (P106, 2020) or estimated performances (2017). Some mode
of MATISSE are not yet commissioned (UT with GRA4MAT), so only estimated performances are used.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from previs.utils import connect

store_directory = Path(__file__).parent / "data"


def JyToMag(f, band):
    """
    Convert flux density in Jy to Johnson mag.

    Parameters:
    -----------

    `f`: {array}:
        Flux density [Jy],\n
    `band`: {str}
        Photometric band name (B, V, R, L, etc.).

    Returns:
    --------

    `m`: {array}:
            Johnson magnitudes.
    """

    conv_flux = {
        "B": {"wl": 0.44, "F0": 4260},
        # Allen's astrophysical quantities
        "V": {"wl": 0.5556, "F0": 3540},
        "R": {"wl": 0.64, "F0": 3080},
        "I": {"wl": 0.79, "F0": 2550},
        "J": {"wl": 1.215, "F0": 1630},
        "H": {"wl": 1.654, "F0": 1050},
        "K": {"wl": 2.179, "F0": 655},
        "L": {"wl": 3.547, "F0": 276},
        "M": {"wl": 4.769, "F0": 160},
        # 10.2, 42.7 Johnson N (https://www.gemini.edu/?q=node/11119)
        "N": {"wl": 10.2, "F0": 42.7},
        "Q": {"wl": 20.13, "F0": 9.7},
    }

    F = np.array(f).astype(float)
    out = -2.5 * np.log10(F / conv_flux[band]["F0"])
    return list(out)


def limit_ESO_matisse_web(check):
    """Extract limiting flux (Jy) from ESO MATISSE instrument descriptions and
    return magnitude (optimal 10% seeing conditions).

    Parameters
    ----------
    `check`: {bool}
        choose whether to request data from web (True) or use on disk data (False).

    Returns
    -------
    `limits_data`: {dict}
        Limiting magnitudes of MATISSE.
    """

    url = "http://www.eso.org/sci/facilities/paranal/instruments/matisse/inst.html"
    stored_data_filepath = store_directory / "eso_limits_matisse.json"
    new_data_filepath = store_directory / "eso_limits_matisse_new.json"

    if Path(stored_data_filepath).is_file() and not check:
        with open(stored_data_filepath) as ofile:
            limits_data = json.load(ofile)
    else:
        print("Check MATISSE limits from ESO web site...")
        response_server = connect(url)
        if response_server:
            tables = pd.read_html(url)  # Returns list of all tables on page
            try:
                limit_MATISSE_abs = tables[4]  # Select table of interest
                limit_MATISSE_rel = tables[5]
                limit_MATISSE_gra4mat = tables[6]

                list_limit_abs = np.array(limit_MATISSE_abs)
                list_limit_rel = np.array(limit_MATISSE_rel)
                list_limit_gra4mat = np.array(limit_MATISSE_gra4mat)

                at_lim_good = [x.split("Jy")[0] for x in list_limit_abs[:, 1]]
                ut_lim_good = [x.split("Jy")[0] for x in list_limit_abs[:, 3]]

                at_lim_good_rel = [x.split("Jy")[0] for x in list_limit_rel[:, 1]]
                ut_lim_good_rel = [x.split("Jy")[0] for x in list_limit_rel[:, 3]]

                at_L_gra4mat = [x.split("Jy")[0] for x in list_limit_gra4mat[1:, 1]]
                at_M_gra4mat = [x.split("Jy")[0] for x in list_limit_gra4mat[1:, 3]]

                at_noft_L = JyToMag(
                    [at_lim_good[0], at_lim_good[2], at_lim_good_rel[3]], "L"
                )
                at_noft_M = JyToMag([at_lim_good[1], at_lim_good_rel[2]], "M")
                at_noft_N = JyToMag([at_lim_good[4], at_lim_good_rel[4]], "N")

                ut_noft_L = JyToMag(
                    [ut_lim_good[0], ut_lim_good_rel[1], ut_lim_good_rel[3]], "L"
                )
                ut_noft_M = JyToMag([ut_lim_good[1], ut_lim_good_rel[2]], "M")
                ut_noft_N = JyToMag([ut_lim_good[4], ut_lim_good_rel[4]], "N")

                at_ft_L = JyToMag(
                    [at_L_gra4mat[0], at_L_gra4mat[1], at_L_gra4mat[2]], "L"
                )
                at_ft_M = JyToMag([at_M_gra4mat[0], at_M_gra4mat[1]], "M")
                at_ft_N = []  # not commisionned (see estimated performance)

                limits_data = {
                    "at": {
                        "noft": {"L": at_noft_L, "M": at_noft_M, "N": at_noft_N},
                        "ft": {"L": at_ft_L, "M": at_ft_M, "N": at_ft_N},
                    },
                    "ut": {
                        "noft": {"L": ut_noft_L, "M": ut_noft_M, "N": ut_noft_N},
                        "ft": {"L": [], "M": [], "N": []},
                    },
                }

                with open(new_data_filepath, mode="w") as ofile:
                    json.dump(limits_data, ofile, indent="  ")
            except Exception:
                print(
                    "-> The structure of the ESO website has changed: (%s) is used instead."
                    % stored_data_filepath
                )
                if Path(stored_data_filepath).is_file():
                    with open(stored_data_filepath) as ofile:
                        limits_data = json.load(ofile)
        else:
            print(
                "-> ESO website not available: (%s) is used instead."
                % stored_data_filepath
            )
            if Path(stored_data_filepath).is_file():
                with open(stored_data_filepath) as ofile:
                    limits_data = json.load(ofile)

    return limits_data


def limit_commissioning_matisse():
    """Estimated performance of MATISSE during testing and commissioning."""
    at_noft_L = [4.2, 0.9, -1.5]
    at_noft_M = [3.24, 1]
    at_noft_N = [-0.35, -2.2]
    at_ft_L = [7.7, 6.1, 4.2]
    at_ft_M = [5.24, 1.6]
    at_ft_N = [1.6, 0.1]
    ut_noft_L = [7, 3.7, 1.3]
    ut_noft_M = [6.03, 3.83]
    ut_noft_N = [2.7, 0.8]
    ut_ft_L = [10.3, 8.8, 6.9]
    ut_ft_M = [5, 5]
    ut_ft_N = [4.6, 3.2]

    dic_consortium = {
        "at": {
            "noft": {"L": at_noft_L, "M": at_noft_M, "N": at_noft_N},
            "ft": {"L": at_ft_L, "M": at_ft_M, "N": at_ft_N},
        },
        "ut": {
            "noft": {"L": ut_noft_L, "M": ut_noft_M, "N": ut_noft_N},
            "ft": {"L": ut_ft_L, "M": ut_ft_M, "N": ut_ft_N},
        },
    }
    return dic_consortium


def gravity_limit(magV, magK):
    """
    Return observability with GRAVITY instrument.
    """
    dic = {
        "UT": {"K": {"MR": False, "HR": False}},
        "AT": {"K": {"MR": False, "HR": False}},
    }
    if magV <= 11:
        dic["V_cond"] = "AT"
    elif (magV > 11) & (magV <= 16):
        dic["V_cond"] = "UT"
    else:
        dic["V_cond"] = "TooFaint"

    if (magK >= -4.0) & (magK <= -1):
        dic["UT"]["K"] = {"MR": False, "HR": False}
        dic["AT"]["K"] = {"MR": False, "HR": True}
    elif (magK > -1) & (magK <= 1):
        dic["UT"]["K"] = {"MR": False, "HR": False}
        dic["AT"]["K"] = {"MR": True, "HR": True}
    elif (magK > 1) & (magK <= 4):
        dic["UT"]["K"] = {"MR": False, "HR": True}
        dic["AT"]["K"] = {"MR": True, "HR": True}
    elif (magK > 4) & (magK <= 8):
        dic["UT"]["K"] = {"MR": True, "HR": True}
        dic["AT"]["K"] = {"MR": True, "HR": True}
    elif (magK > 8) & (magK <= 9):
        dic["UT"]["K"] = {"MR": True, "HR": True}
        dic["AT"]["K"] = {"MR": False, "HR": False}
    else:
        dic["UT"]["K"] = {"MR": False, "HR": False}
        dic["AT"]["K"] = {"MR": False, "HR": False}

    return dic


def matisse_limit(magL, magM, magN, magK, source="ESO", check=False):
    """
    Return observability with MATISSE instrument with different configurations (Spectral
    resolution, UTs or ATs, Fringe tracking, etc...).

    Parameters:
    -----------
    `magL`, `magM`, `magN`, `magK`: {float}
        Magnitudes in near- and mid-infrared (K=2.2, L=3.5, M=4.5, N=10 µm),\n
    `source`: {str}
        Source of the limiting magnitudes. If source = 'ESO' (default), the ESO website
        is checked to extract these limits. Otherwise, the estimated limits are used,\n
    `check`: {bool}
        If True, check the actual MATISSE performances on the ESO website (default=False).
        Otherwise, the data/eso_limits_matisse.json are used (perfomance in P105/2020).
    """
    dic = {}
    dic["AT"] = {
        "ft": {"L": {"LR": False}, "M": {"LR": False}, "N": {"LR": False}},
        "noft": {
            "L": {"LR": False, "MR": False, "HR": False},
            "M": {"LR": False, "HR": False},
            "N": {"LR": False, "HR": False},
        },
    }
    dic["UT"] = {
        "ft": {"L": {"LR": False}, "M": {"LR": False}, "N": {"LR": False}},
        "noft": {
            "L": {"LR": False, "MR": False, "HR": False},
            "M": {"LR": False, "HR": False},
            "N": {"LR": False, "HR": False},
        },
    }
    dic["limK"] = {"UT": False, "AT": False}

    if source == "ESO":
        dic_limit = limit_ESO_matisse_web(check=check)
    else:
        dic_limit = limit_commissioning_matisse()

    dic_matisse = limit_commissioning_matisse()

    # Frange tracker K band limit
    if magK <= 7.5:
        dic["limK"]["UT"] = True
        dic["limK"]["AT"] = True
    elif (magK > 7.5) & (magK <= 10.0):
        dic["limK"]["UT"] = True
        dic["limK"]["AT"] = False
    else:
        dic["limK"]["UT"] = False
        dic["limK"]["AT"] = False

    # --------------------------------------------------------------------
    # UT, ft
    lim = dic_matisse["ut"]["ft"]["L"]
    if magL <= lim[2]:
        dic["UT"]["ft"]["L"]["LR"] = True
        dic["UT"]["ft"]["L"]["MR"] = True
        dic["UT"]["ft"]["L"]["HR"] = True
    elif (magL > lim[2]) & (magL <= lim[1]):
        dic["UT"]["ft"]["L"]["LR"] = True
        dic["UT"]["ft"]["L"]["MR"] = True
        dic["UT"]["ft"]["L"]["HR"] = False
    elif (magL > lim[1]) & (magL <= lim[0]):
        dic["UT"]["ft"]["L"]["LR"] = True
        dic["UT"]["ft"]["L"]["MR"] = False
        dic["UT"]["ft"]["L"]["HR"] = False
    else:
        dic["UT"]["ft"]["L"]["LR"] = False
        dic["UT"]["ft"]["L"]["MR"] = False
        dic["UT"]["ft"]["L"]["HR"] = False

    lim = dic_limit["ut"]["ft"]["M"]
    if len(lim) == 0:
        # print('Not commisionned yet (M): use estimated sensitivity.')
        lim = limit_commissioning_matisse()["ut"]["ft"]["M"]

    if magM <= lim[0]:
        dic["UT"]["ft"]["M"]["LR"] = True
        dic["UT"]["ft"]["M"]["HR"] = True
    else:
        dic["UT"]["ft"]["M"]["LR"] = False
        dic["UT"]["ft"]["M"]["HR"] = False

    lim = dic_limit["ut"]["ft"]["N"]
    if len(lim) == 0:
        lim = limit_commissioning_matisse()["ut"]["ft"]["N"]
    if magN <= lim[1]:
        dic["UT"]["ft"]["N"]["LR"] = True
        dic["UT"]["ft"]["N"]["HR"] = True
    elif (magN > lim[1]) & (magN <= lim[0]):
        dic["UT"]["ft"]["N"]["LR"] = True
        dic["UT"]["ft"]["N"]["HR"] = False
    else:
        dic["UT"]["ft"]["N"]["LR"] = False
        dic["UT"]["ft"]["N"]["HR"] = False

    # --------------------------------------------------------------------
    # UT, noft
    lim = dic_limit["ut"]["noft"]["L"]
    if magL <= lim[2]:
        dic["UT"]["noft"]["L"]["LR"] = True
        dic["UT"]["noft"]["L"]["MR"] = True
        dic["UT"]["noft"]["L"]["HR"] = True
    elif (magL > lim[2]) & (magL <= lim[1]):
        dic["UT"]["noft"]["L"]["LR"] = True
        dic["UT"]["noft"]["L"]["MR"] = True
        dic["UT"]["noft"]["L"]["HR"] = False
    elif (magL > lim[1]) & (magL <= lim[0]):
        dic["UT"]["noft"]["L"]["LR"] = True
        dic["UT"]["noft"]["L"]["MR"] = False
        dic["UT"]["noft"]["L"]["HR"] = False
    else:
        dic["UT"]["noft"]["L"]["LR"] = False
        dic["UT"]["noft"]["L"]["MR"] = False
        dic["UT"]["noft"]["L"]["HR"] = False

    lim = dic_limit["ut"]["noft"]["M"]
    if magM <= lim[1]:
        dic["UT"]["noft"]["M"]["LR"] = True
        dic["UT"]["noft"]["M"]["HR"] = True
    elif (magM > lim[1]) & (magM <= lim[0]):
        dic["UT"]["noft"]["M"]["LR"] = True
        dic["UT"]["noft"]["M"]["HR"] = False
    else:
        dic["UT"]["noft"]["M"]["LR"] = False
        dic["UT"]["noft"]["M"]["HR"] = False

    lim = dic_limit["ut"]["noft"]["N"]
    if magN <= lim[1]:
        dic["UT"]["noft"]["N"]["LR"] = True
        dic["UT"]["noft"]["N"]["HR"] = True
    elif (magN > lim[1]) & (magN <= lim[0]):
        dic["UT"]["noft"]["N"]["LR"] = True
        dic["UT"]["noft"]["N"]["HR"] = False
    else:
        dic["UT"]["noft"]["N"]["LR"] = False
        dic["UT"]["noft"]["N"]["HR"] = False

    # AT, ft
    lim = dic_limit["at"]["ft"]["L"]
    if magL <= lim[2]:
        dic["AT"]["ft"]["L"]["LR"] = True
        dic["AT"]["ft"]["L"]["MR"] = True
        dic["AT"]["ft"]["L"]["HR"] = True
    elif (magL > lim[2]) & (magL <= lim[1]):
        dic["AT"]["ft"]["L"]["LR"] = True
        dic["AT"]["ft"]["L"]["MR"] = True
        dic["AT"]["ft"]["L"]["HR"] = False
    elif (magL > lim[1]) & (magL <= lim[0]):
        dic["AT"]["ft"]["L"]["LR"] = True
        dic["AT"]["ft"]["L"]["MR"] = False
        dic["AT"]["ft"]["L"]["HR"] = False
    else:
        dic["AT"]["ft"]["L"]["LR"] = False
        dic["AT"]["ft"]["L"]["MR"] = False
        dic["AT"]["ft"]["L"]["HR"] = False

    lim = dic_limit["at"]["ft"]["M"]
    if magM <= lim[1]:
        dic["AT"]["ft"]["M"]["LR"] = True
        dic["AT"]["ft"]["M"]["HR"] = True
    elif (magM > lim[1]) & (magM <= lim[0]):
        dic["AT"]["ft"]["M"]["LR"] = True
        dic["AT"]["ft"]["M"]["HR"] = False
    else:
        dic["AT"]["ft"]["M"]["LR"] = False
        dic["AT"]["ft"]["M"]["HR"] = False

    lim = dic_limit["at"]["ft"]["N"]
    if len(lim) == 0:
        lim = limit_commissioning_matisse()["at"]["ft"]["N"]
    if magN <= lim[1]:
        dic["AT"]["ft"]["N"]["LR"] = True
        dic["AT"]["ft"]["N"]["HR"] = True
    elif (magN > lim[1]) & (magN <= lim[0]):
        dic["AT"]["ft"]["N"]["LR"] = True
        dic["AT"]["ft"]["N"]["HR"] = False
    else:
        dic["AT"]["ft"]["N"]["LR"] = False
        dic["AT"]["ft"]["N"]["HR"] = False

    # AT, noft
    lim = dic_limit["at"]["noft"]["L"]
    if magL <= lim[2]:
        dic["AT"]["noft"]["L"]["LR"] = True
        dic["AT"]["noft"]["L"]["MR"] = True
        dic["AT"]["noft"]["L"]["HR"] = True
    elif (magL > lim[2]) & (magL <= lim[1]):
        dic["AT"]["noft"]["L"]["LR"] = True
        dic["AT"]["noft"]["L"]["MR"] = True
        dic["AT"]["noft"]["L"]["HR"] = False
    elif (magL > lim[1]) & (magL <= lim[0]):
        dic["AT"]["noft"]["L"]["LR"] = True
        dic["AT"]["noft"]["L"]["MR"] = False
        dic["AT"]["noft"]["L"]["HR"] = False
    else:
        dic["AT"]["noft"]["L"]["LR"] = False
        dic["AT"]["noft"]["L"]["MR"] = False
        dic["AT"]["noft"]["L"]["HR"] = False

    lim = dic_limit["at"]["noft"]["M"]
    if magM <= lim[1]:
        dic["AT"]["noft"]["M"]["LR"] = True
        dic["AT"]["noft"]["M"]["HR"] = True
    elif (magM > lim[1]) & (magM <= lim[0]):
        dic["AT"]["noft"]["M"]["LR"] = True
        dic["AT"]["noft"]["M"]["HR"] = False
    else:
        dic["AT"]["noft"]["M"]["LR"] = False
        dic["AT"]["noft"]["M"]["HR"] = False

    lim = dic_limit["at"]["noft"]["N"]
    if magN <= lim[1]:
        dic["AT"]["noft"]["N"]["LR"] = True
        dic["AT"]["noft"]["N"]["HR"] = True
    elif (magN > lim[1]) & (magN <= lim[0]):
        dic["AT"]["noft"]["N"]["LR"] = True
        dic["AT"]["noft"]["N"]["HR"] = False
    else:
        dic["AT"]["noft"]["N"]["LR"] = False
        dic["AT"]["noft"]["N"]["HR"] = False

    return dic


def pionier_limit(magH):
    """Return observability with PIONIER instrument."""
    dic = {}
    if (magH >= -1.0) & (magH <= 9.0):
        dic["H"] = True
    else:
        dic["H"] = False
    return dic


def chara_limit(magK, magH, magR, magV):
    """Return observability of the different instruments of CHARA."""
    dic = {
        "PAVO": {"R": False},
        "CLASSIC": {"K": False, "H": False, "V": False},
        "CLIMB": {"K": False},
        "MIRC": {"H": False, "K": False},
        "MYSTIC": {"K": False},
        "VEGA": {"LR": False, "MR": False, "HR": False},
        "SPICA": {"imaging": False, "diam": False},
    }

    dic["Guiding"] = np.min([magV, magR]) <= 10
    dic["CLASSIC"].update({"K": magK <= 6.5, "H": magH <= 7, "V": magV <= 10})

    dic["CLIMB"].update({"K": magK <= 6.0})

    dic["PAVO"].update({"R": magR <= 7.0})

    dic["MIRC"].update({"H": magH <= 6.5, "K": magK <= 3})

    dic["MYSTIC"].update({"K": magK <= 6.5})

    dic["SPICA"].update({"imaging": magV <= 6.0, "diam": magV <= 8})

    dic["VEGA"].update({"HR": magV <= 4.2, "MR": magV <= 5.8, "LR": magV <= 7.2})

    return dic


def ivis_limit(magR):
    dic = {"imaging": False, "diam": False}
    if magR <= 8.0:
        dic["imaging"] = True
        dic["diam"] = True
    elif (magR > 8.0) & (magR <= 10.0):
        dic["diam"] = True
    return dic
