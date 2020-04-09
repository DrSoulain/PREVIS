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
stars = ['Betelgeuse', 'Altair', 'WR112', 'WR104', 'HD100203']

survey = previs.survey(stars)

# The survey can be saved as json file (named 'mysurvey') to be reused:
previs.save_survey(survey, 'mysurvey', overwrite=True)

# If a previous survey is saved, you can load it with:
my_saved_survey = previs.load_survey('mysurvey')

# Count observable stars with each instruments (mode, telescope, etc.):
count_survey = previs.count_survey(survey)

# Print the list of observable stars (resume):
count_survey.print_log()

# plot the histogram of the observable stars (survey.count):
fig = previs.plot_histo_survey(count_survey)
fig.show()
