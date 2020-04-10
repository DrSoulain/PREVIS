#!/usr/bin/env python
import previs

# Perform previs research on one object:
data = previs.search('Altair')

# data contains informations stored as dictionnary. For 
# instance, you can retrieve the magnitudes typing:
mag = data['Mag']

# Plot the observability from VLTI and CHARA
fig = previs.plot_VLTI(data)
fig.show()

fig = previs.plot_CHARA(data)
fig.show()

# Perform previs research on a list of stars:
stars = ['Betelgeuse', 'Altair', 'WR112', 'WR104', 'HD100203']

survey = previs.survey(stars)

# The previs.search on one star can take up 30 sec, you may want to
# save the result of previs.search to be used later. It can be saved 
# as json file (named 'mysurvey') with:
previs.save(survey, 'mysurvey', overwrite=True)

# If a previous survey is saved, you can load it with:
my_saved_survey = previs.load('mysurvey')

# Survey contains data for each stars, we want to know the exact number
# of stars observable with each instruments. So, use previs.count_survey
# to generate the list of observable stars by instruments, mode and telescope.
count_survey = previs.count_survey(survey)

# Print the list of observable stars (resume):
count_survey.print_log()

# plot the histogram of the observable stars (survey.count):
fig = previs.plot_histo_survey(count_survey)
fig.show()
