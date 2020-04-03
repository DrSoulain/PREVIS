PREVIS: Python Request Engine for Virtual Interferometric Survey
================================================================

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

- Europeean Very Large Telescope Interferometer (VLTI, https://www.eso.org/sci/facilities/paranal/telescopes/vlti.html),
  with PIONIER (H band), GRAVITY (K band) and MATISSE (L, M, N bands).
- American Center for Hight Angular Resolution Astronomy (CHARA, http://www.chara.gsu.edu), with 
  VEGA (V band), PAVO (R bands), MIRC (H band), CLIMB (K band) and CLASSIC (H, K bands).

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

>> conda install --file requirements.txt 

Some dependencies are not in the general Conda channel, so use the command to specify the required channel:

>> conda install -c astropy astroquery
>> conda install -c conda-forge uncertainties

- Then, install previs package:

>> pip install .

Additionnal step:
----------------

On macOS (or Linux-like), additional visualisation libraries could be required. We use the Qt5Agg to show figures. If problems appear, you can run the two following commands to install gt5. If you don't want to use qt5, you can remove the line mpl.use('Qt5Agg') (l30) from previs.core.

>> pip install PyQt5

previs use also web request, lxml could not be included in your system. If so, an error can appear like "ImportError: lxml not found, please install it". It's can be fix installing lxml:

>> pip install lxml

Example use of PREVIS:
----------------------

An example script example.py is included to test the previs possibilities. The example include a single target
research using previs_search (from previs.core), a visualisation solution for the VLTI (plot_VLTI) and CHARA (plot_CHARA). 
The example also presents the survey possibility of previs. See example.py for details.

>> python example.py


