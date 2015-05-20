# Nachbarn werden als lowerLeft, lowerRight, upperLeft und upperRight gespeichert.
# Was, wenn es auf einer Seite nur einen Nachbarn gibt?
# Was, wenn es keinen gibt (degeneriertes Trapez)

import numpy as np
import visualization as vis

class Point():
	def __init__(self, x, y):
		self.x = x
		self.y = y
	def __repr__(self):
		return '({0},{1})'.format(self.x, self.y)
	def isAbove(self, line):
		arr = np.array([[1, line.left.x, line.left.y], [1, line.right.x, line.right.y], [1, self.x, self.y]])
		if np.linalg.det(arr) > 0:
			return True
		return False

class Line():
	def __init__(self, p1, p2):
		self.left = p1
		self.right = p2
		if self.left.x > self.right.x: # Guarantee ordering
			self.left, self.right = self.right, self.left
	def __repr__(self):
		return '({0},{1}->{2},{3})'.format(self.p1.x, self.p1.y, self.p2.x, self.p2.y)

class Trapezoid():
	def __init__(self, bottom, top, leftPoint, rightPoint):
		self.bottom = bottom
		self.top = top
		self.leftPoint = leftPoint
		self.rightPoint = rightPoint
		self.neighbors = {'lowerLeft': None, 'lowerRight': None, 'upperLeft': None, 'upperRight': None}

class DAGnode():
	def __init__(self, content):
		self.content = content
		content.dagNode = self

class DAG():
	def __init__(self, root):
		self.root = DAGnode(root)
	def findTrapezoid(self, point):
		node = self.root
		while not isinstance(node.content, Trapezoid):
			if isinstance(node.content, Point):
				if point.x < node.content.x:
					node = node.left
				else:
					node = node.right
			elif isinstance(node.content, Line):
				if point.isAbove(node.content):
					node = node.left
				else:
					node = node.right
			else:
				raise Exception('Unknown node type in DAG')
		return node.content
	def splitSingleTrapezoid(self, oldTrapezoid, edge): # returns new trapezoids
		# Create new trapezoids
		a = Trapezoid(oldTrapezoid.bottom, oldTrapezoid.top, oldTrapezoid.leftPoint, edge.left)
		b = Trapezoid(edge, oldTrapezoid.top, edge.left, edge.right)
		c = Trapezoid(oldTrapezoid.bottom, edge, edge.left, edge.right)
		d = Trapezoid(oldTrapezoid.bottom, oldTrapezoid.top, edge.right, oldTrapezoid.rightPoint)
		
		# Set their neighbor relations
		a.neighbors['lowerLeft'] = oldTrapezoid.neighbors['lowerLeft']
		a.neighbors['upperLeft'] = oldTrapezoid.neighbors['upperLeft']
		a.neighbors['lowerRight'] = c
		a.neighbors['upperRight'] = b
		b.neighbors['lowerLeft'] = a # TODO ist das so richtig...
		b.neighbors['upperLeft'] = a
		b.neighbors['lowerRight'] = d
		b.neighbors['upperRight'] = d
		c.neighbors['lowerLeft'] = a
		c.neighbors['upperLeft'] = a
		c.neighbors['lowerRight'] = d
		c.neighbors['upperRight'] = d # .. bis hier?
		d.neighbors['lowerLeft'] = c
		d.neighbors['upperLeft'] = b
		d.neighbors['lowerRight'] = oldTrapezoid.neighbors['lowerRight']
		d.neighbors['upperRight'] = oldTrapezoid.neighbors['upperRight']
		
		# Set neighbor relations of the neighbors of the old trapezoid
		if oldTrapezoid.neighbors['lowerLeft'] is not None: # avoid bounding box
			oldTrapezoid.neighbors['lowerLeft'].neighbors['upperRight'] = a
		if oldTrapezoid.neighbors['upperLeft'] is not None:
			oldTrapezoid.neighbors['upperLeft'].neighbors['lowerRight'] = a
		if oldTrapezoid.neighbors['lowerRight'] is not None:
			oldTrapezoid.neighbors['lowerRight'].neighbors['upperLeft'] = d
		if oldTrapezoid.neighbors['upperRight'] is not None:
			oldTrapezoid.neighbors['upperRight'].neighbors['lowerLeft'] = d
		
		# Actually update D
		aNode = DAGnode(a)
		bNode = DAGnode(b)
		cNode = DAGnode(c)
		dNode = DAGnode(d)
		edgeNode = DAGnode(edge)
		edgeRightEndNode = DAGnode(edge.right)
		
		oldNode = oldTrapezoid.dagNode
		oldNode.content = edge.left
		oldNode.left = aNode
		oldNode.right = edgeRightEndNode
		
		edgeRightEndNode.left = edgeNode
		edgeRightEndNode.right = dNode
		
		edgeNode.left = bNode
		edgeNode.right = cNode
		#TODO
		
		
		
		return {a, b, c, d}

def readDataset(filename):
	with open(filename, 'r') as f:
		n, m, l = f.readline().strip().split()
		n, m, l = int(n), int(m), int(l)
		
		vertices = []
		edges = []
		queries = []
		for _ in range(n):
			x, y = f.readline().strip().split()
			vertices.append( Point(int(x), int(y)) )
		for _ in range(m):
			i, j = f.readline().strip().split()
			edges.append( Line(vertices[int(i)-1], vertices[int(j)-1]) )
		for _ in range(l):
			x, y = f.readline().strip().split()
			queries.append( Point(int(x), int(y)) )
			
		return vertices, edges, queries

filename = 'data/punktlokalisierung_example'
vertices, edges, queries = readDataset(filename)

#vis.visualizePointLocalization(vertices, edges, queries)


import random

def limits(pointSet):
	xMin, yMin = pointSet[0].x, pointSet[0].y
	xMax, yMax = pointSet[0].x, pointSet[0].y
	for point in pointSet:
		xMin = min(point.x, xMin)
		yMin = min(point.y, yMin)
		xMax = max(point.x, xMax)
		yMax = max(point.y, yMax)
	return xMin, yMin, xMax, yMax

#def intersectedTrapezoids(T, D, edge):
def intersectedTrapezoids(D, edge):
	previousDelta = D.findTrapezoid(edge.left)
	H = {previousDelta}
	
	while edge.right.x > previousDelta.rightPoint.x:
		if previousDelta.rightPoint.isAbove(edge):
			previousDelta = previousDelta.neighbors['lowerRight']
			H.add(previousDelta)
		else:
			previousDelta = previousDelta.neighbors['upperRight']
			H.add(previousDelta)
	return H

def trapezoidDecomposition(vertices, edges):
	# Create bounding box
	xMin, yMin, xMax, yMax = limits(vertices)
	lowerLeftPoint = Point(xMin-2, yMin-2) # Lower left
	lowerRightPoint = Point(xMax+1, yMin-1) # Lower right
	#upperLeftPoint = Point(xMin-1, yMax+1) # Upper left
	#upperRightPoint = Point(xMax+2, yMax+2) # Upper right
	bottom = Line(vertices[-4], vertices[-3]) # Bottom
	#right = Line(vertices[-3], vertices[-1]) # Right
	top = Line(vertices[-2], vertices[-1]) # Top
	#left = Line(vertices[-4], vertices[-2]) # Left
	bbox = Trapezoid(bottom, top, lowerLeftPoint, lowerRightPoint)
	
	#vis.visualizePointLocalization(vertices, edges, [])
	
	T = {bbox}
	D = DAG(bbox)
	
	random.shuffle(edges)
	for edge in edges:
		print(len(T))
		#H = intersectedTrapezoids(T, D, edge)
		H = intersectedTrapezoids(D, edge)
		T -= H
		
		if len(H) == 1:
			newTrapezoids = D.splitSingleTrapezoid(H.pop(), edge)
			T |= newTrapezoids # T.update(newTrapezoids)
		else:
			pass
			# TODO
	
	return T, D

trapezoidDecomposition(vertices, edges)














