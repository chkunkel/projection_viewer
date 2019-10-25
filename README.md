Author: Christian Kunkel
(add your name if you contributed)

Visualizer for molecular structures/compounds from dimensionality reduction performed from ASAP

## Dependencies:
 - Numpy
 - matplotlib
 - bokeh
 - pandas
 - rtools (theochem Munich, https://gitlab.lrz.de/theochem/rtools)
 - ASAP (https://github.com/BingqingCheng/ASAP, Ask BingqingCheng)
 
## HOWTO:

0) Edit the file config.txt (explanations provided therein)
1) Run python visualize_plot.py
2) To visualize the results:
   - python -m SimpleHTTPServer &    (for python2, this will start a local webserver on your machine )
   - python -m http.server &    (for python3 this will start a local webserver on your machine )
   - Find the created webpage in your browser at: http://localhost:8000/

 
Licence so far: BY-SA
