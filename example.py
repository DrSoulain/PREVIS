#!/usr/bin/env python
import previs

# Perform previs research on one object:
data = previs.search("Altair", verbose=True)

# data contains informations stored as dictionnary. You can
# read the api_reference.md to get all detailled informations
# or the docstring of previs.search. For instance:
magL = data["Mag"]["magL"]  # If you want to get the L magnitudes.
# The Spectral Energy Distribution from Vizier (Flux [Jy] and wl [µm])
wl, Flux = data["SED"]["wl"], data["SED"]["Flux"]
distance = data["Gaia_dr2"]["Dkpc"]  # The Gaia DR2 distance [kpc]

# You can save the data as json file (named mydata_Altair) with:
previs.save(data, "mydata_Altair", overwrite=True)

# And load it later with:
data_altair = previs.load("mydata_Altair")

# If you want to know if you can observe the star Altair with
# the different instrument of the VLTI, you can plot the synthetic
# result with:
fig = previs.plot_VLTI(data)
fig.show()

# Or with CHARA:
fig = previs.plot_CHARA(data)
fig.show()

# If you want to know indidually the observability or your target, for instance,
# MATISSE with the AT, without fringe tracking, in L-band and in
# low spectral resolution, you can type:
observability_mat = data["Ins"]["MATISSE"]["AT"]["noft"]["L"]["LR"]

# You can also perform previs.search on a list of stars using previs.survey
list_stars = ["Betelgeuse", "Altair", "WR112", "WR104", "HD100203"]
survey = previs.survey(list_stars)

# The previs.search on one star can take up to 30 sec, you may want to
# save the result of previs.survey to be used later. It can be saved
# and retrieved as before with:
previs.save(survey, "mysurvey", overwrite=True)
my_saved_survey = previs.load("mysurvey")

# Survey contains data for each stars, we want to know the exact number
# of stars observable with each instruments. So, use previs.count_survey
# to generate the list of observable stars by instruments, mode and telescope.
count_survey = previs.count_survey(my_saved_survey)

# Print the list of observable stars (resume):
count_survey.print_log()

# plot the histogram of the observable stars:
fig = previs.plot_histo_survey(count_survey, plot_HR=True)
# plot_HR is set as True to plot high spectral resolution informations (default=False)

fig.show()
