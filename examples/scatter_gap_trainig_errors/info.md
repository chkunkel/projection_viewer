# scatter GAP predictions 

Given a training set for GAP (energies and forces with CP2K) and the predictions of the potential on that set, we would like to look at the distribution energy predictions, click on outliers to see them in tne viewer.

Processing code depends on another private repo of mine, so the output of that is given as well to run the visualiser on. 

```
ipython
>>> import projection_viewer
>>> projection_viewer.processors.gap_errors.ener_errors('train.xyz', 'train_predictions.xyz') 

visualize_plot --fxyz processed.xyz --mode molecular
```