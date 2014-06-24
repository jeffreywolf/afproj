#! /usr/bin/env python
"""
Spatial adjust and test precision


"""

import numpy as np

from sklearn import linear_model
from sklearn import cross_validation
from sklearn.metrics import explained_variance_score
from sklearn.metrics import mean_squared_error
import argparse, sys, csv, os, time


def getArgs():
	parser = argparse.ArgumentParser(
		description = """Affine spatial transformation with simulated error"""
	)

	parser.add_argument(
		"-c",
		"--controlPoints",
		type = str,
		required = True,
		help = "Control points csv file. See README doc for formating instructions."
	)

	parser.add_argument(
		"-u",
		"--unprojectPoints",
		type = str,
		required = True,
		help = "Unprojected points on plot coordinate system"
	)

	parser.add_argument(
		"-x",
		"--xname",
		type = str,
		required = True,
		help = "field name for x-coordinate in unprojected points file"

	)

	parser.add_argument(
		"-y",
		"--yname",
		type = str,
		required = True,
		help = "field name for y-coordinate in unprojected points file"

	)	

	parser.add_argument(
		"-i",
		"--uid",
		type = str,
		required = True,
		help = "field name for unique identifier of point in unprojected points file"

	)

	parser.add_argument(
		"-n",
		"--nsims",
		type = str,
		required = False,
		help = """Number of simulations"""
	)

	parser.add_argument(
		"-o",
		"--output",
		type = str,
		required = True,
		help = """Output directory"""
	)

	return parser.parse_args()

def getIndex(header, item):
	for i, elem in enumerate(header):
		if elem.lower() == item.lower():
			return i
	return None


def getData(path, fields):
	""" reads in a CSV file and returns data table for analysis """
	data = []
	with open(path, 'rUb') as f:
		indata = csv.reader(f)
		var_indices = []
		for i, line in enumerate(indata):
			if i == 0:
				header = line
				continue
			if 'NA' in line:
				continue # remove lines with NA's
			data.append(line)
	data = np.array(data, dtype=np.float64)
	#print header
	indices = np.array([getIndex(header, item) for item in fields])
	header = [header[i] for i in indices]
	data = data[:, indices]
	return header, data

def getControl(path):
	data = []
	with open(path, "rU") as f:
		for i, line in enumerate(f):
			ls = line.strip().split(',')
			if i == 0:
				continue
			data.append(ls)
	data = np.array(data, dtype=np.float64)
	return data


def writeOut(data, header, filename):
	if header is not None:
		print "\nInitializing {0} file output".format(filename)	
		with open(filename, "w") as f:
			header_str = ",".join(header)+"\n"
			f.write(header_str)
			for line in data: 
				row = ",".join([str(elem) for elem in line])+"\n"
				f.write(row)
	else:
		print "\nInitializing {0} file output".format(filename)	
		with open(filename, "a") as f:
			for line in data: 
				row = ",".join([str(elem) for elem in line])+"\n"
				f.write(row)
	print "Wrote {0} to disk\n".format(filename)

def affine_parameterization(utm_e, utm_n, x, y):
	X = np.column_stack((x, y))
	#print X
	affine_x = linear_model.LinearRegression().fit(X, utm_e)
	affine_y = linear_model.LinearRegression().fit(X, utm_n)
	print affine_x.score(X, utm_e)
	print affine_x.coef_
	#print affine_x.get_params()
	print np.sqrt(mean_squared_error(utm_e, affine_x.predict(X)))
	print affine_y.score(X, utm_n)
	print affine_y.coef_
	#print affine_y.get_params()
	print np.sqrt(mean_squared_error(utm_n, affine_y.predict(X)))
	return affine_x, affine_y


def affine_transformation(X_unprj, affine_x, affine_y, args, header):
	# Affine transformation parameterized.
	# Project unprojected points to UTM coordinate space

	x_pred = affine_x.predict(X_unprj)
	y_pred = affine_y.predict(X_unprj)
	#print x_pred, y_pred
	return x_pred, y_pred


if __name__ == "__main__":
	t_i = time.time()
	args = getArgs()
	initDir = os.getcwd()
	
	fields = [
		args.uid,
		args.xname,
		args.yname
	]

	header, data = getData(args.unprojectPoints, fields)
	print header, data


	np.random.seed(10)

	cp = getControl(args.controlPoints)
	print cp
	print cp.shape

	if cp.shape[1] == 6 and args.nsims is not None:
		sim = True
		print "Will simulate {} realizations of corners.".format(args.nsims)
	elif args.nsims is None:
		sim = False
	elif cp.shape[1] == 4:
		sim = False
		if args.nsims is not None:
			print "Cannot simulate error because no utm_e and utm_n se's" 
			print  "are included in control points file."
	else:
		print "Incorrect dimensions for control points csv."
		raise Exception 


	# Affine Spatial Transformation Parameterization
	# x' = Ax + By + C
	# y' = Dx + Ey + F
	#print cp[:,0:4]
	utm_e, utm_n, x, y = cp[:,0], cp[:,1], cp[:,2], cp[:,3]
	affine_x, affine_y = affine_parameterization(utm_e, utm_n, x, y ) # utm_e, utm_n, x, y

	# data, affine_x, affine_y, args, header 
	uids = data[:, getIndex(header, args.uid)]
	gx = data[:, getIndex(header, args.xname)]
	gy = data[:, getIndex(header, args.yname)]
	X_unprj = np.column_stack(
		(
			gx,
			gy
		)
	)
	x_pred, y_pred = affine_transformation(X_unprj, affine_x, affine_y, args, header) 

	projected_data = np.column_stack(
		(
			uids,
			gx,
			gy,
			x_pred,
			y_pred
		)
	)

	projected_data_header = ["uid", "gx", "gy", "x_pred", "y_pred"]
	writeOut(projected_data, projected_data_header, args.output+"-projected.csv") # data, header, filename

	
	# Simulated locations
	if sim:
		# error cols 4 and 5 from cp csv
		utm_se_e = cp[:,4]
		utm_se_n = cp[:,5]
		sim_data_header = ["iter", "uid", "gx", "gy", "x_pred", "y_pred"]
		for i in range(int(args.nsims)):
			print "Simulation number {}".format(i+1)
			evec = np.zeros(cp.shape[0])
			nvec = np.zeros(cp.shape[0])
			for j, row in enumerate(cp):
				evec[j] = np.random.normal(row[0],row[4], 1)
				nvec[j] = np.random.normal(row[1],row[5], 1)
			affine_x, affine_y = affine_parameterization(evec, nvec, x, y)
			x_pred, y_pred = affine_transformation(X_unprj, affine_x, affine_y, args, header)			
			iteration = i + np.zeros(x_pred.shape[0])
			sim_data = np.column_stack(
				(
				iteration,
				uids,
				gx,
				gy,
				x_pred,
				y_pred
				)
			)
			if i == 0:
				writeOut(sim_data, sim_data_header, args.output+"-sim.csv") # data, header, filename
			else:
				writeOut(sim_data, None, args.output+"-sim.csv") # data, header, filename
	t_f = time.time()
	print "Spatially adjusted data in {} seconds".format(t_f - t_i)
