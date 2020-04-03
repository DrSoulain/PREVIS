# PREVIS: [P]ython [R]equest [E]ngine for [V]irtual [I]nterferometric [S]urvey

PREVIS is a module to easely know if an astronomical source is observable 
with the actual interferometric facilities in the world. It can perform
a single object research (previs_search) or a multiple object research (previs_survey).
This research take benefit of the Virtual Observatory (OV) to get useful informations as:
 
- Spectral Energy Distribution (SED) from Vizier (http://vizier.u-strasbg.fr/vizier/sed/). 
- Magnitudes: visible (V, R, G), near-infrared (J, H, K) and mid-infrared (L, M, N). The SED 
  is used to extract the missing magnitudes of Simbad (http://simbad.u-strasbg.fr/simbad/). 
  Especially L (3.5 µm), M (4.5 µm), and N (10 µm) magnitudes which are not often included 
  in the standard catalogs,
- Spectral type,
- Celestial coordinates,
- Gaia DR2 informations (if exist).

PREVIS compare the magnitudes to the current limiting magnitudes of each instruments to know if
the target is observable given the current performances. The actual instruments are installed at:

- The europeean Very Large Telescope Interferometer (VLTI, https://www.eso.org/sci/facilities/paranal/telescopes/vlti.html),
  with **PIONIER** (H band), **GRAVITY** (K band) and **MATISSE** (L, M, N bands),
- The American Center for Hight Angular Resolution Astronomy (CHARA, http://www.chara.gsu.edu), with 
  **VEGA** (V band), **PAVO** (R bands), **MIRC** (H band), **CLIMB** (K band) and **CLASSIC** (H, K bands).

PREVIS also use the V or G magnitudes to check the guiding issues or the tip/tilt correction limit. 
For the VLTI: If the star is too faint in G mag, PREVIS research the list of stars around
the target (57 arcsec) with the appropriate magnitude and give the list of celestial coordinates
usable as guiding star. Of course, PREVIS check also the on-site observability given the latitude of 
both observatory.


Recommandation for installation:
-------------------------------

From the downloaded directory PREVIS._version_.

Firstly, install dependencies using Conda. It's recommended to create a specific environment 
using (conda create -n env_name) but you can use your base env. If you don't use Conda, you can use pip instead.

In your Conda env (Conda activate env_name):

- Install python dependencies:
```
conda install --file requirements.txt 
```

Some dependencies are not in the general Conda channel, so use the command to specify the required channel:
```
conda install -c astropy astroquery
conda install -c conda-forge uncertainties
```

- Then, install previs package:
```
pip install .
```

Additionnal step:
----------------

On macOS (or Linux-like), additional visualisation libraries could be required. We use the Qt5Agg to show figures. If visualisation problems appear, you can run the following command to install gt5. If you don't want to use qt5, you can remove the line mpl.use('Qt5Agg') (l30) from example.py.
```
pip install PyQt5
```
PREVIS use also web requests, lxml could not be installed in your system. If so, an error can appear like "ImportError: lxml not found, please install it". It's can be fixed installing lxml:
```
pip install lxml
```

What can do PREVIS for you?:
----------------------------

An example script example.py is included to test the previs possibilities. The example include a single target
research using previs_search (from previs.core), a visualisation solution for the VLTI (plot_VLTI) and CHARA (plot_CHARA). 
The example also presents the survey possibility of previs. See example.py for details.
```
python example.py
```

For example, if you use previs_search (previs.core) to get informations about the star Altair, you can display the resulting observability with the VLTI instruments with plot_VLTI (previs.display):

![Figure 1](doc/figure_1.png)

On the Fig. [FIG1](doc/figure_1.png), you can see multiple informations:

- Upper right: appropriate magnitudes for the VLTI instruments,
- Upper left: the name of target with a green cirle if the star is observable from the VLTI, red if not,
- The green square at the bottom of the target indicate the information of the guiding star: if 'Science', the target is bright enought to be used as guiding star, if 'off axis', the coudé off-axis guiding need to be used. If 'off axis*', the coudé off-axis guiding can only be performed in visitor mode.
- The organigram of each instrument:
    - The blue/green octogone indicate the telescope (UT (8m) or AT (1.8m)),
    - The pink circle indicate if fringe tracker is used (GRA4MAT),
    - The colored squares indicates the observing bands (same color as magnitude),
    - The points indicates if the target is observable for each spectral resolution (low (LR), medium (MR) or high (HR)).
