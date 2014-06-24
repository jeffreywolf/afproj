README 
======

General
-------
This program applies an affine spatial transformation to project unprojected point data.  This program will also simulate the locational uncertainty introduced through imprecise GPS point data through creating nsims realizations of the control points used for affine transformation.

Two files must be passed to the program:
1. Data file containing unique identifier for each point, an x coordinate, and a y coordinate. 

Other fields may be kept in the input file, but will not appear in the output file from this 
program. You can, of course, later join the projected coordinate to your other data associated with each point by joining on the unique identifier.

2. Control points file (see below for formatting requirements).


Output
-------------
This program returns two files:
1. A file with unprojected points projected to utm coordinates using affine 
transformation. 

2. A file with nsims realizations of utm coordinates for each input point.  

The simulated locations are based on the precision estimates for your projected points. Such data may be available for GPS coordinates collected using differential GPS.  Normal distributions in the
north and east directions are parameterized using the proj_dir and proj_dir_se for mean and
standard error.  Draws from both normals then give a simulated location for the corner.  Affine
spatial transformation is then parameterized with the simulated corners.  The parameterized
affine transformation model is then used to project the unprojected data.


Dependencies
--------------
sklearn
numpy


Control Points File
-------------------
A file containing projected and unprojected coordinates.

Control Points CSV Input file format. 

Header: proj_e, proj_n, unproj_x, unproj_y

OR 

Header: proj_e, proj_n, unproj_x, unproj_y, proj_e_se, proj_n_se


See example control points file in source directory.

The example points are in the WGS 84 UTM Zone 17 N projection and an unprojected coordinate system.



Data File
-------------
Enter column names next to adjacent flags

For help on command line flags type

`./afproj.py -h` 



Example call
-------------
Make sure the program permissions are set to executable
`chmod u+x afproj.py`

Then run the program with the example data file and without simulation.

`./afproj.py -c test-control-points.csv -u data.csv -x gx -y gy -i uid -o projected-data`

Here is an example that will both project the unprojected data using the mean for each control point and also produce simulated locations for each data point using simulated control points.

`./afproj.py -c test-control-points-with-precision.csv -u data.csv -x gx -y gy -i uid -n 1000 -o projected-data`

