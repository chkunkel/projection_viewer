import glob

from setuptools import setup, find_packages

description = 'Plotly app for viewing of atomistic data'

setup(name='projection_viewer',
      packages=find_packages(),  # ['projection_viewer'],
      scripts=['scripts/visualize_plot',
               'scripts/visualize_abcd'],
      keywords='ase, database, dash, plotly, dash_bio',
      version='0.1.0',
      description=description,
      long_description=description,
      author='Christian Kunkel, Simon Wengert, Tamas K Stenczel',
      author_email='christian.kunkel@tum.de, s.wengert@tum.de, tks32@cam.ac.uk',
      url='',
      project_urls={
          'Source Code': 'https://github.com/chkunkel/projection_viewer',
      },
      install_requires=['ase', 'dash_bio', 'numpy', 'pandas', 'dash', 'plotly'],
      data_files=[('assets', glob.glob('projection_viewer/assets/*.css')), ]
      )
