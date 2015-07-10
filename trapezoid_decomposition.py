#~ TODO:
#~ Mehr Daten generieren
#~ Möglichkeit finden, Punkte Facetten zuzuordnen
#~ Überlegen, wie das mit |delta| > 1 funktioniert
#~ Kommentieren

import random
from shapes import *
import visualization as vis

class Decomposition(set):
	def get_intersected_trapezoids(self, D, line):
		#~ TODO justify searching for a point on the Line l_i just after
		#~ the point p_i, instead of searching for p_i directly
		#~ deltata = [ D.find(line.p) ]
		#~ TODO also make the values 0.99, 0.01 data-dependent
		search_start = Point(line.p.x * 0.99 + line.q.x*0.01, line.p.y * 0.99 + line.q.y*0.01)
		deltata = [ D.find(search_start) ]
		while line.q.is_right_of(deltata[-1].rightp):
			if deltata[-1].rightp.is_above(line):
				deltata.append(deltata[-1].se)
			else:
				deltata.append(deltata[-1].ne)
		return deltata
	
	def __str__(self):
		string_representation = ''
		for trapezoid in self:
			string_representation += '{0}\n'.format(trapezoid)
		return string_representation

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
	
	def __str__(self, indent=0, indent_string = '  '):
		string_representation = self.content.__str__(indent)
		if not isinstance(self.content, Trapezoid):
			string_representation += '\n'
			string_representation += self.left.__str__(indent+1)
			string_representation += '\n'
			string_representation += self.right.__str__(indent+1)
		return string_representation

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

def handle_one_trapezoid_completely_inside(T, D, delta0, line):
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
	
	# Update delta0's neighbor's neighbor-pointers.
	if delta0.nw is not None:
		delta0.nw.replace_neighbor(delta0, A_trap)
	if delta0.sw is not None:
		delta0.sw.replace_neighbor(delta0, A_trap)
	if delta0.ne is not None:
		delta0.ne.replace_neighbor(delta0, D_trap)
	if delta0.se is not None:
		delta0.se.replace_neighbor(delta0, D_trap)
	
	# Update decomposition
	T.update([A_trap, B_trap, C_trap, D_trap])
	
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

def handle_one_trapezoid_left_touching(T, D, delta0, line):
	# Split into 3 trapezoids
	B_trap = Trapezoid(delta0.top, line, line.p, line.q)
	C_trap = Trapezoid(line, delta0.bot, line.p, line.q)
	D_trap = Trapezoid(delta0.top, delta0.bot, line.q, delta0.rightp)
	
	# Set neighbors
	B_trap.nw, B_trap.ne, B_trap.sw, B_trap.se = delta0.nw, D_trap, None, None
	C_trap.nw, C_trap.ne, C_trap.sw, C_trap.se = None, None, delta0.sw, D_trap
	D_trap.nw, D_trap.ne, D_trap.sw, D_trap.se = B_trap, delta0.ne, C_trap, delta0.se
	
	# Update delta0's neighbor's neighbor-pointers.
	if delta0.nw is not None:
		delta0.nw.replace_neighbor(delta0, B_trap)
	if delta0.sw is not None:
		delta0.sw.replace_neighbor(delta0, C_trap)
	if delta0.ne is not None:
		delta0.ne.replace_neighbor(delta0, D_trap)
	if delta0.se is not None:
		delta0.se.replace_neighbor(delta0, D_trap)
	
	# Update decomposition
	T.update([B_trap, C_trap, D_trap])
	
	# Update search structure
	B_node = Tree(B_trap)
	C_node = Tree(C_trap)
	D_node = Tree(D_trap)
	s_node = Tree(line, B_node, C_node)
	q_node = D._find_node(line.q)
	q_node.content = line.q
	q_node.left = s_node
	q_node.right = D_node

def handle_one_trapezoid_right_touching(T, D, delta0, line):
	# Split into 3 trapezoids
	A_trap = Trapezoid(delta0.top, delta0.bot, delta0.leftp, line.p)
	B_trap = Trapezoid(delta0.top, line, line.p, line.q)
	C_trap = Trapezoid(line, delta0.bot, line.p, line.q)
	
	# Set neighbors
	A_trap.nw, A_trap.ne, A_trap.sw, A_trap.se = delta0.nw, B_trap, delta0.sw, C_trap
	B_trap.nw, B_trap.ne, B_trap.sw, B_trap.se = A_trap, delta0.ne, None, None
	C_trap.nw, C_trap.ne, C_trap.sw, C_trap.se = None, None, A_trap, delta0.se
	
	# Update delta0's neighbor's neighbor-pointers.
	if delta0.nw is not None:
		delta0.nw.replace_neighbor(delta0, A_trap)
	if delta0.sw is not None:
		delta0.sw.replace_neighbor(delta0, A_trap)
	if delta0.ne is not None:
		delta0.ne.replace_neighbor(delta0, B_trap)
	if delta0.se is not None:
		delta0.se.replace_neighbor(delta0, C_trap)
	
	# Update decomposition
	T.update([A_trap, B_trap, C_trap])
	
	# Update search structure
	A_node = Tree(A_trap)
	B_node = Tree(B_trap)
	C_node = Tree(C_trap)
	s_node = Tree(line, B_node, C_node)
	p_node = D._find_node(line.p)
	p_node.content = line.p
	p_node.left = A_node
	p_node.right = s_node

#~ TODO what if there are exactly 2 intersected trapezoids?
def handle_multiple_trapezoids_completely_inside(T, D, Delta, line):
	left_trap = Trapezoid(Delta[0].top, Delta[0].bot, Delta[0].leftp, line.p)
	
	upper_trap = Trapezoid(Delta[0].top, line, line.p, Delta[0].rightp)
	upper_list = [upper_trap]
	for old_trap in Delta[1:-1]:
		if old_trap.top is upper_trap.top:
			upper_trap.rightp = old_trap.rightp
		else:
			upper_trap = Trapezoid(old_trap.top, line, old_trap.leftp, old_trap.rightp)
			upper_list.append(upper_trap)
			

def construct_trapezoid_decomposition(edges):
	T, D = initialize(edges)
	random.shuffle(edges)
	for line in edges:
		print('--------------------')
		print('\nT:\n{0}'.format(T))
		print('D:\n{0}'.format(D))
		print('\nAdding line {0}'.format(line))
		print('--------------------')
		vis.draw_decomposition(T)
		H = T.get_intersected_trapezoids(D, line)
		T -= set(H)
		if len(H) == 1:
			delta0 = H[0]
			
			if line.p.x > delta0.leftp.x and line.q.x < delta0.rightp.x:
				handle_one_trapezoid_completely_inside(T, D, delta0, line)
			elif line.p.x == delta0.leftp.x and line.q.x < delta0.rightp.x:
				handle_one_trapezoid_left_touching(T, D, delta0, line)
			elif line.p.x > delta0.leftp.x and line.q.x == delta0.rightp.x:
				handle_one_trapezoid_right_touching(T, D, delta0, line)
			else: # line.p.x == delta0.leftp.x and line.q.x == delta0.rightp.x
				#~ handle_one_trapezoid_both_touching(T, D, delta0, line)
				T |= set(H) # TODO
				T.update([delta0])
		else:
			if line.p.x > H[0].leftp.x and line.q.x < H[-1].rightp.x:
				T |= set(H) # TODO
			elif line.p.x == H[0].leftp.x and line.q.x < H[-1].rightp.x:
				T |= set(H) # TODO
			elif line.p.x > H[0].leftp.x and line.q.x == H[-1].rightp.x:
				T |= set(H) # TODO
			else: # line.p.x == H[0].leftp.x and line.q.x == H[-1].rightp.x:
				T |= set(H) # TODO
		
	return T, D

filename = 'data/punktlokalisierung_example'
vertices, edges, queries = readDataset(filename)
#~ vis.draw_scenario(vertices, edges, queries)
T, D = construct_trapezoid_decomposition(edges)











