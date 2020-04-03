# PREVIS
(**P**ython **R**equest **E**ngine for **V**irtual **I**nterferometric **S**urvey)

[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)

PREVIS is a module to easily determine whether an astronomical source is observable 
with the current interferometric facilities in the world. It can perform
a single object research (`previs_search`) or a multiple object research (`previs_survey`).
This search uses data from the Virtual Observatory (OV), such as:
 
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
For the VLTI: if the star is too faint in G mag, PREVIS will research the list of stars around
the target (57 arcsec) with the appropriate magnitude and give the list of celestial coordinates
usable as guiding star. Of course, PREVIS checks also the on-site observability given the latitude of 
both observatory.


## Installation (for conda-based systems)

It is recommended (though not mandatory) to create a seperate environment with `conda create -n <env_name>`.
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
# alternatively, to install in dev mode
conda develop .
```

### troubleshooting

On UNIX systems (Linux, macOS), additional visualisation libraries could be required. We use the Qt5Agg to display figures. If visualisation problems appear, you can run the following command to install gt5. If you do not want to use qt5, you can remove the line mpl.use('Qt5Agg') (l30) from [example.py](example.py) .
```bash
pip install PyQt5
```
PREVIS also uses web requests, lxml may not be installed in your system. If so, this error can appear
```python
ImportError: lxml not found, please install it
```
It is fixed by installing lxml
```bash
conda install lxml
# or
pip install lxml
```

## What can PREVIS do for you?

An example script [example.py](example.py) is included to test the possibilities offered by PREVIS. The example includes a single target
research using `previs.core.previs_search`, a visualisation solution for the VLTI (`previs.display.plot_VLTI`) and CHARA (`previs.display.plot_CHARA`). 
The example also presents the survey capabilities of the module.

For instance, if you use `previs_search` to fetch data about the star Altair, you can display the resulting observability with the VLTI instruments with `plot_VLTI`:

![Figure 1](doc/figure_1.png)

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
