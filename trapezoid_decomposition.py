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

def read_dataset(filename):
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

def write_result(filename, groups):
	with open(filename, 'w') as f:
		for group in groups:
			for point in group:
				f.write('{0} '.format(point + 1))
			f.write('\n')

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

#~ TODO check das mal, Yannick
def handle_one_trapezoid_both_touching(T, D, delta0, line):
	# Split into 2 trapezoids
	B_trap = Trapezoid(delta0.top, line, line.p, line.q)
	C_trap = Trapezoid(line, delta0.bot, line.p, line.q)
	
	# Set neighbors
	B_trap.nw, B_trap.ne, B_trap.sw, B_trap.se = delta0.nw, delta0.ne, None, None
	C_trap.nw, C_trap.ne, C_trap.sw, C_trap.se = None, None, delta0.sw, delta0.se
	
	# Update delta0's neighbor's neighbor-pointers.
	if delta0.nw is not None:
		delta0.nw.replace_neighbor(delta0, B_trap)
	if delta0.sw is not None:
		delta0.sw.replace_neighbor(delta0, C_trap)
	if delta0.ne is not None:
		delta0.ne.replace_neighbor(delta0, B_trap)
	if delta0.se is not None:
		delta0.se.replace_neighbor(delta0, C_trap)
	
	# Update decomposition
	T.update([B_trap, C_trap])
	
	# Update search structure
	B_node = Tree(B_trap)
	C_node = Tree(C_trap)
	inside_point = Point(line.p.x * 0.5 + line.q.x * 0.5, line.p.y * 0.5 + line.q.y * 0.5)
	s_node = D._find_node(inside_point)
	s_node.content = line
	s_node.left = B_node
	s_node.right = C_node

def handle_multiple_trapezoids_completely_inside(T, D, Delta, line):
	left_trap = Trapezoid(Delta[0].top, Delta[0].bot, Delta[0].leftp, line.p)
	
	# Create first trapezoid above the line
	upper_trap = Trapezoid(Delta[0].top, line, line.p, Delta[0].rightp)
	upper_trap.ne = Delta[0].ne # Only for unique x-coordinates
	if Delta[0].ne is not None:
		Delta[0].ne.replace_neighbor(Delta[0], upper_trap)
	upper_list = [upper_trap]
	
	# Create first trapezoid below the line
	lower_trap = Trapezoid(line, Delta[0].bot, line.p, Delta[0].rightp)
	lower_trap.se = Delta[0].se
	if Delta[0].se is not None:
		Delta[0].se.replace_neighbor(Delta[0], lower_trap)
	lower_list = [lower_trap]
	
	# Update D for Delta[0]
	Left_Trap_node = Tree(left_trap)
	Upper_Trap_node = Tree(upper_trap)
	Lower_Trap_node = Tree(lower_trap)
	Left_Line_node = Tree(line, Upper_Trap_node, Lower_Trap_node)
	P_node = D._find_node(line.p)
	P_node.content = line.p
	P_node.left = Left_Trap_node
	P_node.right = Left_Line_node
	
	for old_trap in Delta[1:-1]:
		# Handle trapezoids above the line
		if old_trap.top is upper_list[-1].top:
			upper_list[-1].rightp = old_trap.rightp
			upper_list[-1].ne = old_trap.ne
			if old_trap.ne is not None:
				old_trap.ne.replace_neighbor(old_trap, upper_list[-1])
		else:
			upper_trap = Trapezoid(old_trap.top, line, old_trap.leftp, old_trap.rightp)
			upper_trap.nw = old_trap.nw
			if old_trap.nw is not None:
				old_trap.nw.replace_neighbor(old_trap, upper_trap)
			upper_trap.ne = old_trap.ne
			if old_trap.ne is not None:
				old_trap.ne.replace_neighbor(old_trap, upper_trap)
			upper_trap.sw = upper_list[-1]
			upper_list[-1].se = upper_trap
			upper_list.append(upper_trap)
			Upper_Trap_node = Tree(upper_trap)
		
		# Handle trapezoids below the line
		if old_trap.bot is lower_list[-1].bot:
			lower_list[-1].rightp = old_trap.rightp
			lower_list[-1].se = old_trap.se
			if old_trap.se is not None:
				old_trap.se.replace_neighbor(old_trap, lower_list[-1])
		else:
			lower_trap = Trapezoid(line, old_trap.bot, old_trap.leftp, old_trap.rightp)
			lower_trap.sw = old_trap.sw
			if old_trap.sw is not None:
				old_trap.sw.replace_neighbor(old_trap, lower_trap)
			lower_trap.se = old_trap.se
			if old_trap.se is not None:
				old_trap.se.replace_neighbor(old_trap, lower_trap)
			lower_trap.nw = lower_list[-1]
			lower_list[-1].ne = lower_trap
			lower_list.append(lower_trap)
			Lower_Trap_node = Tree(lower_trap)
		
		point_in_old_trap = Point( (old_trap.leftp.x + old_trap.rightp.x)/2, line.eval((old_trap.leftp.x + old_trap.rightp.x)/2) )
		S_node = D._find_node(point_in_old_trap)
		S_node.content = line
		S_node.left = Upper_Trap_node
		S_node.right = Lower_Trap_node
	
	# Create last trapezoid above the line
	if upper_list[-1].top is Delta[-1].top:
		upper_list[-1].rightp = line.q
	else:
		upper_trap = Trapezoid(Delta[-1].top, line, Delta[-1].leftp, line.q)
		upper_trap.nw = Delta[-1].nw
		if Delta[-1].nw is not None:
			Delta[-1].nw.replace_neighbor(Delta[-1], upper_trap)
		upper_trap.sw = upper_list[-1]
		upper_list[-1].se = upper_trap
		upper_list.append(upper_trap)
		Upper_Trap_node = Tree(upper_trap)
	
	# Create last trapezoid below the line
	if lower_list[-1].bot is Delta[-1].bot:
		lower_list[-1].rightp = line.q
	else:
		lower_trap = Trapezoid(line, Delta[-1].bot, Delta[-1].leftp, line.q)
		lower_trap.sw = Delta[-1].sw
		if Delta[-1].sw is not None:
			Delta[-1].sw.replace_neighbor(Delta[-1], lower_trap)
		lower_trap.nw = lower_list[-1]
		lower_list[-1].ne = lower_trap
		lower_list.append(lower_trap)
		Lower_Trap_node = Tree(lower_trap)
	
	right_trap = Trapezoid(Delta[-1].top, Delta[-1].bot, line.q, Delta[-1].rightp)
	
	# Update D for Delta[-1]
	Right_Trap_node = Tree(right_trap)
	Right_Line_node = Tree(line, Upper_Trap_node, Lower_Trap_node)
	Q_node = D._find_node(line.q)
	Q_node.content = line.q
	Q_node.left = Right_Line_node
	Q_node.right = Right_Trap_node
	
	# Set neighbors of leftmost trapezoid and back-pointers
	left_trap.nw = Delta[0].nw
	if Delta[0].nw is not None:
		Delta[0].nw.replace_neighbor(Delta[0], left_trap)
	left_trap.sw = Delta[0].sw
	if Delta[0].sw is not None:
		Delta[0].sw.replace_neighbor(Delta[0], left_trap)
	left_trap.ne = upper_list[0]
	left_trap.se = lower_list[0]
	upper_list[0].nw = left_trap
	lower_list[0].sw = left_trap
	
	# Set neighbors of rightmost trapezoid and back-pointers
	right_trap.ne = Delta[-1].ne
	if Delta[-1].ne is not None:
		Delta[-1].ne.replace_neighbor(Delta[-1], right_trap)
	right_trap.se = Delta[-1].se
	if Delta[-1].se is not None:
		Delta[-1].se.replace_neighbor(Delta[-1], right_trap)
	right_trap.nw = upper_list[-1]
	right_trap.sw = lower_list[-1]
	upper_list[-1].ne = right_trap
	lower_list[-1].se = right_trap
	
	T.add(left_trap)
	T.add(right_trap)
	T.update(upper_list)
	T.update(lower_list)

def handle_multiple_trapezoids_left_touching(T, D, Delta, line):
	# Create first trapezoid above the line
	upper_trap = Trapezoid(Delta[0].top, line, line.p, Delta[0].rightp)
	upper_trap.nw = Delta[0].nw
	if Delta[0].nw is not None:
		Delta[0].nw.replace_neighbor(Delta[0], upper_trap)
	upper_trap.ne = Delta[0].ne # Only for unique x-coordinates
	if Delta[0].ne is not None:
		Delta[0].ne.replace_neighbor(Delta[0], upper_trap)
	upper_list = [upper_trap]
	
	# Create first trapezoid below the line
	lower_trap = Trapezoid(line, Delta[0].bot, line.p, Delta[0].rightp)
	lower_trap.sw = Delta[0].sw
	if Delta[0].sw is not None:
		Delta[0].sw.replace_neighbor(Delta[0], lower_trap)
	lower_trap.se = Delta[0].se
	if Delta[0].se is not None:
		Delta[0].se.replace_neighbor(Delta[0], lower_trap)
	lower_list = [lower_trap]
	
	# Update D for Delta[0]
	Upper_Trap_node = Tree(upper_trap)
	Lower_Trap_node = Tree(lower_trap)
	search_point = Point( (Delta[0].leftp.x + Delta[0].rightp.x)/2, line.eval( (Delta[0].leftp.x + Delta[0].rightp.x)/2 ) )
	S_node = D._find_node(search_point)
	S_node.content = line
	S_node.left = Upper_Trap_node
	S_node.right = Lower_Trap_node
	
	for old_trap in Delta[1:-1]:
		# Handle trapezoids above the line
		if old_trap.top is upper_list[-1].top:
			upper_list[-1].rightp = old_trap.rightp
			upper_list[-1].ne = old_trap.ne
			if old_trap.ne is not None:
				old_trap.ne.replace_neighbor(old_trap, upper_list[-1])
		else:
			upper_trap = Trapezoid(old_trap.top, line, old_trap.leftp, old_trap.rightp)
			upper_trap.nw = old_trap.nw
			if old_trap.nw is not None:
				old_trap.nw.replace_neighbor(old_trap, upper_trap)
			upper_trap.ne = old_trap.ne
			if old_trap.ne is not None:
				old_trap.ne.replace_neighbor(old_trap, upper_trap)
			upper_trap.sw = upper_list[-1]
			upper_list[-1].se = upper_trap
			upper_list.append(upper_trap)
			Upper_Trap_node = Tree(upper_trap)
		
		# Handle trapezoids below the line
		if old_trap.bot is lower_list[-1].bot:
			lower_list[-1].rightp = old_trap.rightp
			lower_list[-1].se = old_trap.se
			if old_trap.se is not None:
				old_trap.se.replace_neighbor(old_trap, lower_list[-1])
		else:
			lower_trap = Trapezoid(line, old_trap.bot, old_trap.leftp, old_trap.rightp)
			lower_trap.sw = old_trap.sw
			if old_trap.sw is not None:
				old_trap.sw.replace_neighbor(old_trap, lower_trap)
			lower_trap.se = old_trap.se
			if old_trap.se is not None:
				old_trap.se.replace_neighbor(old_trap, lower_trap)
			lower_trap.nw = lower_list[-1]
			lower_list[-1].ne = lower_trap
			lower_list.append(lower_trap)
			Lower_Trap_node = Tree(lower_trap)
		
		point_in_old_trap = Point( (old_trap.leftp.x + old_trap.rightp.x)/2, line.eval((old_trap.leftp.x + old_trap.rightp.x)/2) )
		S_node = D._find_node(point_in_old_trap)
		S_node.content = line
		S_node.left = Upper_Trap_node
		S_node.right = Lower_Trap_node
	
	# Create last trapezoid above the line
	if upper_list[-1].top is Delta[-1].top:
		upper_list[-1].rightp = line.q
	else:
		upper_trap = Trapezoid(Delta[-1].top, line, Delta[-1].leftp, line.q)
		upper_trap.nw = Delta[-1].nw
		if Delta[-1].nw is not None:
			Delta[-1].nw.replace_neighbor(Delta[-1], upper_trap)
		upper_trap.sw = upper_list[-1]
		upper_list[-1].se = upper_trap
		upper_list.append(upper_trap)
		Upper_Trap_node = Tree(upper_trap)
	
	# Create last trapezoid below the line
	if lower_list[-1].bot is Delta[-1].bot:
		lower_list[-1].rightp = line.q
	else:
		lower_trap = Trapezoid(line, Delta[-1].bot, Delta[-1].leftp, line.q)
		lower_trap.sw = Delta[-1].sw
		if Delta[-1].sw is not None:
			Delta[-1].sw.replace_neighbor(Delta[-1], lower_trap)
		lower_trap.nw = lower_list[-1]
		lower_list[-1].ne = lower_trap
		lower_list.append(lower_trap)
		Lower_Trap_node = Tree(lower_trap)
	
	right_trap = Trapezoid(Delta[-1].top, Delta[-1].bot, line.q, Delta[-1].rightp)
	
	# Update D for Delta[-1]
	Right_Trap_node = Tree(right_trap)
	Right_Line_node = Tree(line, Upper_Trap_node, Lower_Trap_node)
	Q_node = D._find_node(line.q)
	Q_node.content = line.q
	Q_node.left = Right_Line_node
	Q_node.right = Right_Trap_node
	
	# Set neighbors of rightmost trapezoid and back-pointers
	right_trap.ne = Delta[-1].ne
	if Delta[-1].ne is not None:
		Delta[-1].ne.replace_neighbor(Delta[-1], right_trap)
	right_trap.se = Delta[-1].se
	if Delta[-1].se is not None:
		Delta[-1].se.replace_neighbor(Delta[-1], right_trap)
	right_trap.nw = upper_list[-1]
	right_trap.sw = lower_list[-1]
	upper_list[-1].ne = right_trap
	lower_list[-1].se = right_trap
	
	T.add(right_trap)
	T.update(upper_list)
	T.update(lower_list)

def handle_multiple_trapezoids_right_touching(T, D, Delta, line):
	left_trap = Trapezoid(Delta[0].top, Delta[0].bot, Delta[0].leftp, line.p)
	
	# Create first trapezoid above the line
	upper_trap = Trapezoid(Delta[0].top, line, line.p, Delta[0].rightp)
	upper_trap.ne = Delta[0].ne # Only for unique x-coordinates
	if Delta[0].ne is not None:
		Delta[0].ne.replace_neighbor(Delta[0], upper_trap)
	upper_list = [upper_trap]
	
	# Create first trapezoid below the line
	lower_trap = Trapezoid(line, Delta[0].bot, line.p, Delta[0].rightp)
	lower_trap.se = Delta[0].se
	if Delta[0].se is not None:
		Delta[0].se.replace_neighbor(Delta[0], lower_trap)
	lower_list = [lower_trap]
	
	# Update D for Delta[0]
	Left_Trap_node = Tree(left_trap)
	Upper_Trap_node = Tree(upper_trap)
	Lower_Trap_node = Tree(lower_trap)
	Left_Line_node = Tree(line, Upper_Trap_node, Lower_Trap_node)
	P_node = D._find_node(line.p)
	P_node.content = line.p
	P_node.left = Left_Trap_node
	P_node.right = Left_Line_node
	
	for old_trap in Delta[1:-1]:
		# Handle trapezoids above the line
		if old_trap.top is upper_list[-1].top:
			upper_list[-1].rightp = old_trap.rightp
			upper_list[-1].ne = old_trap.ne
			if old_trap.ne is not None:
				old_trap.ne.replace_neighbor(old_trap, upper_list[-1])
		else:
			upper_trap = Trapezoid(old_trap.top, line, old_trap.leftp, old_trap.rightp)
			upper_trap.nw = old_trap.nw
			if old_trap.nw is not None:
				old_trap.nw.replace_neighbor(old_trap, upper_trap)
			upper_trap.ne = old_trap.ne
			if old_trap.ne is not None:
				old_trap.ne.replace_neighbor(old_trap, upper_trap)
			upper_trap.sw = upper_list[-1]
			upper_list[-1].se = upper_trap
			upper_list.append(upper_trap)
			Upper_Trap_node = Tree(upper_trap)
		
		# Handle trapezoids below the line
		if old_trap.bot is lower_list[-1].bot:
			lower_list[-1].rightp = old_trap.rightp
			lower_list[-1].se = old_trap.se
			if old_trap.se is not None:
				old_trap.se.replace_neighbor(old_trap, lower_list[-1])
		else:
			lower_trap = Trapezoid(line, old_trap.bot, old_trap.leftp, old_trap.rightp)
			lower_trap.sw = old_trap.sw
			if old_trap.sw is not None:
				old_trap.sw.replace_neighbor(old_trap, lower_trap)
			lower_trap.se = old_trap.se
			if old_trap.se is not None:
				old_trap.se.replace_neighbor(old_trap, lower_trap)
			lower_trap.nw = lower_list[-1]
			lower_list[-1].ne = lower_trap
			lower_list.append(lower_trap)
			Lower_Trap_node = Tree(lower_trap)
		
		point_in_old_trap = Point( (old_trap.leftp.x + old_trap.rightp.x)/2, line.eval((old_trap.leftp.x + old_trap.rightp.x)/2) )
		S_node = D._find_node(point_in_old_trap)
		S_node.content = line
		S_node.left = Upper_Trap_node
		S_node.right = Lower_Trap_node
	
	# Create last trapezoid above the line
	if upper_list[-1].top is Delta[-1].top:
		upper_list[-1].rightp = line.q
	else:
		upper_trap = Trapezoid(Delta[-1].top, line, Delta[-1].leftp, line.q)
		upper_trap.nw = Delta[-1].nw
		if Delta[-1].nw is not None:
			Delta[-1].nw.replace_neighbor(Delta[-1], upper_trap)
		upper_trap.sw = upper_list[-1]
		upper_list[-1].se = upper_trap
		upper_list.append(upper_trap)
		Upper_Trap_node = Tree(upper_trap)
	
	# Create last trapezoid below the line
	if lower_list[-1].bot is Delta[-1].bot:
		lower_list[-1].rightp = line.q
	else:
		lower_trap = Trapezoid(line, Delta[-1].bot, Delta[-1].leftp, line.q)
		lower_trap.sw = Delta[-1].sw
		if Delta[-1].sw is not None:
			Delta[-1].sw.replace_neighbor(Delta[-1], lower_trap)
		lower_trap.nw = lower_list[-1]
		lower_list[-1].ne = lower_trap
		lower_list.append(lower_trap)
		Lower_Trap_node = Tree(lower_trap)
	
	# Update D for Delta[-1]
	search_point = Point( (Delta[-1].leftp.x + Delta[-1].rightp.x)/2, line.eval((Delta[-1].leftp.x + Delta[-1].rightp.x)/2) )
	S_node = D._find_node(search_point)
	S_node.content = line
	S_node.left = Upper_Trap_node
	S_node.right = Lower_Trap_node
	
	# Set neighbors of leftmost trapezoid and back-pointers
	left_trap.nw = Delta[0].nw
	if Delta[0].nw is not None:
		Delta[0].nw.replace_neighbor(Delta[0], left_trap)
	left_trap.sw = Delta[0].sw
	if Delta[0].sw is not None:
		Delta[0].sw.replace_neighbor(Delta[0], left_trap)
	left_trap.ne = upper_list[0]
	left_trap.se = lower_list[0]
	upper_list[0].nw = left_trap
	lower_list[0].sw = left_trap
	
	# Set neighbors of rightmost trapezoids and back-pointers
	upper_list[-1].ne = Delta[-1].ne
	if Delta[-1].ne is not None:
		Delta[-1].ne.replace_neighbor(Delta[-1], upper_list[-1])
	lower_list[-1].se = Delta[-1].se
	if Delta[-1].se is not None:
		Delta[-1].se.replace_neighbor(Delta[-1], lower_list[-1])
	
	T.add(left_trap)
	T.update(upper_list)
	T.update(lower_list)

def handle_multiple_trapezoids_both_touching(T, D, Delta, line):
	# Create first trapezoid above the line
	upper_trap = Trapezoid(Delta[0].top, line, line.p, Delta[0].rightp)
	upper_trap.nw = Delta[0].nw
	if Delta[0].nw is not None:
		Delta[0].nw.replace_neighbor(Delta[0], upper_trap)
	upper_trap.ne = Delta[0].ne # Only for unique x-coordinates
	if Delta[0].ne is not None:
		Delta[0].ne.replace_neighbor(Delta[0], upper_trap)
	upper_list = [upper_trap]
	
	# Create first trapezoid below the line
	lower_trap = Trapezoid(line, Delta[0].bot, line.p, Delta[0].rightp)
	lower_trap.sw = Delta[0].sw
	if Delta[0].sw is not None:
		Delta[0].sw.replace_neighbor(Delta[0], lower_trap)
	lower_trap.se = Delta[0].se
	if Delta[0].se is not None:
		Delta[0].se.replace_neighbor(Delta[0], lower_trap)
	lower_list = [lower_trap]
	
	# Update D for Delta[0]
	Upper_Trap_node = Tree(upper_trap)
	Lower_Trap_node = Tree(lower_trap)
	search_point = Point( (Delta[0].leftp.x + Delta[0].rightp.x)/2, line.eval( (Delta[0].leftp.x + Delta[0].rightp.x)/2 ) )
	S_node = D._find_node(search_point)
	S_node.content = line
	S_node.left = Upper_Trap_node
	S_node.right = Lower_Trap_node
	
	for old_trap in Delta[1:-1]:
		# Handle trapezoids above the line
		if old_trap.top is upper_list[-1].top:
			upper_list[-1].rightp = old_trap.rightp
			upper_list[-1].ne = old_trap.ne
			if old_trap.ne is not None:
				old_trap.ne.replace_neighbor(old_trap, upper_list[-1])
		else:
			upper_trap = Trapezoid(old_trap.top, line, old_trap.leftp, old_trap.rightp)
			upper_trap.nw = old_trap.nw
			if old_trap.nw is not None:
				old_trap.nw.replace_neighbor(old_trap, upper_trap)
			upper_trap.ne = old_trap.ne
			if old_trap.ne is not None:
				old_trap.ne.replace_neighbor(old_trap, upper_trap)
			upper_trap.sw = upper_list[-1]
			upper_list[-1].se = upper_trap
			upper_list.append(upper_trap)
			Upper_Trap_node = Tree(upper_trap)
		
		# Handle trapezoids below the line
		if old_trap.bot is lower_list[-1].bot:
			lower_list[-1].rightp = old_trap.rightp
			lower_list[-1].se = old_trap.se
			if old_trap.se is not None:
				old_trap.se.replace_neighbor(old_trap, lower_list[-1])
		else:
			lower_trap = Trapezoid(line, old_trap.bot, old_trap.leftp, old_trap.rightp)
			lower_trap.sw = old_trap.sw
			if old_trap.sw is not None:
				old_trap.sw.replace_neighbor(old_trap, lower_trap)
			lower_trap.se = old_trap.se
			if old_trap.se is not None:
				old_trap.se.replace_neighbor(old_trap, lower_trap)
			lower_trap.nw = lower_list[-1]
			lower_list[-1].ne = lower_trap
			lower_list.append(lower_trap)
			Lower_Trap_node = Tree(lower_trap)
		
		point_in_old_trap = Point( (old_trap.leftp.x + old_trap.rightp.x)/2, line.eval((old_trap.leftp.x + old_trap.rightp.x)/2) )
		S_node = D._find_node(point_in_old_trap)
		S_node.content = line
		S_node.left = Upper_Trap_node
		S_node.right = Lower_Trap_node
	
	# Create last trapezoid above the line
	if upper_list[-1].top is Delta[-1].top:
		upper_list[-1].rightp = line.q
	else:
		upper_trap = Trapezoid(Delta[-1].top, line, Delta[-1].leftp, line.q)
		upper_trap.nw = Delta[-1].nw
		if Delta[-1].nw is not None:
			Delta[-1].nw.replace_neighbor(Delta[-1], upper_trap)
		upper_trap.sw = upper_list[-1]
		upper_list[-1].se = upper_trap
		upper_list.append(upper_trap)
		Upper_Trap_node = Tree(upper_trap)
	
	# Create last trapezoid below the line
	if lower_list[-1].bot is Delta[-1].bot:
		lower_list[-1].rightp = line.q
	else:
		lower_trap = Trapezoid(line, Delta[-1].bot, Delta[-1].leftp, line.q)
		lower_trap.sw = Delta[-1].sw
		if Delta[-1].sw is not None:
			Delta[-1].sw.replace_neighbor(Delta[-1], lower_trap)
		lower_trap.nw = lower_list[-1]
		lower_list[-1].ne = lower_trap
		lower_list.append(lower_trap)
		Lower_Trap_node = Tree(lower_trap)
	
	# Update D for Delta[-1]
	search_point = Point( (Delta[-1].leftp.x + Delta[-1].rightp.x)/2, line.eval((Delta[-1].leftp.x + Delta[-1].rightp.x)/2) )
	S_node = D._find_node(search_point)
	S_node.content = line
	S_node.left = Upper_Trap_node
	S_node.right = Lower_Trap_node
	
	# Setneighbors of rightmost trapezoids and back-pointers
	upper_list[-1].ne = Delta[-1].ne
	if Delta[-1].ne is not None:
		Delta[-1].ne.replace_neighbor(Delta[-1], upper_list[-1])
	lower_list[-1].se = Delta[-1].se
	if Delta[-1].se is not None:
		Delta[-1].se.replace_neighbor(Delta[-1], lower_list[-1])
	
	T.update(upper_list)
	T.update(lower_list)

def assign_face(trapezoid, face_index):
	if trapezoid is not None:
		if not hasattr(trapezoid, 'face_index'):
			trapezoid.face_index = face_index
			
			assign_face(trapezoid.nw, face_index)
			assign_face(trapezoid.ne, face_index)
			assign_face(trapezoid.sw, face_index)
			assign_face(trapezoid.se, face_index)
			
			return True
	return False

def assign_faces(T):
	face_index = 0
	for trapezoid in T:
		if assign_face(trapezoid, face_index):
			face_index += 1

def construct_trapezoid_decomposition(edges):
	T, D = initialize(edges)
	random.shuffle(edges) # FIXME
	for line in edges:
		#~ print('--------------------')
		#~ print('\nT:\n{0}'.format(T))
		#~ print('D:\n{0}'.format(D))
		#~ print('\nAdding line {0}'.format(line))
		#~ print('--------------------')
		#~ vis.draw_decomposition(T)
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
				handle_one_trapezoid_both_touching(T, D, delta0, line)
		else:
			if line.p.x > H[0].leftp.x and line.q.x < H[-1].rightp.x:
				handle_multiple_trapezoids_completely_inside(T, D, H, line)
			elif line.p.x == H[0].leftp.x and line.q.x < H[-1].rightp.x:
				handle_multiple_trapezoids_left_touching(T, D, H, line)
			elif line.p.x > H[0].leftp.x and line.q.x == H[-1].rightp.x:
				handle_multiple_trapezoids_right_touching(T, D, H, line)
			else: # line.p.x == H[0].leftp.x and line.q.x == H[-1].rightp.x:
				handle_multiple_trapezoids_both_touching(T, D, H, line)
		
	return T, D

def group_points(D, queries):
	groups = {}
	
	for query in queries:
		trapezoid = D.find(query)
		face = trapezoid.face_index
		
		if face not in groups:
			groups[face] = [queries.index(query)]
		else:
			groups[face].append(queries.index(query))
	
	return list(groups.values())

dataset_filename = 'data/punktlokalisierung_example'
#~ dataset_filename = 'data/multiple_intersections_completely_inside_example'
vertices, edges, queries = read_dataset(dataset_filename)

#~ vis.draw_scenario(vertices, edges, queries)
T, D = construct_trapezoid_decomposition(edges)
assign_faces(T)
groups = group_points(D, queries)
#~ vis.draw_decomposition(T, D, queries)

result_filename = 'result'
write_result(result_filename, groups)











