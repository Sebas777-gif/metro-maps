# Metro Maps on Octilinear Grid Graphs

## Project Description

Schematic "metro maps" are important to create visualizations of public transit networks that are easy to read and convey the necessary information. The de facto standard layout used today is a so-called octilinear design using horizontal, vertical and diagonal line segments, which was proposed by Harry Beck in 1931 for the London subway. These maps are even today still drawn manually; and since the network structure might change regularly, it is of high interest to render them automatically instead.

## Used Data

The focus of the project was on the data of the RAB network, which is freely available in the GTFS format here: https://www.nvbw.de/open-data/fahrplandaten/fahrplandaten-ohne-liniennetz

In particular, the data of the _Stadtbus Ravensburg Weingarten_ (town bus of Ravensburg and Weingarten) was used, which was obtained from the data by reading in the routes with an ID that matches the regex `7-3(0(1|3|[4-7]|9)|1(0|1|4|5)|2(0|1))`.

## Running the calculations

Extract the zipped GTFS data into the folder `gtfs`. Then run the following command:

```
python -m main $GRIDS $SCALE $SEARCH_RADIUS $BEND_FACTOR $GEO_PENALTY
```

The resulting grid graph and color graph are then stored in a `pickle` file.

The parameters do the following:

* `GRIDS`: Number of cells used in the base grid.
* `SCALE`: Relevant for plotting. Higher numbers mean larger pictures.
* `SEARCH_RADIUS`: The search radius in the optimization step. Higher numbers should theoretically lead to better results, but runtime inreases exponentially.
* `BEND_FACTOR`: All bend penalties are multiplied by this factor.
* `GEO_PENALTY`: All geographical penalties are multiplied by this factor.

The last two parameters in combination can be used to prefer geographically more accurate or more abstract drawings with smoother lines.

## Plotting

In the plotting step, the `pickle` files are read in and the result image is plotted. Alongside, a second image is plotted with the Hanan grid visible in the background. To run the step, execute

```
python plotting.py $GRIDS $SCALE $SEARCH_RADIUS $BEND_FACTOR $GEO_PENALTY
```

The parameters are necessary again so that the image can be saved with an appropriate file name.
