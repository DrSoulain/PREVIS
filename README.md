# PREVIS
(**P**ython **R**equest **E**ngine for **V**irtual **I**nterferometric **S**urvey)

[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)

PREVIS is a Python module that provides functions to help determine the observability of astronomical sources
in a few lines of code.
One can perform a single object search (`previs.search`) or a multiple-objects search (`previs.survey`).
These functions use data from the Virtual Observatory (OV), such as:
 
- Spectral Energy Distribution (SED) from [Vizier](http://vizier.u-strasbg.fr/vizier/sed/). 
- Magnitudes: visible (V, R, G), near-infrared (J, H, K) and mid-infrared (L, M, N). The SED 
  is used to extract the missing magnitudes of [Simbad](http://simbad.u-strasbg.fr/simbad/). 
  Especially L (3.5 µm), M (4.5 µm), and N (10 µm) magnitudes which are not often included 
  in the standard catalogs,
- Spectral type,
- Celestial coordinates,
- Gaia DR2 informations (if available).

PREVIS compares the magnitudes to the current limiting magnitudes of each instruments to determine whether
the target is observable with current performances. The actual instruments are installed at:

- The european [Very Large Telescope Interferometer](VLTI, https://www.eso.org/sci/facilities/paranal/telescopes/vlti.html),
  with **PIONIER** (H band), **GRAVITY** (K band) and **MATISSE** (L, M, N bands),
- The American Center for Hight Angular Resolution Astronomy ([CHARA](http://www.chara.gsu.edu)), with 
  **VEGA** (V band), **PAVO** (R bands), **MIRC** (H band), **CLIMB** (K band) and **CLASSIC** (H, K bands).

PREVIS also uses the V or G magnitudes to check the guiding issues or the tip/tilt correction limit. 
For the VLTI: if the star is too faint in G mag, PREVIS will look for the list of stars around
the target (57 arcsec) with the appropriate magnitude and give the list of celestial coordinates
usable as guiding star. Of course, PREVIS checks also the on-site observability given the latitude of 
both observatories.


## What can PREVIS do for you?

An example script [example.py](example.py) is included to test the possibilities offered by PREVIS. The example includes a single target
research using `previs.search`, a visualisation solution for the VLTI (`previs.plot_VLTI`) and CHARA (`previs.plot_CHARA`). 
The example also presents the survey capabilities of the module.

For instance, if you use `previs.search` to fetch data about the star Altair, you can display the resulting observability with the VLTI instruments with `previs.plot_VLTI`:

![Figure 1](doc/figure_1.png | width=100)

Such a graph represents multiple informations:

- *Upper left*: the name of the target with a green cirle if the star is observable from the VLTI, red if not,
- *Upper right*: appropriate magnitudes for the VLTI instruments,
- The round square at the bottom of the target indicate the information of the guiding star: 
  - 'Science': the target is bright enought to be used as guiding star, 
  - 'off axis': the coudé off-axis guiding need to be used,
  - 'off axis*', the coudé off-axis guiding can only be performed in visitor mode.
- The organigram of each instrument:
    - The blue/green octogone indicate the telescope (UT (8m) or AT (1.8m)),
    - The pink circle indicate if fringe tracker is used (GRA4MAT),
    - The colored squares indicates the observing bands (same color as magnitudes),
    - The right circles are green if the target is observable for each spectral resolution (low (LR), medium (MR) or high (HR)), red if not.


## Install from source (for conda-based systems)

It is recommended (though not mandatory) to create a separate environment with `conda create -n <env_name>`.
Then, within your Conda env (`conda activate <env_name>`):

```bash
cd PREVIS/

# Install main dependencies
conda install --file requirements.txt

# Some dependencies are not in the general Conda channel,
# so we specify the desired channels
conda install -c astropy astroquery
conda install -c conda-forge uncertainties

# Finally, install PREVIS
pip install .
```