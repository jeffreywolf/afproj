#! /usr/bin/env python
"""
Affine spatial transformation
"""
import numpy as np
import argparse, sys, csv, os, time

def getArgs():
	parser = argparse.ArgumentParser(
		description = """Affine spatial transformation"""
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
		help = """Output file prefix"""
	)
	parser.add_argument(
		"-v",
		"--verbose",
		action = "store_true",
		help = "Print status updates while executing"
	)
	return parser.parse_args()

def getIndex(header, item):
	"""Get index of variable
	"""
	for i, elem in enumerate(header):
		if elem.lower() == item.lower():
			return i
	return None

def getData(path, fields):
	"""Read unprojected points file as numpy array"""
	data = []
	with open(path, 'rUb') as f:
		indata = csv.reader(f)
		var_indices = []
		for i, line in enumerate(indata):
			if i == 0:
				header = line
				continue
			if 'NA' in line:
				for j, elem in enumerate(line):
					line[j] = np.nan
			data.append(line)
	data = np.array(data, dtype = np.float64)
	indices = np.array([getIndex(header, item) for item in fields])
	header = [header[i] for i in indices]
	data = data[:, indices]
	return header, data

def getControl(path):
	"""Read control points file as numpy array
	"""
	data = []
	with open(path, "rU") as f:
		for i, line in enumerate(f):
			ls = line.strip().split(',')
			if i == 0:
				continue
			data.append(ls)
	data = np.array(data, dtype = np.float64)
	return data

def update(line):
	"""Convert uid or nsim column to integer
	"""
	if len(line)==5:
		line[0]=int(line)
		return line
	else:
		line[0]=int(line)
		line[1]=int(line)
		return line

def writeOut(data, header, filename, verbose):
	"""Write data to a file.
	"""
	if verbose:
		print "\nInitializing {0} file output".format(filename)		
	if header is not None:

		with open(filename, "w") as f:
			header_str = ",".join(header)+"\n"
			f.write(header_str)
			for line in data:
				line = update(line)
				row = ",".join([str(elem) for elem in line])+"\n"
				f.write(row)
	else:
		with open(filename, "a") as f:
			for line in data:
				line = update(line)
				row = ",".join([str(elem) for elem in line])+"\n"
				f.write(row)
	if verbose:
		print "Wrote {0} to disk\n".format(filename)

def fit(X, y):
	"""Fit using matrix algebra
	"""
	XTXinv = inv(np.dot(X.T, X))
	XTy = np.dot(X.T, y)
	B = np.dot(XTXinv, XTy)
	return B

def affine_parameterization(utm_e, utm_n, x, y):
	"""Parameterize affine function
	"""
	X = np.column_stack(
		(
			x, 
			y, 
			np.ones(len(x))
		)
	)
	affine_x = fit(X, utm_e)
	affine_y = fit(X, utm_n)
	return affine_x, affine_y

def affine_transformation(X_unprj, affine_x, affine_y, args, header):
	"""Predict with affine function
	"""
	x_pred = np.dot(X_unprj, affine_x)
	y_pred = np.dot(X_unprj, affine_y)
	return x_pred, y_pred

def main():
	t_i = time.time()
	args = getArgs()
	initDir = os.getcwd()
	
	fields = [
		args.uid,
		args.xname,
		args.yname
	]

	np.random.seed(10)

	header, data = getData(args.unprojectPoints, fields)
	cp = getControl(args.controlPoints)

	# Determine whether or not to run simulation
	if cp.shape[1] == 6 and args.nsims is not None:
		sim = True
		if args.verbose:
			print "Will simulate {} realizations of corners.".format(args.nsims)
	elif args.nsims is None:
		sim = False
	elif cp.shape[1] == 4:
		sim = False
		if args.nsims is not None:
			if args.verbose:
				print "Cannot simulate error because no utm_e and utm_n se's" 
				print  "are included in control points file."
	else:
		print "Incorrect dimensions for control points file. Exiting."
		sys.exit(1)

	# Affine Spatial Transformation Parameterization
	# x' = Ax + By + C
	# y' = Dx + Ey + F
	utm_e, utm_n = cp[:,0].flatten(), cp[:,1].flatten()
	x, y = cp[:,2].flatten(), cp[:,3].flatten()
	affine_x, affine_y = affine_parameterization(utm_e, utm_n, x, y )

	uids = data[:, getIndex(header, args.uid)].flatten()
	gx = data[:, getIndex(header, args.xname)].flatten()
	gy = data[:, getIndex(header, args.yname)].flatten()
	X_unprj = np.column_stack(
		(
			gx,
			gy,
			np.ones(gx)
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
	writeOut(projected_data, projected_data_header, args.output+"-projected.csv", args.verbose) # data, header, filename

	
	# Simulated locations
	if sim:
		# error cols 4 and 5 from cp csv
		utm_se_e = cp[:,4]
		utm_se_n = cp[:,5]
		sim_data_header = ["iter", "uid", "gx", "gy", "x_pred", "y_pred"]
		for i in range(int(args.nsims)):
			if args.verbose:
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
				writeOut(sim_data, sim_data_header, args.output+"-sim.csv", args.verbose) # data, header, filename
			else:
				writeOut(sim_data, None, args.output+"-sim.csv", args.verbose) # data, header, filename
	t_f = time.time()
	if args.verbose:
		print "Spatially adjusted data in {} seconds".format(t_f - t_i)


if __name__ == "__main__":
	main()
