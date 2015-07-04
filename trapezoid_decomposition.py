import random

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y
	
	def is_left_of(self, point):
		return self.x < point.x
		
	def is_right_of(self, point):
		return self.x > point.x
	
	def is_above(self, line):
		# Sarrus scheme
		det = line.q.x * self.y + line.p.x * line.q.y + line.p.y * self.x - line.p.y * line.q.x - line.q.y * self.x - self.y * line.p.x
		return det > 0
	
	def __str__(self):
		return '({0},{1})'.format(self.x, self.y)

class Line:
	def __init__(self, p, q):
		self.p = p
		self.q = q

class Trapezoid:
	def __init__(self, top, bot, leftp, rightp):
		self.top = top
		self.bot = bot
		self.leftp = leftp
		self.rightp = rightp
		
		self.nw = None
		self.ne = None
		self.sw = None
		self.se = None

class Decomposition(set):
	def get_intersected_trapezoids(self, D, line):
		deltata = [ D.find(line.p) ]
		while line.q.is_right_of(deltata[-1].rightp):
			if deltata[-1].rightp.is_above(line):
				deltata.append(deltata[-1].se)
			else:
				deltata.append(deltata[-1].ne)
		return set(deltata)

# For an inner node that represents a line, the left pointer references
# the area above the line, and the right pointer the area below
# For an inner node that represents a point, the left pointer references
# the area left of the point, and the right pointer the area to the right
class Tree:
	def __init__(self, content, left=None, right=None):
		self.content = content
		self.left = left
		self.right = right
	
	def find(self, point):
		return self._find_node(point).content
	
	def _find_node(self, point):
		if isinstance(self.content, Trapezoid):
			return self
		elif isinstance(self.content, Line):
			if point.is_above(self.content):
				return self.left._find_node(point)
			else:
				return self.right._find_node(point)
		elif isinstance(self.content, Point):
			if point.is_left_of(self.content):
				return self.left._find_node(point)
			else:
				return self.right._find_node(point)
		else:
			raise Exception('Nope.')

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
			if vertices[int(i)-1].x > vertices[int(j)-1].x:
				i, j = j, i
			edges.append( Line(vertices[int(i)-1], vertices[int(j)-1]) )
		for _ in range(l):
			x, y = f.readline().strip().split()
			queries.append( Point(int(x), int(y)) )
			
		return vertices, edges, queries

def initialize(edges):
	left_limit = min(edges[0].p.x, edges[0].q.x)
	right_limit = max(edges[0].p.x, edges[0].q.x)
	lower_limit = min(edges[0].p.y, edges[0].q.y)
	upper_limit = max(edges[0].p.y, edges[0].q.y)
	for line in edges[1:]:
		left_limit = min(left_limit, line.p.x, line.q.x)
		right_limit = max(right_limit, line.p.x, line.q.x)
		lower_limit = min(lower_limit, line.p.y, line.q.y)
		upper_limit = max(upper_limit, line.p.y, line.q.y)
	
	bb_nw = Point(left_limit - 1, upper_limit + 1)
	bb_sw = Point(left_limit - 1, lower_limit - 1)
	bb_ne = Point(right_limit + 1, upper_limit + 1)
	bb_se = Point(right_limit + 1, lower_limit - 1)
	bb_top = Line(bb_nw, bb_ne)
	bb_bot = Line(bb_sw, bb_se)
	bb = Trapezoid(bb_top, bb_bot, bb_nw, bb_ne)
	
	return Decomposition([bb]), Tree(bb)

def construct_trapezoid_decomposition(edges):
	T, D = initialize(edges)
	random.shuffle(edges)
	for line in edges:
		H = T.get_intersected_trapezoids(D, line)
		T -= H
		if len(H) == 1:
			delta0 = H.pop()
			
			# Split into 4 trapezoids
			A_trap = Trapezoid(delta0.top, delta0.bot, delta0.leftp, line.p)
			B_trap = Trapezoid(delta0.top, line, line.p, line.q)
			C_trap = Trapezoid(line, delta0.bot, line.p, line.q)
			D_trap = Trapezoid(delta0.top, delta0.bot, line.q, delta0.rightp)
			
			# Set neighbors
			A_trap.nw, A_trap.ne, A_trap.sw, A_trap.se = delta0.nw, B_trap, delta0.sw, C_trap
			B_trap.nw, B_trap.ne, B_trap.sw, B_trap.se = A_trap, D_trap, None, None
			C_trap.nw, C_trap.ne, C_trap.sw, C_trap.se = None, None, A_trap, D_trap
			D_trap.nw, D_trap.ne, D_trap.sw, D_trap.se = B_trap, delta0.ne, C_trap, delta0.se
			
			# Update search structure
			A_node = Tree(A_trap)
			B_node = Tree(B_trap)
			C_node = Tree(C_trap)
			D_node = Tree(D_trap)
			s_node = Tree(line, B_node, C_node)
			q_node = Tree(line.q, s_node, D_node)
			p_node = D._find_node(line.p)
			p_node.content = line.p
			p_node.left = A_node
			p_node.right = q_node
		else:
			pass
		
	return T, D

filename = 'data/punktlokalisierung_example'
vertices, edges, queries = readDataset(filename)
T, D = construct_trapezoid_decomposition(edges)






