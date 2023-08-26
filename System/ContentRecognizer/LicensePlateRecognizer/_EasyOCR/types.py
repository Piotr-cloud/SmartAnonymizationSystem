
from ctypes import *
import numpy as np

import random


def sample(probs):
	s = sum(probs)
	probs = [a/s for a in probs]
	r = random.uniform(0, 1)
	for i in range(len(probs)):
		r = r - probs[i]
		if r <= 0:
			return i
	return len(probs)-1

def c_array(ctype, values):
	arr = (ctype*len(values))()
	arr[:] = values
	return arr

class BOX(Structure):
	_fields_ = [("x", c_float),
				("y", c_float),
				("w", c_float),
				("h", c_float)]

class DETECTION(Structure):
	_fields_ = [("bbox", BOX),
				("classes", c_int),
				("prob", POINTER(c_float)),
				("mask", POINTER(c_float)),
				("objectness", c_float),
				("sort_class", c_int)]


class IMAGE(Structure):
	_fields_ = [("w", c_int),
				("h", c_int),
				("c", c_int),
				("data", POINTER(c_float))]

class METADATA(Structure):
	_fields_ = [("classes", c_int),
				("names", POINTER(c_char_p))]

class Label:

	def __init__(self,cl=-1,tl=np.array([0.,0.]),br=np.array([0.,0.]),prob=None):
		self.__tl 	= tl
		self.__br 	= br
		self.__cl 	= cl
		self.__prob = prob

	def __str__(self):
		return 'Class: %d, top_left(x:%f,y:%f), bottom_right(x:%f,y:%f)' % (self.__cl, self.__tl[0], self.__tl[1], self.__br[0], self.__br[1])

	def copy(self):
		return Label(self.__cl,self.__tl,self.__br)

	def wh(self): return self.__br-self.__tl

	def cc(self): return self.__tl + self.wh()/2

	def tl(self): return self.__tl

	def br(self): return self.__br

	def tr(self): return np.array([self.__br[0],self.__tl[1]])

	def bl(self): return np.array([self.__tl[0],self.__br[1]])

	def cl(self): return self.__cl

	def area(self): return np.prod(self.wh())

	def prob(self): return self.__prob

	def set_class(self,cl):
		self.__cl = cl

	def set_tl(self,tl):
		self.__tl = tl

	def set_br(self,br):
		self.__br = br

	def set_wh(self,wh):
		cc = self.cc()
		self.__tl = cc - .5*wh
		self.__br = cc + .5*wh

	def set_prob(self,prob):
		self.__prob = prob



class Shape():

	def __init__(self,pts=np.zeros((2,0)),max_sides=4,text=''):
		self.pts = pts
		self.max_sides = max_sides
		self.text = text

	def isValid(self):
		return self.pts.shape[1] > 2

	def write(self,fp):
		fp.write('%d,' % self.pts.shape[1])
		ptsarray = self.pts.flatten()
		fp.write(''.join([('%f,' % value) for value in ptsarray]))
		fp.write('%s,' % self.text)
		fp.write('\n')

	def read(self,line):
		data 		= line.strip().split(',')
		ss 			= int(data[0])
		values 		= data[1:(ss*2 + 1)]
		text 		= data[(ss*2 + 1)] if len(data) >= (ss*2 + 2) else ''
		self.pts 	= np.array([float(value) for value in values]).reshape((2,ss))
		self.text   = text


def readShapes(path,obj_type=Shape):
	shapes = []
	with open(path) as fp:
		for line in fp:
			shape = obj_type()
			shape.read(line)
			shapes.append(shape)
	return shapes


def writeShapes(path,shapes):
	if len(shapes):
		with open(path,'w') as fp:
			for shape in shapes:
				if shape.isValid():
					shape.write(fp)

