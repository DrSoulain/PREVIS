#!/usr/bin/env python

import matplotlib as mpl
from matplotlib import pyplot as plt
from previs.core import previs_search, previs_survey
from previs.display import (count_survey, plot_CHARA, plot_histo_survey,
                            plot_VLTI, print_list_survey)
from termcolor import cprint

mpl.use('Qt5Agg')

print('test 1')

# Perform previs research on one object:
data = previs_search('Antares')

# Plot the observability from VLTI and CHARA (using output of previs_search).
plot_VLTI(data)
plot_CHARA(data)

# Perform previs research on a list of stars:
list_star = ['Betelgeuse', 'Altair']

survey = previs_survey(list_star, namelist='survey_example', upload=True)

# Count the observable star with each instruments (mode, telescope, spectral resolution, etc.)
result_survey, list_no_simbad = count_survey(survey)

# If some stars of the list are not in the Simbad database, they will appear here:
if len(list_no_simbad) > 0:
    cprint('Warning: some stars are not in Simbad:', 'red')
    print(list_no_simbad)

# Print the list of observable stars (resume):
print_list_survey(result_survey)

# plot the histogram of the survey:
plot_histo_survey(result_survey)

plt.show()
