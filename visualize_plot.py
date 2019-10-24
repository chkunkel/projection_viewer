# This file is part of the projection_viewer.
# (C) 2019 Christian Kunkel

import os
import shutil
import configparser

import numpy as np
import pandas as pd

import ase.io
from ase.io import read

from bokeh.plotting import figure, output_file, show, save, ColumnDataSource
from bokeh.models import HoverTool, CustomJSHover, TapTool, CustomJS
from bokeh import events
import bokeh.io
from bokeh.models import LinearColorMapper, Ticker, ColorBar

from helpers import get_features_atomic, get_features_molecular
from tooltips import tooltips

config = configparser.ConfigParser()
config.read('config.txt')
extended_xyz_file =   config['Basic']['extended_xyz_file']
mode = config['Basic']['mode']
property_visualize = config['Basic']['property_visualize']
dimensions = config['Basic']['dimensions']
consider_species = config['Basic']['consider_species']
title = config['Basic']['title']


atoms = read(extended_xyz_file,':')

print('Writing molecules')
#if os.path.isdir('data_plot'):
#    shutil.rmtree('data_plot')
#os.mkdir('data_plot')
#[mol.write('data_plot/mol_{}.xyz'.format(i)) for i,mol in enumerate(atoms)]


if consider_species=='all':
    consider_species = list(set(atoms[0].get_chemical_symbols()))
else:
    consider_species = consider_species.split(',')


if mode =='atomic':
    Y = get_features_atomic(property_visualize, atoms, consider_species = consider_species)
    p_xyzs = [['mol_{}.xyz'.format(i)]*len(mol) for i,mol in enumerate(atoms)]
    p_xyzs = [item for sublist in p_xzys for item in sublist]
    atomic_numbers = [range(len(mol)) for mol in atoms]
    atomic_numbers = list(np.array(atomic_numbers).flatten())  
else:
    Y = get_features_molecular(property_visualize, atoms); atomic_numbers=[]
    p_xyzs = ['mol_{}.xyz'.format(i) for i,mol in enumerate(atoms)]
    atomic_numbers = [-1]*len(Y)


embedding_coordinates=np.array([mol.info['pca_coord'] for mol in atoms])


bokeh.io.output_file('index.html')


print("Layouting the final plot")


hover = HoverTool(tooltips=tooltips[mode])


TOOLS="crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"


p = figure(title=title, x_axis_label='dimension 1', y_axis_label='dimension 2',
           plot_width=900,plot_height=700,tools=[TOOLS, hover])


p.background_fill_color = "beige"


color_mapper = LinearColorMapper(palette='Viridis256', low=min(Y), high=max(Y))
#color_mapper = LinearColorMapper(palette='Spectral10', low=70, high=500)
#color_mapper = LinearColorMapper(palette='Viridis256', low=20, high=32)
# color_mapper = LinearColorMapper(palette='Viridis256', low=10, high=160)
# color_mapper = LinearColorMapper(palette='Viridis256', low=0, high=int(dict_config["color_high"]))  # SPW: dict_config["color_high"] was formally an int (e.g. 3)



source = ColumnDataSource({
    "index"     : range(len(Y)),
    "x1"  : embedding_coordinates[:, 0].tolist(),
    "x2"  : embedding_coordinates[:, 1].tolist(),
    "feature"  : Y,
    "p_xyzs": p_xyzs,
    "atomic_num": atomic_numbers})

r_circles=p.scatter("x1",
                    "x2",
                    size=4,
                    alpha=0.3,
                    source=source,
                    level="overlay",
                    line_width=4.5,
                    color={'field': 'feature', 'transform': color_mapper})


color_bar = ColorBar(color_mapper=color_mapper,
                     label_standoff=12, border_line_color=None, location=(0,0))
p.add_layout(color_bar, 'right')

callback_tap=CustomJS(args={"source":source},
                            code="""
               display_xyz(source.data['p_xyzs'][source.selected.indices], atomhighlight=source.data['atomic_num'][source.selected.indices])""")
taptool = p.select(type=TapTool)
taptool.callback = callback_tap

callback_hover = CustomJS(args={'title': p.title, "source":source}, code="""
    const indices = cb_data.index.indices;
    display_xyz(source.data['p_xyzs'][indices], atomhighlight=source.data['atomic_num'][indices])
    //title.text = 'Hovering over points: ' + source.data['p_xyzs'][indices];
""")
p.hover.callback = callback_hover


save(p)
#show(p)


# Add 3dmol.js

newfile=""
err=False


with open("index.html") as out:
    for line in out.readlines():
        if "3Dmol.csb" in line: err =True; break

        if "</head>" in line: continue
        if "<body>" in line:
            newfile+="""
                               <script src="http://3Dmol.csb.pitt.edu/build/3Dmol-min.js"></script>

          <style>
.mol-container {
  width: 500px;
  height: 500px;
  position: relative;
  border: 1px solid #999;
}

.align-center {
  width: 600px;
  margin: 20px auto 10px;
  text-align: center;
}
</style>


  </head>


  <body>



      <script>
      // Display a molecule/crystal using 3dmol.js and an http request
  function display_xyz(mol_xyz, atomhighlight=-1)
    {
  jQuery(function() {
  let element = $('#container-02');
  let config = { defaultcolors: $3Dmol.rasmolElementColors, backgroundColor: 'white' };
  let viewer = $3Dmol.createViewer( element, config );
  let pdbUri = 'http://localhost:8000/data_plot/'+mol_xyz;
    //let pdbUri = "https://3dmol.csb.pitt.edu/doc-data/1ycr.pdb";
    jQuery.ajax( pdbUri, {
      success: function(data) {
        let v = viewer;
        v.addModel( data, "xyz" );                       /* load data */
        v.setStyle({sphere:{radius:0.5}, stick: {}});  /* style all atoms */
        if (atomhighlight>-1)
        {
            // v.getModel(0).selectedAtoms({atomhighlight})
            var lines = data.split("\\n");
            for (var i=0; i<lines.length; i++)
            {
               if (i == atomhighlight+2)
               {
                   coord = lines[i].split(" ");
                   var x=parseFloat(coord[1]);
                   var y=parseFloat(coord[2]);
                   var z=parseFloat(coord[3]);
                   document.getElementById("container-03").innerHTML = atomhighlight+" "+coord[0]+" "+coord[1]+" " +coord[2]+" "+coord[3];

               }
            }
            //atoms=v.getModel(0).selectedAtoms([atomhighlight])
            v.addSphere( { center: {x:x, y:y, z:z}, radius:1.4, color:'green', wireframe: true } );
        }
        v.zoomTo();                                      /* set camera */
        v.render();                                      /* render scene */
        //v.zoom(1.2, 1000);                               /* slight zoom */
      },
      error: function(hdr, status, err) {
        console.error( "Failed to load PDB " + pdbUri + ": " + err );
      },
  })
})

    }

display_xyz('"""+p_xyzs[0]+"""');

</script>


 <table style="width:100%">
  <tr align="left">
    <td valign="top"> <div>
            3D-Model:<br>
            <div id="container-02" class="mol-container"></div>
           </div>
           <div id="container-03"></div>
           </div>

    </td>
    <th>


            """; continue

        if "<\body>" in line:
            newfile+="""
            </td></tr></table>
            </body>
            """
            continue

        newfile+=line

if not err:
    with open("index.html","w") as out:
        out.write(newfile)
else:
    print(err)

print("")
print("Finished generating plot, please follow these steps now (in the directory of this script):")
print("1) Start a webserver using 'python -m SimpleHTTPServer' for python2 or 'python -m http.server' for python3")
print("2) Open http://localhost:8000/ in your webbrowser")
