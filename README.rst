PREVIS: Python Request Engine for Virtual Interferometric Survey
================================================================

Previs is a module to easely get the observability of a target or a
list of targets with the different beam combiners from the VLTI and 
CHARA interferometers. Previs perform a research in the Virtual
Observatory (OV) to get useful informations as:
- Spectral Energy Distribution (SED) from Vizier (). The SED is used to
 extract magnitudes (especially L, M, and N mag which are not often included in the 
standard catalogs),
- Gaia DR2 distances.

Previs compare these magnitudes to the current limiting magnitudes
of each instruments. It also use the V or G magnitudes to check the
guiding issues or the tip/tilt correction limit. For the VLTI: If 
the star is too faint in G mag, Previs research the list of stars around
the target (57 arcsec) with the appropriate magnitude and give the
list of celestial coordinates usable as guiding star. Of course,
previs check also the on-site observability given the latitude of 
both observatory.


Recommandation for installation:
-------------------------------

In the terminal, go in the downloaded directory PREVIS._version_.

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

Example:
--------

An example script example.py is included to test the previs possibilities. The example include a single target
research using previs_search (from previs.core), a visualisation solution for the VLTI (plot_VLTI) and CHARA (plot_CHARA). 
The example also presents the survey possibility of previs. See example.py for details.

>> python example.py


