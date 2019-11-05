# This file is part of the projection_viewer.
# (C) 2019 Christian Kunkel

import os
import shutil
import configparser
import argparse

import itertools as ito
import numpy as np
import pandas as pd

import ase.io
from ase.io import read

from bokeh.plotting import figure, output_file, show, save, ColumnDataSource
from bokeh.models import HoverTool, CustomJSHover, TapTool, CustomJS
from bokeh import events
import bokeh.io
from bokeh.models import LinearColorMapper, Ticker, ColorBar

import helpers
import tooltips


# command-line adjustments
parser = argparse.ArgumentParser()
parser.add_argument( \
        '--x_axis',
        help = 'Dimension used on x-axis',
        default=1,
        type = int)
parser.add_argument( \
        '--y_axis',
        help = 'Dimension used on y-axis',
        default=2,
        type = int)
args = parser.parse_args()



# read config
config = configparser.ConfigParser()
config.read('config.txt')
extended_xyz_file =   config['Basic']['extended_xyz_file']
mode = config['Basic']['mode']
coord_key = config['Basic']['coord_key']
property_visualize = config['Basic']['property_visualize']
dimensions = config['Basic']['dimensions']
consider_species = config['Basic']['consider_species']
title = config['Basic']['title']


# read atoms
atoms = read(extended_xyz_file,':')


# collect data
if '[' in consider_species:
    consider_species = list(consider_species)
elif consider_species == 'all':
    consider_species = list(set(ito.chain(*[atoms_i.get_chemical_symbols() for atoms_i in atoms])))
else:
    consider_species = str(consider_species)

if mode =='atomic':
    feature = helpers.get_features_atomic(property_visualize, atoms, consider_species = consider_species)
    p_xyzs = list(ito.chain(*[['mol_{}.xyz'.format(idx)]*len(mol) for idx, mol in enumerate(atoms)]))
    mols = list(ito.chain(*[[mol]*len(mol) for idx, mol in enumerate(atoms)]))
    # p_xyzs = [item for sublist in p_xzys for item in sublist]
    atomic_numbers = [range(len(mol)) for mol in atoms]
    atomic_numbers = list(np.array(atomic_numbers).flatten())
    # atomic_numbers = helpers.get_features_atomic('numbers', atoms, consider_species)
    embedding_coordinates = np.asarray(helpers.get_features_atomic(coord_key, atoms, consider_species))
elif mode in ['compound', 'generic']:
    feature = helpers.get_features_molecular(property_visualize, atoms)
    p_xyzs = ['mol_{}.xyz'.format(idx) for idx in range(len(atoms))]
    mols = [mol for mol in atoms]
    atomic_numbers = [-1]*len(feature)
    embedding_coordinates = np.asarray(helpers.get_features_molecular(coord_key, atoms))


# write molecules
print('Writing molecules')
if os.path.isdir('data_plot'):
    shutil.rmtree('data_plot')
os.mkdir('data_plot')
for p_xyz_i, mol_i in zip(p_xyzs, mols):
    ase.io.write(os.path.join('data_plot', p_xyz_i), mol_i)


# prepare visualization
print("Layouting the final plot")

bokeh.io.output_file('index.html')
hover = HoverTool(tooltips=tooltips.tooltips[mode])
TOOLS = "crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"

p = figure(
        title = title,
        x_axis_label = 'Dimension 1',
        y_axis_label = 'Dimension 2',
        plot_width = 900,
        plot_height = 700,
        tools = [TOOLS, hover],
        )
p.background_fill_color = 'beige'
color_mapper = LinearColorMapper(palette='Viridis256', low=min(feature), high=max(feature))

source = ColumnDataSource({
    'index'      :  range(len(feature)),
    'x1'         :  embedding_coordinates[:, args.x_axis].tolist(),
    'x2'         :  embedding_coordinates[:, args.y_axis].tolist(),
    'feature'    :  feature,
    'p_xyzs'     :  p_xyzs,
    'atomic_num' :  atomic_numbers,
    })

r_circles = p.scatter(
        'x1',
        'x2',
        size = 4,
        alpha = 0.3,
        source = source,
        level = 'overlay',
        line_width = 4.5,
        color = {'field': 'feature', 'transform': color_mapper},
        )

color_bar = ColorBar(
        color_mapper = color_mapper,
        label_standoff = 12,
        border_line_color = None,
        location = (0,0)
        )
p.add_layout(color_bar, 'right')

code = """
display_xyz(source.data['p_xyzs'][source.selected.indices], atomhighlight=source.data['atomic_num'][source.selected.indices])
"""[1:-1]
callback_tap = CustomJS(
        args = {"source":source},
        code = code,
        )
taptool = p.select(type=TapTool)
taptool.callback = callback_tap

code="""
const indices = cb_data.index.indices;
display_xyz(source.data['p_xyzs'][indices], atomhighlight=source.data['atomic_num'][indices])
//title.text = 'Hovering over points: ' + source.data['p_xyzs'][indices];
"""[1:-1]
callback_hover = CustomJS(
        args = {'title': p.title, "source":source},
        code = code,
        )
p.hover.callback = callback_hover

save(p)


# Add 3dmol.js
newfile = ''
err = False


with open("index.html") as out:
    for line in out.readlines():

        if "3Dmol.csb" in line:
            err = True
            break

        if "</head>" in line:
            continue
        if "<body>" in line:
            newfile += """
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
            newfile += """
            </td></tr></table>
            </body>
            """
            continue

        newfile += line

if not err:
    with open("index.html","w") as out:
        out.write(newfile)
else:
    print(err)

print("")
print("Finished generating plot, please follow these steps now (in the directory of this script):")
print("1) Start a webserver using 'python -m SimpleHTTPServer' for python2 or 'python -m http.server' for python3")
print("2) Open http://localhost:8000/ in your webbrowser")
