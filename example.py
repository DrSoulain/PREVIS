#!/usr/bin/env python
import previs

# Perform previs research on one object:
data = previs.search('Altair')

# Plot the observability from VLTI and CHARA
fig = previs.plot_VLTI(data)
fig.show()

fig = previs.plot_CHARA(data)
fig.show()

# Perform previs research on a list of stars:
stars = ['Betelgeuse', 'Altair']

survey = previs.survey(stars, namelist='survey_example')

# Count observable stars with each instruments (mode, telescope, spectral resolution, etc.)
result_survey = previs.count_survey(survey)

# Print the list of observable stars (resume):
result_survey.print_log()

# plot the histogram of the survey:
fig = previs.plot_histo_survey(result_survey)
fig.show()

