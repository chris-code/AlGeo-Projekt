import tkinter as tk
from shapes import *

canvasSizeX = 400
canvasSizeY = 400

# The colors that are used to show which point is assigned to which trapezoid
colors = ['blue', 'red', 'green', 'yellow', 'cyan', 'magenta']

# Global variables so that the user can call different draw functions that
# draw on the same canvas without having to supply the canvas as a handle
window, canv = None, None

# Set the window and canv global variables
def make_surface():
	global window, canv
	
	window = tk.Tk()
	window.resizable(tk.FALSE, tk.FALSE)
	canv = tk.Canvas(window, width = canvasSizeX, height = canvasSizeY)
	canv.pack()

# Show the drawn canvas, then purge the global variables window and canv
def show_surface():
	global window, canv
	
	if window is None or canv is None:
		raise Exception('Nothing was drawn!')
	
	# Scale everything
	min_x, max_x, min_y, max_y = 100000, -1000000, 100000, -100000
	for ident in canv.find_all():
		x1, y1, x2, y2 = canv.coords(ident)
		min_x = min(min_x, x1, x2)
		max_x = max(max_x, x1, x2)
		min_y = min(min_y, y1, y2)
		max_y = max(max_y, y1, y2)
	border = max(canvasSizeX, canvasSizeY) / 8 # Min. distance to borders
	scaling = (min(canvasSizeX, canvasSizeY) - 2 * border) / max(max_x - min_x, max_y - min_y)
	for ident in canv.find_all():
		canv.scale(ident, 0, 0, scaling, scaling)
		canv.move(ident, -min_x * scaling + border, -min_y * scaling + border)
	
	window.mainloop()
	window, canv = None, None

# point is a vis.Point object
def draw_point(point, color='black'):
	if window is None or canv is None:
		make_surface() # Make sure there is a surface to draw on
	
	x = point.x
	y = canvasSizeY - point.y
	canv.create_oval(x-0.2, y-0.2, x+0.2, y+0.2, fill=color)

# Draw line from p to q, where p and q are vis.Point objects
def draw_line(p, q, color='black'):
	if window is None or canv is None:
		make_surface() # Make sure there is a surface to draw on
	
	px = p.x
	py = canvasSizeY - p.y
	qx = q.x
	qy = canvasSizeY - q.y
	canv.create_line(px, py, qx, qy, width = 2, fill=color)

# top and bot are vis.Line objects, leftp and rightp are vis.Point objects
def draw_trapezoid(top, bot, leftp, rightp, color='black'):
	if window is None or canv is None:
		make_surface() # Make sure there is a surface to draw on
	
	# Calculate corner points
	nw = Point(leftp.x, top.eval(leftp.x))
	ne = Point(rightp.x, top.eval(rightp.x))
	sw = Point(leftp.x, bot.eval(leftp.x))
	se = Point(rightp.x, bot.eval(rightp.x))
	
	draw_line(nw, ne, color=color)
	draw_line(ne, se, color=color)
	draw_line(se, sw, color=color)
	draw_line(sw, nw, color=color)

# Draws the entire trapezoid decomposition T
def draw_decomposition(T, D=None, queries=[]):
	if window is None or canv is None:
		make_surface()
	
	for trapezoid in T:
		draw_trapezoid(trapezoid.top, trapezoid.bot, trapezoid.leftp, trapezoid.rightp)
		#TODO draw face number if present
		#~ if hasattr(trapezoid, 'face_index'):
			#~ x_pos = (trapezoid.leftp.x + trapezoid.rightp.x)/2
			#~ y_pos = (trapezoid.top.eval(x_pos) + trapezoid.bot.eval(x_pos))/2
			#~ canv.create_text(x_pos, y_pos, text=trapezoid.face_index)
	
	# Also draw query points and the trapezoids that contain them in the same color
	for index, q in enumerate(queries):
		# Draw the trapezoid slightly smaller so that shared edges don't overwrite each other
		trap = D.find(q)
		shrinkage = 0.1
		top = Line(Point(trap.top.p.x, trap.top.p.y - shrinkage), Point(trap.top.q.x, trap.top.q.y - shrinkage))
		bot = Line(Point(trap.bot.p.x, trap.bot.p.y+0.1), Point(trap.bot.q.x, trap.bot.q.y + shrinkage))
		leftp = Point(trap.leftp.x+0.1, trap.leftp.y)
		rightp = Point(trap.rightp.x-0.1, trap.rightp.y)
		
		if not hasattr(trap, 'color'):
			trap.color = colors[index % len(colors)]
		draw_trapezoid(top, bot, leftp, rightp, color=trap.color)
		draw_point(q, color=trap.color)

# Draws lists of vertices, edges and query points
# Query points are drawn in blue for clarity
def draw_scenario(vertices, edges, queries):
	if window is None or canv is None:
		make_surface() # Make sure there is a surface to draw on
	
	for vertex in vertices:
		draw_point(vertex)
	for edge in edges:
		draw_line(edge.p, edge.q)
	for query in queries:
		draw_point(query, color='blue')

# Draw the road map of T. This needs to be calculated beforehand and be
# accessible via the Trapezoid.center attribute.
def draw_road_map(T):
	if window is None or canv is None:
		make_surface() # Make sure there is a surface to draw on
	
	points = []
	lines = []
	for trap in T:
		draw_point(trap.center)
		for neighbor in trap.center.neighbors:
			draw_point(neighbor)
			draw_line(trap.center, neighbor)

# Draw a path
def draw_path(path):
	if window is None or canv is None:
		make_surface() # Make sure there is a surface to draw on
	
	for index, point in enumerate(path[:-1]):
		draw_point(point, color='blue')
		draw_line(point, path[(index+1) % len(path)])
	draw_point(path[-1], color='blue')












