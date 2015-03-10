#! /usr/bin/env python

import unittest
import numpy as np
import afproj


# put an import test here!

class TestGetIndex(unittest.TestCase):
	def setUp(self):
		self.header = ["proj_e","proj_n","unproj_x","unproj_y"]

	def test_index(self):
		for i, elem in enumerate(self.header):
			index = afproj.getIndex(self.header, elem)
			self.assertEqual(i, index)

class TestGetData(unittest.TestCase):
	def setUp(self):
		self.path = "test-data.csv" # test data
		self.fields = ["uid","gx","gy"] # equivalent to header
		self.data = np.array([
			[1,9,30],
			[2,9,70],
			[3,9,110],
			[4,9,150],
			[5,9,190],
			[6,9,230],
			[7,9,270],
			[8,9,310],
			[9,9,350],
			[10,9,390],
			[11,9,430],
			[12,9,470],
			[13,29,10],
			[14,29,50],
			[15,29,90],
			[16,29,130],
			[17,29,170],
			[18,29,210],
			[19,29,250],
			[20,29,290]

		],  dtype = np.float64)

	def test_get_data(self):
		header, data = afproj.getData(self.path, self.fields)
		self.assertTrue(header, self.fields)
		self.assertTrue(np.allclose(data, self.data))

class TestGetControl(unittest.TestCase):
	def setUp(self):
		self.control_points_path = "test-control-points.csv"
		self.control_points_precision_path = "test-control-points-with-precision.csv"
		self.control_points = np.array([
			[625790.088,1012275.575,0,500],
			[626789.5653,1012243.118,1000,500],
			[626773.3367,1011743.38,1000,0],
			[625773.8594,1011775.837,0,0]
		], dtype = np.float64)
		#print self.control_points
		self.control_points_precision = np.array([
			[625790.088,1012275.575,0,500,10,3],
			[626789.5653,1012243.118,1000,500,2,3],
			[626773.3367,1011743.38,1000,0,3,1],
			[625773.8594,1011775.837,0,0,2,4]
		], dtype = np.float64)
		# Negative case - utm_e off by 0.0002. Threshold is 0.0001.
		self.control_points_neg = np.array([
			[625790.088,1012275.575,0,500],
			[626789.5655,1012243.118,1000,500],
			[626773.3367,1011743.38,1000,0],
			[625773.8594,1011775.837,0,0]
		], dtype = np.float64) 
		# Negative case - utm_e off by 0.0002. Threshold is 0.0001.
		self.control_points_precision_neg = np.array([
			[625790.088,1012275.575,0,500,10,3],
			[626789.5655,1012243.118,1000,500,2,3],
			[626773.3367,1011743.38,1000,0,3,1],
			[625773.8594,1011775.837,0,0,2,4]
		], dtype = np.float64) 
		self.header_control_points=["utm_e","utm_n","gx","gy"]
		self.header_control_points_precision=["utm_e","utm_n","gx","gy","utm_e_se","utm_n_se"]

	def test_get_control(self):
		header, control_points = afproj.getControl(self.control_points_path)
		self.assertEqual(header, self.header_control_points)
		self.assertTrue(
			np.allclose(
				control_points, 
				self.control_points, 
				atol=0.00001, 
				rtol=0.0
			)
		)
		with self.assertRaises(AssertionError):
			np.testing.assert_allclose(
				control_points, 
				self.control_points_neg, 
				atol=0.0001, 
				rtol=0.0
			)

	def test_get_control_precision(self):
		header, control_points_precision = afproj.getControl(self.control_points_precision_path)
		self.assertEqual(header, self.header_control_points_precision)
		self.assertTrue(
			np.allclose(
				control_points_precision, 
				self.control_points_precision, 
				atol=0.00001, 
				rtol=0.0
			)
		)
		with self.assertRaises(AssertionError):
			np.testing.assert_allclose(
				control_points_precision, 
				self.control_points_precision_neg, 
				atol=0.0001, 
				rtol=0.0
			)

class TestUpdate(unittest.TestCase):
	def setUp(self):
		self.row = [625, 37000.562, 54000.7642]
		# arbirary, but represents [uid,utm_e,utm_n]
		self.line = np.array([625.0, 37000.562, 54000.7642], dtype = np.float64)

	def test_update(self):
		row = afproj.update(self.line)
		self.assertTrue(np.allclose(row, self.row))

class TestWriteOut(unittest.TestCase):
	pass

class TestFit(unittest.TestCase):
	def setUp(self):
		self.B = 

if __name__ == "__main__":
	unittest.main()
