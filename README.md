Visualizer for molecular structures/compounds from dimensionality reduction performed from ASAP.
Input is read from extended xyz files, written e.g. by ASE or ASAP 

## Dependencies:
 - Numpy
 - plotly, dash, dash_bio_utils
 - dash_bio (IMPORTANT: You need to install a modified version from https://github.com/chkunkel/dash-bio, contact us!)
 - pandas
 - rtools (theochem Munich, https://gitlab.lrz.de/theochem/rtools)
 - ASAP (https://github.com/BingqingCheng/ASAP, Ask BingqingCheng)
 - ASE (https://wiki.fysik.dtu.dk/ase/)
 
## HOWTO:

0) Edit the file config.txt (explanations provided therein)
1) Run python visualize_plot.py
2) To visualize the results:
   - Find the created webpage in your browser at: http://localhost:9999/

## Screenshot of the viewer in action

Visualization of MD-Snapshots (Water) using SOAP and PCA (performed in ASAP). Provided by @BingqingCheng

![alt text](example.png "Screenshot")

 
Authors: Christian Kunkel (christian.kunkel@tum.de), Simon Wengert (s.wengert@tum.de)
Licence so far: BY-SA
