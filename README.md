# Metro Maps on Octilinear Grid Graphs

## Project Description

Schematic "metro maps" are important to create visualizations of public transit networks that are easy to read and convey the necessary information. The de facto standard layout used today is a so-called octilinear design using horizontal, vertical and diagonal line segments, which was proposed by Harry Beck in 1931 for the London subway. These maps are even today still drawn manually; and since the network structure might change regularly, it is of high interest to render them automatically instead.

## Used Data

The focus of the project was on the data of the RAB network, which is freely available in the GTFS format here: https://www.nvbw.de/open-data/fahrplandaten/fahrplandaten-ohne-liniennetz

In particular, the data of the _Stadtbus Ravensburg Weingarten_ (town bus of Ravensburg and Weingarten) was used, which was obtained from the data by reading in the routes with an ID that matches the regex `7-3(0(1|3|[4-7]|9)|1(0|1|4|5)|2(0|1))`.

## Running the calculations

Extract the zipped GTFS data into the folder `gtfs/rab`. Then run the following command:

```
python main.py
```

Running the calculations and viewing the plotting are possible via a web interface which should be self-explanatory.
Explanations for the parameters can be found on the tutorial page.