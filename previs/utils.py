"""
@author: Anthony Soulain (University of Sydney)

--------------------------------------------------------------------
PREVIS: Python Request Engine for Virtual Interferometric Survey
--------------------------------------------------------------------

This file contains general function.
"""
import json
import os
import time
import urllib.request
from pathlib import Path

from numpy import bool_
from termcolor import colored
from termcolor import cprint

# on windows, colorama should help making termcolor compatible
try:
    import colorama

    colorama.init()
except ImportError:
    if os.name == "nt":  # Windows plateform detected
        print(
            "Warning: in Windows, some prints might not work properly. Install colorama to fix this."
        )


def connect(host):
    try:
        urllib.request.urlopen(host)
        return True
    except Exception:
        return False


def check_servers_response():
    connect_simbad = connect("http://simbad.u-strasbg.fr/simbad")
    connect_vizier = connect("http://vizier.u-strasbg.fr/vizier/sed/")
    if connect_simbad and connect_vizier:
        out = {}
    else:
        cprint("\nPREVIS uses url requests, but something has gone wrong !", "red")
        if not connect_simbad and not connect_vizier:
            cprint("-> check your internet connection,", "red")
        elif not connect_simbad:
            cprint("-> check SIMBAD server,", "red")
        else:
            cprint("-> check VIZIER server.", "red")
        out = None
    return out


def printtime(n, start_time):
    t = time.time() - start_time
    t0 = time.time()
    m = t // 60
    print("==> %s (%d min %2.3f s)" % (n, m, t - m * 60))
    return t0


def sanitize_survey_file(survey_file):
    assert isinstance(survey_file, (str, os.PathLike))
    survey_file = Path(survey_file)

    if survey_file.suffix == "":
        survey_file = survey_file.with_suffix(".json")

    return survey_file


def sanitize_booleans(dic):
    """Recursively convert values in a nested dictionnary from np.bool_ to builtin bool type
    This is required for json serialization.
    """
    d2 = dic.copy()
    for k, v in dic.items():
        if isinstance(v, dict):
            d2[k] = sanitize_booleans(v)
        if isinstance(v, bool_):
            d2[k] = bool(v)
    return d2


def save(result, result_file, overwrite=False):
    """Save <result> data to json <result_file>"""
    data_file = sanitize_survey_file(result_file)
    if data_file.exists() and not overwrite:
        raise FileExistsError(data_file)

    if not data_file.parent.is_dir():
        # todo: logme
        os.makedirs(data_file.parent)

    survey_ = sanitize_booleans(result)
    with open(data_file, mode="w") as ofile:
        json.dump(survey_, ofile)

    return data_file


def load(result_file):
    """Load result data from json <result_file>"""
    survey_file = sanitize_survey_file(result_file)
    with open(survey_file) as ofile:
        survey = json.load(ofile)
    return survey


def add_vs_mode_matisse(out, dic, star, cond_VLTI, cond_guid):
    """Small function for count_survey. Counts MATISSE observability for each mode."""
    for tel in ["AT", "UT"]:
        for ft in ["noft", "ft"]:
            for band in ["L", "N"]:
                for res in ["LR", "HR"]:
                    cond_ins = out[star]["Ins"]["MATISSE"][tel][ft][band][res]
                    if cond_VLTI and cond_guid and cond_ins:
                        dic["MATISSE"][tel][ft][band][res].append(star)
    return dic


def add_vs_mode_gravity(out, dic, star, cond_VLTI, cond_guid):
    """Small function for count_survey. Counts GTAVITY observability for each mode."""
    for tel in ["AT", "UT"]:
        for res in ["MR", "HR"]:
            cond_ins = out[star]["Ins"]["GRAVITY"][tel]["K"][res]
            if cond_VLTI and cond_guid and cond_ins:
                dic["GRAVITY"][tel][res].append(star)
    return dic


def count_survey(survey, limit="imaging"):
    """Count the number of star observable with each HRA instrument.

    Parameters:
    -----------
    `survey`: {dict}
        survey is the result from previs.search. It's generally used if
        the input of previs.search is a list of stars.
    Result:
    -------
    `dic`: {dict}
        The result contains lists of stars observable with each mode
        and instrument considered by previs.search (See data['Ins]).

    """

    if survey is not None:
        pass
    else:
        return SurveyClass([])

    list_star = survey.keys()
    n_star = len(list_star)

    n_chara, n_vlti = 0, 0
    for x in list_star:
        if survey[x] is not None:
            if survey[x]["Simbad"]:
                if not survey[x]["SED"] is None:
                    if survey[x]["Observability"]["VLTI"]:
                        n_vlti += 1
                    if survey[x]["Observability"]["CHARA"]:
                        n_chara += 1

    cprint("\nYour list contains %i stars:" % n_star, "cyan")
    cprint("-------------------------", "cyan")
    print(
        "Observability: %i (%2.1f %%) from the VLTI, %i (%2.1f %%) from the CHARA.\n"
        % (n_vlti, 100 * float(n_vlti) / n_star, n_chara, 100 * float(n_chara) / n_star)
    )

    dic = SurveyClass(
        {
            "MATISSE": {
                "UT": {
                    "noft": {"L": {"LR": [], "HR": []}, "N": {"LR": [], "HR": []}},
                    "ft": {"L": {"LR": [], "HR": []}, "N": {"LR": [], "HR": []}},
                },
                "AT": {
                    "noft": {"L": {"LR": [], "HR": []}, "N": {"LR": [], "HR": []}},
                    "ft": {"L": {"LR": [], "HR": []}, "N": {"LR": [], "HR": []}},
                },
            },
            "GRAVITY": {"UT": {"MR": [], "HR": []}, "AT": {"MR": [], "HR": []}},
            "PIONIER": [],
            "VISION": [],
            "PAVO": [],
            "CLASSIC": {"V": [], "H": [], "K": []},
            "CLIMB": [],
            "MYSTIC": [],
            "MIRC": {"H": [], "K": []},
            "VEGA": {"LR": [], "MR": [], "HR": []},
        }
    )

    list_no_simbad = []
    for star in list_star:
        if survey[star] is not None:
            if survey[star]["Simbad"]:
                if type(survey[star]["Guiding_star"]["VLTI"]) == list:
                    if (len(survey[star]["Guiding_star"]["VLTI"][0]) > 0) or (
                        len(survey[star]["Guiding_star"]["VLTI"][1]) > 0
                    ):
                        cond_guid_vlti = True
                    else:
                        cond_guid_vlti = False
                elif survey[star]["Guiding_star"]["VLTI"] == "Science star":
                    cond_guid_vlti = True
                else:
                    cond_guid_vlti = False

                cond_VLTI = survey[star]["Observability"]["VLTI"]
                cond_CHARA = survey[star]["Observability"]["CHARA"]
                cond_tilt = survey[star]["Ins"]["CHARA"]["Guiding"]
                dic = add_vs_mode_matisse(survey, dic, star, cond_VLTI, cond_guid_vlti)
                dic = add_vs_mode_gravity(survey, dic, star, cond_VLTI, cond_guid_vlti)

                cond_ins = survey[star]["Ins"]["PIONIER"]["H"]
                if cond_VLTI and cond_guid_vlti and cond_ins:
                    dic["PIONIER"].append(star)

                cond_ins = survey[star]["Ins"]["VISION"][limit]
                if cond_VLTI and cond_guid_vlti and cond_ins:
                    dic["VISION"].append(star)

                for band in ["H", "K"]:
                    cond_ins = survey[star]["Ins"]["CHARA"]["MIRC"][band]

                    if cond_CHARA and cond_ins and cond_tilt:
                        dic["MIRC"][band].append(star)

                for res in ["LR", "HR"]:
                    cond_ins = survey[star]["Ins"]["CHARA"]["VEGA"][res]
                    if cond_CHARA and cond_ins and cond_tilt:
                        dic["VEGA"][res].append(star)

                for band in ["V", "H", "K"]:
                    cond_ins = survey[star]["Ins"]["CHARA"]["CLASSIC"][band]
                    if cond_CHARA and cond_ins and cond_tilt:
                        dic["CLASSIC"][band].append(star)

                if (
                    cond_CHARA
                    and survey[star]["Ins"]["CHARA"]["PAVO"]["R"]
                    and cond_tilt
                ):
                    dic["PAVO"].append(star)

                if (
                    cond_CHARA
                    and survey[star]["Ins"]["CHARA"]["MYSTIC"]["K"]
                    and cond_tilt
                ):
                    dic["MYSTIC"].append(star)

                if (
                    cond_CHARA
                    and survey[star]["Ins"]["CHARA"]["CLIMB"]["K"]
                    and cond_tilt
                ):
                    dic["CLIMB"].append(star)
            else:
                list_no_simbad.append(star)

    # if list_no_simbad:
    #     cprint('Warning: some stars are not in Simbad:', 'red')
    #     print(list_no_simbad)
    dic["unavailable"] = list_no_simbad
    return dic


class SurveyClass(dict):
    def print_log(self):
        res = "\n".join(
            [
                colored("VLTI:", "green"),
                colored("-----", "green"),
                "MATISSE (AT): %s" % str(self["MATISSE"]["AT"]["noft"]["L"]["LR"]),
                "        (UT): %s" % str(self["MATISSE"]["UT"]["noft"]["L"]["LR"]),
                "GRAVITY (AT): %s" % str(self["GRAVITY"]["AT"]["MR"]),
                "        (UT): %s" % str(self["GRAVITY"]["UT"]["MR"]),
                "PIONIER (AT/UT): %s" % str(self["PIONIER"]),
                "",
                colored("CHARA:", "green"),
                colored("------", "green"),
                "VEGA: %s" % str(self["VEGA"]["LR"]),
                "PAVO: %s" % str(self["PAVO"]),
                "MIRC: %s" % str(self["MIRC"]["H"]),
                "CLIMB: %s" % str(self["CLIMB"]),
                "CLASSIC: %s" % str(self["CLASSIC"]["H"]),
            ]
        )
        print(res)
        return res
