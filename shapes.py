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
		det = line.q.x * self.y + line.p.x * line.q.y + line.p.y * self.x
		det -= line.p.y * line.q.x + line.q.y * self.x + self.y * line.p.x
		return det > 0
	
	def __str__(self, indent=0, indent_string = '  '):
		string_representation = indent_string * indent
		string_representation += 'Po: ({0},{1})'.format(self.x, self.y)
		return string_representation

class Line:
	def __init__(self, p, q):
		self.p = p
		self.q = q
	
	def eval(self, x_coord):
		try:
			slope = (self.q.y - self.p.y) / (self.q.x - self.p.x)
			intersect = self.p.y - slope * self.p.x
			return slope * x_coord + intersect
		except ZeroDivisionError:
			return self.p.y
	
	def __str__(self, indent=0, indent_string = '  '):
		string_representation = indent_string * indent
		string_representation += 'Li: ({0},{1}->{2},{3})'.format(self.p.x, self.p.y, self.q.x, self.q.y)
		return string_representation

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
	
	def replace_neighbor(self, old, new):
		if self.nw is old:
			self.nw = new
		elif self.ne is old:
			self.ne = new
		elif self.sw is old:
			self.sw = new
		elif self.se is old:
			self.se = new		
		else:
			raise Exception('Unlinked neighbor!')
	
	def __str__(self, indent=0, indent_string = '  '):
		string_representation = indent_string * indent
		string_representation += 'Tr: Top={0}, Bot={1}, LeftP={2}, RightP={3}'
		#~ string_representation += ' nw={4}, ne={5}, sw={6}, se={7}'
		#~ return string_representation.format(self.top, self.bot, self.leftp, self.rightp, nw, ne, sw, se)
		return string_representation.format(self.top, self.bot, self.leftp, self.rightp)






