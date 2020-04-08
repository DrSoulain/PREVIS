# -*- coding: utf-8 -*-
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


def save_survey(survey, survey_file):
    """ Save the survey as json file named survey_file.json. """
    with open(survey_file + '.json', mode='wt') as ofile:
        json.dump(survey, ofile)


def load_survey(survey_file):
    """ Load the survey from the json file named survey_file.json. """
    # if Path(survey_file + 'json').is_file():
    with open(survey_file + '.json', mode='rt') as ofile:
        survey = json.load(ofile)
    # else:
    #    print('Error: %s.json does not exist.'%survey_file)
    #    survey = None
    return survey


def add_vs_mode_matisse(out, dic, star, cond_VLTI, cond_guid):
    """ Small function for count_survey. Counts MATISSE observability for each mode."""
    for tel in ['AT', 'UT']:
        for ft in ['noft', 'ft']:
            for band in ['L', 'N']:
                for res in ['LR', 'HR']:
                    cond_ins = out[star]['Ins']['MATISSE'][tel][ft][band][res]
                    if cond_VLTI and cond_guid and cond_ins:
                        dic['MATISSE'][tel][ft][band][res].append(star)
    return dic


def add_vs_mode_gravity(out, dic, star, cond_VLTI, cond_guid):
    """ Small function for count_survey. Counts GTAVITY observability for each mode."""
    for tel in ['AT', 'UT']:
        for res in ['MR', 'HR']:
            cond_ins = out[star]['Ins']['GRAVITY'][tel]['K'][res]
            if cond_VLTI and cond_guid and cond_ins:
                dic['GRAVITY'][tel][res].append(star)
    return dic


def count_survey(survey):
    """ Count the number of star observable with each HRA instrument."""
    list_star = survey.keys()
    n_star = len(list_star)

    n_chara, n_vlti = 0, 0
    for x in list_star:
        if survey[x]['Simbad']:
            if not survey[x]['SED'] is None:
                if survey[x]['Observability']['VLTI']:
                    n_vlti += 1
                if survey[x]['Observability']['CHARA']:
                    n_chara += 1

    colored('\nYour list contain %i stars:' % n_star, 'cyan')
    colored('-------------------------', 'cyan')
    print('Observability: %i (%2.1f %%) from the VLTI, %i (%2.1f %%) from the CHARA.\n' %
          (n_vlti, 100*float(n_vlti)/n_star, n_chara, 100*float(n_chara)/n_star))

    dic = SurveyClass({'MATISSE': {'UT': {'noft': {'L': {'LR': [], 'HR': []}, 'N': {'LR': [], 'HR': []}},
                                          'ft': {'L': {'LR': [], 'HR': []}, 'N': {'LR': [], 'HR': []}}
                                          },
                                   'AT': {'noft': {'L': {'LR': [], 'HR': []}, 'N': {'LR': [], 'HR': []}},
                                          'ft': {'L': {'LR': [], 'HR': []}, 'N': {'LR': [], 'HR': []}}
                                          },
                                   },
                       'GRAVITY': {'UT': {'MR': [],
                                          'HR': []},
                                   'AT': {'MR': [],
                                          'HR': []}
                                   },
                       'PIONIER': [],
                       'PAVO': [],
                       'CLASSIC': {'V': [], 'H': [], 'K': []},
                       'CLIMB': [],
                       'MYSTIC': [],
                       'MIRC': {'H': [], 'K': []},
                       'VEGA': {'LR': [], 'MR': [], 'HR': []},
                       })

    list_no_simbad = []
    for star in list_star:
        if survey[star]['Simbad']:
            if type(survey[star]['Guiding_star']) == list:
                if (len(survey[star]['Guiding_star'][0]) > 0) or (len(survey[star]['Guiding_star'][1]) > 0):
                    guid = True
                else:
                    guid = False
            elif survey[star]['Guiding_star'] == 'Science star':
                guid = True
            else:
                guid = False

            cond_VLTI = survey[star]['Observability']['VLTI']
            cond_guid = guid
            cond_CHARA = survey[star]['Observability']['CHARA']
            cond_tilt = survey[star]['Ins']['CHARA']['Guiding']

            dic = add_vs_mode_matisse(survey, dic, star, cond_VLTI, cond_guid)
            dic = add_vs_mode_gravity(survey, dic, star, cond_VLTI, cond_guid)

            cond_ins = survey[star]['Ins']['PIONIER']['H']
            if (cond_VLTI and cond_guid and cond_ins):
                dic['PIONIER'].append(star)

            for band in ['H', 'K']:
                cond_ins = survey[star]['Ins']['CHARA']['MIRC'][band]

                if (cond_CHARA and cond_ins and cond_tilt):
                    dic['MIRC'][band].append(star)

            for res in ['LR', 'HR']:
                cond_ins = survey[star]['Ins']['CHARA']['VEGA'][res]
                if (cond_CHARA and cond_ins and cond_tilt):
                    dic['VEGA'][res].append(star)

            for band in ['V', 'H', 'K']:
                cond_ins = survey[star]['Ins']['CHARA']['CLASSIC'][band]
                if (cond_CHARA and cond_ins and cond_tilt):
                    dic['CLASSIC'][band].append(star)

            if (cond_CHARA and survey[star]['Ins']['CHARA']['PAVO']['R'] and cond_tilt):
                dic['PAVO'].append(star)

            if (cond_CHARA and survey[star]['Ins']['CHARA']['MYSTIC']['K'] and cond_tilt):
                dic['MYSTIC'].append(star)

            if (cond_CHARA and survey[star]['Ins']['CHARA']['CLIMB']['K'] and cond_tilt):
                dic['CLIMB'].append(star)
        else:
            list_no_simbad.append(star)

    if list_no_simbad:
        colored('Warning: some stars are not in Simbad:', 'red')
        print(list_no_simbad)
    dic["unavailable"] = list_no_simbad
    return dic


class SurveyClass(dict):
    def print_log(self):
        res = '\n'.join([
            colored('VLTI:', 'green'),
            colored('-----', 'green'),
            'MATISSE (AT): %s' % str(self['MATISSE']['AT']['noft']['L']['LR']),
            '        (UT): %s' % str(self['MATISSE']['UT']['noft']['L']['LR']),
            'GRAVITY (AT): %s' % str(self['GRAVITY']['AT']['MR']),
            '        (UT): %s' % str(self['GRAVITY']['UT']['MR']),
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
        print(res)
        return res
