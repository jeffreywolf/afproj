README 
======

General
-------
This program applies an affine spatial transformation to project unprojected point data.  This program will also simulate the locational uncertainty introduced through imprecise GPS point data through creating nsims realizations of the control points used for affine transformation.

Two files must be passed to the program:

1. **Data file** containing unique identifier for each point, an x coordinate, and a y coordinate. Other fields may be kept in the input file, but will not appear in the output file from this program. You can, of course, later join the projected coordinate to your other data associated with each point by joining on the unique identifier.

2. **Control points file** (see below for formatting requirements).


Output
-------------
This program returns two files:

1. A file with unprojected points projected to utm coordinates using affine 
transformation. 

2. A file with nsims realizations of utm coordinates for each input point.  

The simulated locations are based on the precision estimates for your projected points. Such data may be available for GPS coordinates collected using differential GPS.  Normal distributions in the north and east directions are parameterized using the mean and se for mean.  Draws from both normals then give a simulated location for the corner.  An affine spatial transformation is then parameterized with the simulated corners.  The parameterized affine transformation model is then used to project the unprojected data.


Dependencies
--------------
sklearn, numpy


Control Points File
-------------------
A file containing projected and unprojected coordinates. Optionally, also contains measurements of precision in the projected coordinate space for the easting and northing.

Control Points CSV Input file header: 

| proj_e | proj_n | unproj_x | unproj_y |
|--------|--------|----------|----------|

see *test-control-points.csv* for example.

OR

| proj_e | proj_n | unproj_x | unproj_y | proj_e_se | proj_n_se |
|--------|--------|----------|----------|-----------|-----------|

see *test-control-points-with-precision.csv* for example.

| Variable name | Description                           |
|:--------------|:--------------------------------------|
|proj_e         | projected easting (e) coordinate      |
|proj_n         | projected northing (y) coordinate     |
|unproj_e       | unprojected easting (e) coordinate    |
|unproj_n       | unprojected northing (y) coordinate   |
|proj_e_se      | projected easting (e) standard error  |
|proj_n_se      | projected northing (y) standard error |


The example control points are in the projection WGS 1984 UTM Zone 17N (EPSG 32617) and an unprojected coordinate system.

Data File
-------------
Enter column names next to adjacent flags

For help on command line flags type

`./afproj.py -h` 

The example data file is *data.csv*

Example call
-------------
Make sure the program permissions are set to executable
`chmod u+x afproj.py`

Then run the program with the example data file and without simulation.

`./afproj.py -c test-control-points.csv -u data.csv -x gx -y gy -i uid -o projected-data`

Here is an example that will both project the unprojected data using the mean for each control point and also produce simulated locations for each data point using simulated control points.

`./afproj.py -c test-control-points-with-precision.csv -u data.csv -x gx -y gy -i uid -n 1000 -o projected-data`


