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


#### Usage in docker
Currently a manual uploaded image is available, that was built on 7/2/2020 by Tamas K. Stenczel.
To access it:
1. pull the image
    ```
    docker pull stenczelt/projection-abcd:latest
    ```
2. create a docker network, which enables the containers to communicate with each other and the outside world as well 
    ```
    docker network create --driver bridge abcd-network
    ```
3. run the mongo (ABCD) and the visualiser as well
    ```
    docker run -d --rm --name abcd-mongodb-net -v <path-on-your-machine-to-store-database>:/data/db -p 27017:27017 --network abcd-network mongo
    docker run -it --rm --name visualiser-dev -p 9999:9999 --network abcd-network stenczelt/projection-abcd
    ```
    NB: You need a a directory where the database files are kept locally and you need to connect this to the mongo 
    container. More info about this can be found in the original ABCD repo
    
This will start the visualiser with ABCD integration! Have fun!

After usage, for cleanup:
```
docker stop visualiser-dev abcd-mongodb-net         # stop the containers
docker rm visualiser-dev abcd-mongodb-net           # remove them if --rm did not
docker network rm abcd-network                      # remove the docker network
``` 
 
#### Authors: 

Christian Kunkel (christian.kunkel@tum.de)

Simon Wengert (s.wengert@tum.de)

Tamas K. Stenczel (tks32@cam.ac.uk)

Licence so far: BY-SA

