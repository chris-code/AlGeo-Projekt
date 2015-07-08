class Point:
	class_counter = 0
	def __init__(self, x, y):
		self.x = x
		self.y = y
		
		self.ident = Point.class_counter
		Point.class_counter += 1
	
	def is_left_of(self, point):
		return self.x < point.x
		
	def is_right_of(self, point):
		return self.x > point.x
	
	def is_above(self, line):
		# Sarrus scheme
		det = line.q.x * self.y + line.p.x * line.q.y + line.p.y * self.x - line.p.y * line.q.x - line.q.y * self.x - self.y * line.p.x
		return det > 0
	
	def __str__(self, indent=0, indent_string = '  '):
		string_representation = indent_string * indent
		string_representation += 'Po{0}: ({1},{2})'.format(self.ident, self.x, self.y)
		return string_representation

class Line:
	class_counter = 0
	def __init__(self, p, q):
		self.p = p
		self.q = q
		self.ident = Line.class_counter
		Line.class_counter += 1
	
	def eval(self, point):
		try:
			slope = (self.q.y - self.p.y) / (self.q.x - self.p.x)
			intersect = self.p.y - slope * self.p.x
			return slope * point + intersect
		except ZeroDivisionError:
			return self.p.y
	
	def __str__(self, indent=0, indent_string = '  '):
		string_representation = indent_string * indent
		string_representation += 'Li{0}: ({1},{2}->{3},{4})'.format(self.ident, self.p.x, self.p.y, self.q.x, self.q.y)
		return string_representation

class Trapezoid:
	class_counter = 0
	def __init__(self, top, bot, leftp, rightp):
		self.top = top
		self.bot = bot
		self.leftp = leftp
		self.rightp = rightp
		
		self.nw = None
		self.ne = None
		self.sw = None
		self.se = None
		
		self.ident = Trapezoid.class_counter
		Trapezoid.class_counter += 1
	
	def __str__(self, indent=0, indent_string = '  '):
		string_representation = indent_string * indent
		string_representation += 'Tr{0}: Top={1}, Bot={2}, LeftP={3}, RightP={4}'
		string_representation += ' nw={5}, ne={6}, sw={7}, se={8}'
		nw, ne, sw, se = None, None, None, None
		if self.nw is not None:
			nw = self.nw.ident
		if self.ne is not None:
			ne = self.ne.ident
		if self.sw is not None:
			sw = self.sw.ident
		if self.se is not None:
			se = self.se.ident
		return string_representation.format(self.ident, self.top, self.bot, self.leftp, self.rightp, nw, ne, sw, se)
