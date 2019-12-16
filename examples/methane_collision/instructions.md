# Example: Methane collision

Trajectory of two methane molecules colliding is given in `traj.xyz`, calculated with a developmental reactive-GAP model. 

1. Produce the SOAP descriptor for them using ASAP. We are using n_max=6, 
l_max=8, atom_sigma=0.5 with a cutoff of 4.5A
    ```
    gen_soap_descriptors.py -fxyz traj.xyz --l 8 --n 6 --g 0.5 --periodic True --rcut 4.5 --peratom True
   ```
   This gives you a file named `ASAP-n6-l8-c4.5-g0.5.xyz` which contains the SOAP
   vectors in the arrays with label `"SOAP-n6-l8-c4.5-g0.5"`.
1. Produce PCA coordinates
    ```
   pca.py -fmat "SOAP-n6-l8-c4.5-g0.5" -fxyz ASAP-n6-l8-c4.5-g0.5.xyz --output xyz --peratom False
   ```
   This pops up a plot and saves png files of it, which you can look at as 
   reference later, to see that the output is similar.
   
   In addition, there is an xyz (`ASAP-pca-d10.xyz`) with the PCA coordinates for the first 10 PCA 
   dimensions. 
1. Use the visualiser! This needs to be in the current directory, so just link 
it here. 
    ```
    python visualize_plot.py
    ```
1. to see that the result is the same, choose `pca_coord_0` and `pca_coord_1` on the x and y axes respectively. You can also have the energy as marker colour.  
   