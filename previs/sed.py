"""
Created on Thur Mar 26 14:49:19 2020

@author: asoulain
"""
import json
import tempfile
import urllib.parse
import urllib.request
import warnings
from pathlib import Path

import astropy.io.votable as vo
import numpy as np
from astroquery.vizier import Vizier
from scipy.constants import c as c_light
from scipy.interpolate import interp1d

warnings.filterwarnings("ignore", module="astropy.io.votable.tree")
warnings.filterwarnings("ignore", module="astropy.io.votable.xmlutil")
warnings.filterwarnings("ignore", module="scipy.interpolate.interp1d")

store_directory = Path(__file__).parent / "data"


def getSed(coord):
    r"""
    Extract SED from Vizier database.

    Parameters.
    -----------
    `coord` : {str}
        Coordinates of the target (format: RA DEC).

    Returns:
    --------
    `sed` : {dict}
        Dictionnary containing the SED informations (keys: 'Flux' ([Jy]), 'wl'
        (wavelength [µm]), 'Err' (uncertainties [Jy]), 'Catalogs' (Vizier catalogs name),
        'References' (references/publications)):
    """
    try:
        coord_ = coord.replace(" ", "+").replace("+-", "-")
        f = f"http://vizier.u-strasbg.fr/viz-bin/sed?-c={coord_}&-c.rs=1"
        # f = f"http://vizier.u-strasbg.fr/vizier/sed/?submitSimbad=Photometry&-c={coord_}&-c.r=1&-c.u=arcsec&show_settings=1"
        response = urllib.request.urlopen(f)
        with tempfile.TemporaryFile() as tmpfile:
            tmpfile.write(response.read())
            tab = np.ma.getdata(vo.parse_single_table(tmpfile).array)

        catalogs = [x for x in tab["_tabname"]]
        # references = getVizierRef(catalogs)

        cond = tab["sed_flux"] >= 0
        freq = tab["sed_freq"][cond]
        wl = c_light / (freq * 1e9) * 1e6
        flux = tab["sed_flux"][cond].astype(float)
        err = tab["sed_eflux"][cond].astype(float)

        data = {
            "Flux": list(flux),
            "Err": list(err),
            "wl": list(wl),
            "References": [],  # list(references),
            "Catalogs": list(catalogs),
        }
    except (urllib.request.HTTPError, Exception):
        # todo: logme
        data = None
    return data


def sed2mag(sed, bands):
    """
    Extract magnitude from interpolated SED.
    """
    conv_flux = {
        "B": {"wl": 0.44, "F0": 4260},
        "V": {"wl": 0.5556, "F0": 3540},  # Allen's astrophysical quantities
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

    with np.errstate(divide="ignore"):
        f_sed = interp1d(sed["wl"], np.log10(sed["Flux"]), bounds_error=False)

    l_m = np.full(len(bands), np.nan)
    for i, band in enumerate(bands):
        F = 10 ** (f_sed(conv_flux[band]["wl"]))
        F0 = conv_flux[band]["F0"]
        l_m[i] = -2.5 * np.log10(F / F0)
    return list(l_m)


def find_author_vizier(cat):
    """Search Vizier catalog with astroquery and find the reference
    in the description.

    Parameters:
    -----------
    `cat`: {str}
        Name of the catalog (e.g.: "I/337/gaia").

    Returns:
    --------
    `cat_ref`: {str}
        Name of the original publication of the catalog (e.g.: "Gaia Collaboration, 2016").

    """
    vizier_catalog = cat.split("/")[:-1]
    vizier_name = vizier_catalog[0]
    for j in range(len(vizier_catalog) - 1):
        vizier_name += "/%s" % vizier_catalog[j + 1]
    catalog_list = Vizier.find_catalogs(vizier_name)
    cat_desc = catalog_list[vizier_name].description
    i2 = -1
    while True:
        i = i2
        i2 = cat_desc.find("(", i2 + 1)
        if i2 == -1:
            break
    cat_ref = cat_desc[cat_desc.find("(", i) + 1 : cat_desc.find(")", i)]
    return cat_ref


def buildVizierRef(sed_name_cat, verbose=False):
    """Build the Vizier references list. For each search of new SED, check if new catalogs
    are detected and add the reference to the saved json file (default: 'vizier_catalog_naming.json').
    """
    stored_catalog_filepath = store_directory / "vizier_catalog_references.json"
    if Path(stored_catalog_filepath).is_file():
        with open(stored_catalog_filepath) as ofile:
            known_entries = json.load(ofile)
    else:
        known_entries = {}

    sed_name_cat_set = list(set(sed_name_cat))

    not_in_json = [x for x in sed_name_cat_set if x not in known_entries.keys()]
    if len(not_in_json) > 0:
        if verbose:
            print(
                "\nFetching new Vizier catalog references (%i) from the Vizier database."
                % (len(not_in_json))
            )

        for cat in not_in_json:
            cat_ref = find_author_vizier(cat)
            known_entries[cat] = cat_ref

        with open(stored_catalog_filepath, mode="w") as ofile:
            json.dump(known_entries, ofile)
    return known_entries


def getVizierRef(sed_name_cat, verbose=False):
    """Function to identify the references corresponding to each Vizier
    catalog included in the fetched SED.
    """
    known_entries = buildVizierRef(sed_name_cat, verbose=verbose)
    sed_name_ref = [known_entries.get(name, name) for name in sed_name_cat]
    return sed_name_ref
