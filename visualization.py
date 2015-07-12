import tkinter as tk
from shapes import *

canvasSizeX = 400
canvasSizeY = 400
colors = ['blue', 'red', 'green', 'yellow', 'cyan', 'magenta']

def _get_limits(points):
	min_x, max_x, min_y, max_y = 1000, -1000, 1000, -1000
	for point in points:
		min_x = min(min_x, point.x)
		max_x = max(max_x, point.x)
		min_y = min(min_y, point.y)
		max_y = max(max_y, point.y)
	return min_x, max_x, min_y, max_y

def draw_point(canv, point, scaling, offset, color='black'):
	x = scaling * point.x + offset
	y = canvasSizeY - (scaling * point.y + offset)
	canv.create_oval(x-4, y-4, x+4, y+4, fill=color)

def draw_line(canv, p, q, scaling, offset, color='black'):
	px = scaling * p.x + offset
	py = canvasSizeY - (scaling * p.y + offset)
	qx = scaling * q.x + offset
	qy = canvasSizeY - (scaling * q.y + offset)
	canv.create_line(px, py, qx, qy, width = 2, fill=color)

#~ TODO draw_trapezoid method
def draw_trapezoid(canv, top, bot, leftp, rightp, scaling, offset, color='black'):
	nw = Point(leftp.x, top.eval(leftp.x))
	ne = Point(rightp.x, top.eval(rightp.x))
	sw = Point(leftp.x, bot.eval(leftp.x))
	se = Point(rightp.x, bot.eval(rightp.x))
	
	draw_line(canv, nw, ne, scaling, offset, color=color)
	draw_line(canv, ne, se, scaling, offset, color=color)
	draw_line(canv, se, sw, scaling, offset, color=color)
	draw_line(canv, sw, nw, scaling, offset, color=color)

def draw_decomposition(T, D=None, queries=[]):
	root = tk.Tk()
	root.resizable(tk.FALSE, tk.FALSE)
	canv = tk.Canvas(root, width=canvasSizeX, height=canvasSizeY)
	canv.pack()
	
	points = [trapezoid.top.p for trapezoid in T]
	points += [trapezoid.top.q for trapezoid in T]
	points += [trapezoid.bot.p for trapezoid in T]
	points += [trapezoid.bot.q for trapezoid in T]
	min_x, max_x, min_y, max_y = _get_limits(points)
	offset = max(canvasSizeX, canvasSizeY) / 8 # Min. distance to borders
	scaling = (min(canvasSizeX, canvasSizeY) - 2 * offset) / max(max_x - min_x, max_y - min_y)
	offset -= scaling * min(min_x, min_y)
	
	for trapezoid in T:
		draw_trapezoid(canv, trapezoid.top, trapezoid.bot, trapezoid.leftp, trapezoid.rightp, scaling, offset)
		#~ FIXME this is to test that there are no 0-width trapezoids left
		#~ Remove once this is achieved
		#~ print('Width={0}'.format(trapezoid.rightp.x - trapezoid.leftp.x))
	
	for index, q in enumerate(queries):
		trap = D.find(q)
		shrinkage = 0.1
		top = Line(Point(trap.top.p.x, trap.top.p.y - shrinkage), Point(trap.top.q.x, trap.top.q.y - shrinkage))
		bot = Line(Point(trap.bot.p.x, trap.bot.p.y+0.1), Point(trap.bot.q.x, trap.bot.q.y + shrinkage))
		leftp = Point(trap.leftp.x+0.1, trap.leftp.y)
		rightp = Point(trap.rightp.x-0.1, trap.rightp.y)
		
		if not hasattr(trap, 'color'):
			trap.color = colors[index % len(colors)]
		draw_trapezoid(canv, top, bot, leftp, rightp, scaling, offset, color=trap.color)
		draw_point(canv, q, scaling, offset, color=trap.color)
	
	root.mainloop()

def draw_scenario(vertices, edges, queries):
	min_x, max_x, min_y, max_y = _get_limits(vertices + queries)
	offset = max(canvasSizeX, canvasSizeY) / 8 # Min. distance to borders
	scaling = (min(canvasSizeX, canvasSizeY) - 2 * offset) / max(max_x - min_x, max_y - min_y)
	offset -= scaling * min(min_x, min_y)
	
	root = tk.Tk()
	root.resizable(tk.FALSE, tk.FALSE)

	canv = tk.Canvas(root, width = canvasSizeX, height = canvasSizeY)
	canv.pack()
	for vertex in vertices:
		draw_point(canv, vertex, scaling, offset)
	for edge in edges:
		draw_line(canv, edge.p, edge.q, scaling, offset)
	for query in queries:
		draw_point(canv, query, scaling, offset, color='blue')
		
	root.mainloop()














