
INSTALLATION:
-------------

In terminal, go in the downloaded directory PREVIS._version_.


Firstly, install dependencies using Conda. It's recommended to create a specific environment using (conda create -n env_name) but you can use your base env. If you don't use Conda, you can use pip instead.

In your Conda env (Conda activate env_name):

- Install python dependencies: 

conda install --file requirements.txt 


Some dependencies are not in the general Conda channel, so use the command to specify the required channel:

conda install -c astropy astroquery
conda install -c conda-forge uncertainties

- Then, install previs package:

pip install .


EXAMPLE:
--------

A example script example.py is included to test the previs possibilities. The example include a single target research using previs_search (from previs.core), a visualisation solution for the VLTI instruments with plot_VLTI and CHARA with plot_CHARA. The example also presents the survey possibility of previs.

python example.py


ADDITIONAL STEP:
----------------

On macOS (or Linux-like), additional visualisation libraries could be required. We use the Qt5Agg to show figures. If problems appear, you can run the two following commands to install gt5. If you don't want to use qt5, you can remove the line mpl.use('Qt5Agg') (l30) from previs.core.

pip install PyQt5

previs use also web request, lxml could not be included in your system. If so, an error can appear like "ImportError: lxml not found, please install it". It's can be fix installing lxml:

pip install lxml