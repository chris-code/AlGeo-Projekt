import tkinter as tk
from shapes import *

canvasSizeX = 400
canvasSizeY = 400
colors = ['blue', 'red', 'green', 'yellow', 'cyan', 'magenta']

def make_surface():
	window = tk.Tk()
	window.resizable(tk.FALSE, tk.FALSE)
	canv = tk.Canvas(window, width = canvasSizeX, height = canvasSizeY)
	canv.pack()
	
	return window, canv

def show_surface(surface):
	window, canv = surface
	
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

def draw_point(canv, point, color='black'):
	x = point.x
	y = canvasSizeY - point.y
	canv.create_oval(x-0.2, y-0.2, x+0.2, y+0.2, fill=color)

def draw_line(canv, p, q, color='black'):
	px = p.x
	py = canvasSizeY - p.y
	qx = q.x
	qy = canvasSizeY - q.y
	canv.create_line(px, py, qx, qy, width = 2, fill=color)

def draw_trapezoid(canv, top, bot, leftp, rightp, color='black'):
	nw = Point(leftp.x, top.eval(leftp.x))
	ne = Point(rightp.x, top.eval(rightp.x))
	sw = Point(leftp.x, bot.eval(leftp.x))
	se = Point(rightp.x, bot.eval(rightp.x))
	
	draw_line(canv, nw, ne, color=color)
	draw_line(canv, ne, se, color=color)
	draw_line(canv, se, sw, color=color)
	draw_line(canv, sw, nw, color=color)

def draw_decomposition(surface, T, D=None, queries=[]):
	window, canv = surface
	#~ window, canv = make_surface()
	
	for trapezoid in T:
		draw_trapezoid(canv, trapezoid.top, trapezoid.bot, trapezoid.leftp, trapezoid.rightp)
	
	for index, q in enumerate(queries):
		trap = D.find(q)
		shrinkage = 0.1
		top = Line(Point(trap.top.p.x, trap.top.p.y - shrinkage), Point(trap.top.q.x, trap.top.q.y - shrinkage))
		bot = Line(Point(trap.bot.p.x, trap.bot.p.y+0.1), Point(trap.bot.q.x, trap.bot.q.y + shrinkage))
		leftp = Point(trap.leftp.x+0.1, trap.leftp.y)
		rightp = Point(trap.rightp.x-0.1, trap.rightp.y)
		
		if not hasattr(trap, 'color'):
			trap.color = colors[index % len(colors)]
		draw_trapezoid(canv, top, bot, leftp, rightp, color=trap.color)
		draw_point(canv, q, color=trap.color)
	
	#~ show_surface(window, canv)

def draw_scenario(surface, vertices, edges, queries):
	window, canv = surface
	#~ window, canv = make_surface()
	
	for vertex in vertices:
		draw_point(canv, vertex)
	for edge in edges:
		draw_line(canv, edge.p, edge.q)
	for query in queries:
		draw_point(canv, query, color='blue')
	
	#~ show_surface(window, canv)














