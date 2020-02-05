# Quickstart for plotting tools

```
# clone working
git clone git@github.com:stenczelt/ASAP.git
git clone git@github.com:stenczelt/projection_viewer.git

# and the ones for installation
git clone git@github.com:chkunkel/dash-bio.git
git clone git@github.com:plotly/dash-bio-utils.git

#make a copy environement::
conda create --name tum_test --clone quip_env
conda activate tum_test

# conda installs: plotly, dash and dscribe
conda install -c plotly plotly -n tum_test
conda install -c dash -n tum_test
conda install -c conda-forge dscribe -n tum_test

# dash-bio-utils install (cloned above)
cd dash-bio-utils
python setup.py install
cd ../

# dash-bio fork install (cloned above)
cd dash-bio
python setup.py install
cd ../


```