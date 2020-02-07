Visualizer for molecular structures/compounds from dimensionality reduction performed from ASAP.

Input is read from extended xyz files, written e.g. by ASE or ASAP 

#### Screenshot of the viewer in action

Visualization of MD-Snapshots (Water) using SOAP and PCA (performed in ASAP). Provided by @BingqingCheng

![alt text](example.png "Screenshot")


#### Dependencies and installation:

Easiest way: Install miniconda first and then install all listed packages using conda. Tested only with python3, not python2!

 - Numpy
 - plotly, dash, dash_bio_utils
 - dash_bio (You need to install a modified version from https://github.com/chkunkel/dash-bio, contact us!)
 - pandas
 - ASAP (https://github.com/BingqingCheng/ASAP, Ask BingqingCheng)
 - ASE (https://wiki.fysik.dtu.dk/ase/)
 
#### Howto:

**Install:**
- locally 
```
# locally with setup.py
python setup.py install --record files.txt
# for uninstall: rm -r $(cat files.txt)
```
- with pip (when the repo will be public, or use ssh key magic)
```
pip install git+https://github.com/chkunkel/projection_viewer.git
```
This installs the pacakge `projection_viewer` and gives you two scripts: `visualise_plot` and `visualise_abcd_summary` 

**Use simple visualiser:**

Get an xyz file with the relevant data. For projections and clustering, the usage of [ASAP](https://github.com/BingqingCheng/ASAP) might be helpful for this.


`visualise_plot` should be in your path if you installed correctly
1. use `visualize_plot` with command line arguments, see `visualize_plot --help` for details.
1. from config:
    
    Edit the file config.txt (explanations provided therein)
    
   ```
    visualize_plot --config-file config.txt
    ```

Find the created webpage in your browser at: http://localhost:9999/ 

*NB. This is a dev server and do not use it for deployment, further dev is needed for proper deployment server.*
   
**Use visualiser with [ABCD](https://github.com/libatoms/abcd) integration:**
 
set up ABCD, see the original repo and documentation:
https://github.com/libatoms/abcd

run `visualise_abcd_summary` and dig in your database, then click 'Visualise' on the ABCD tab to take the chosen frames to the visualiser tab   

 

 
#### Authors: 

Christian Kunkel (christian.kunkel@tum.de)

Simon Wengert (s.wengert@tum.de)

Tamas K. Stenczel (tks32@cam.ac.uk)

Licence so far: BY-SA

