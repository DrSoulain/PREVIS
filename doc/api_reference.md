# PREVIS's public api reference

## Core functions

`previs.search`: This function is the core of previs, it use the Virtual Observatory (VO) to get multiple informations about a star. The star magnitudes are compared to the limiting magnitudes of each HRA instruments to determine if the target is observable. Previs check also the general observing limitations as guiding performance and tip/tilt correction using V, R and G magnitudes.

```python
import previs

data = previs.search('Altair')

# What is inside data:
print(data.keys())
# return: dict_keys(['Simbad', 'Ins', 'Name', 'Coord', 'Distance', 
# 'sp_type', 'SED', 'Mag', 'Gaia_dr2', 'Guiding_star', 'Observability'])

# data['Simbad'] contains a boolean, True if the star is in Simbad, 
# False if not.
print(data['Simbad']) # return True

# data['Name'] is the name of the star.
print(data['Name']) # return Altair

# data['Coord'] are the celestial coordinates.
print(data['Coord']) # return 19 50 46.9985 +08 52 05.956

# data['Mag'] contains the magnitudes:
print(data['Mag']['magV'], data['Mag']['magH']) # return 0.752, 0.243
```

`previs.survey`: This function perform the `previs.search` on a list of stars.

## Saving/loading results from previous runs

Results from `previs.survey` can be exported to, and read back from json.

`previs.save_survey`: Save the results of `previs.survey` to an easely accessible json file. The survey process can take a long time (between 10 and 30s for each stars), do not forget to save the survey results if your sample is large.

`previs.load_survey`: Load the json file containing a previous survey saved with `previs.save_survey`.

## Plotting functions

These functions are used to present a synthetic resume of the `previs.search` or `previs.survey` results. The first application of previs is to know quickly the observability of a star, so the following functions will often be used to display the results of previs.

`previs.plot_VLTI`: Fonction to plot the observability of a star with each instruments installed at the VLTI array. The structure of the figure is discussed in the [README.md](README.md) file. **Tips**: a green point/circle indicate that your star in ready to be observed.

`previs.plot_CHARA`: Same as `previs.plot_VLTI` for the american interferometer CHARA.

`previs.plot_histo_survey`: Fonction to present the results from `previs.survey` as an histogram. All implimented instruments are included (from VLTI and CHARA). An example is presented in the [README.md](../README.md) and in the [Fig. 2](figure_2.jpeg).
