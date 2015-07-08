import tkinter as tk
from shapes import *

canvasSizeX = 400
canvasSizeY = 400

def get_limits(points):
	min_x, max_x, min_y, max_y = 1000, -1000, 1000, -1000
	for point in points:
		min_x = min(min_x, point.x)
		max_x = max(max_x, point.x)
		min_y = min(min_y, point.y)
		max_y = max(max_y, point.y)
	return min_x, max_x, min_y, max_y

def draw_point(canv, point, scaling, offset):
	x = scaling * point.x + offset
	y = canvasSizeY - (scaling * point.y + offset)
	canv.create_oval(x-4, y-4, x+4, y+4, fill='black')

def draw_line(canv, p, q, scaling, offset):
	px = scaling * p.x + offset
	py = canvasSizeY - (scaling * p.y + offset)
	qx = scaling * q.x + offset
	qy = canvasSizeY - (scaling * q.y + offset)
	canv.create_line(px, py, qx, qy, width = 2)

def visualizePointLocalization(vertices, edges, queries):
	min_x, max_x, min_y, max_y = get_limits(vertices + queries)
	offset = max(canvasSizeX, canvasSizeY) / 8 # Min. distance to borders
	scaling = (min(canvasSizeX, canvasSizeY) - 2 * offset) / max(max_x, max_y)
	
	root = tk.Tk()
	root.resizable(tk.FALSE, tk.FALSE)

	canv = tk.Canvas(root, width = canvasSizeX, height = canvasSizeY)
	canv.pack()
	for vertex in vertices:
		draw_point(canv, vertex, scaling, offset)
	for edge in edges:
		draw_line(canv, edge.p, edge.q, scaling, offset)
	for query in queries:
		draw_point(canv, query, scaling, offset)
		
	root.mainloop()

def draw_decomposition(T):
	root = tk.Tk()
	root.resizable(tk.FALSE, tk.FALSE)
	canv = tk.Canvas(root, width=canvasSizeX, height=canvasSizeY)
	canv.pack()
	
	points = [trapezoid.top.p for trapezoid in T]
	points += [trapezoid.top.q for trapezoid in T]
	points += [trapezoid.bot.p for trapezoid in T]
	points += [trapezoid.bot.q for trapezoid in T]
	min_x, max_x, min_y, max_y = get_limits(points)
	
	offset = max(canvasSizeX, canvasSizeY) / 8 # Min. distance to borders
	scaling = (min(canvasSizeX, canvasSizeY) - 2 * offset) / max(max_x, max_y)
	
	for trapezoid in T:
		draw_line(canv, trapezoid.top.p, trapezoid.top.q, scaling, offset)
		draw_line(canv, trapezoid.bot.p, trapezoid.bot.q, scaling, offset)
		
		p1 = Point(trapezoid.leftp.x, trapezoid.top.eval(trapezoid.leftp.x))
		p2 = Point(trapezoid.leftp.x, trapezoid.bot.eval(trapezoid.leftp.x))
		draw_line(canv, p1, p2, scaling, offset)
		
		p3 = Point(trapezoid.rightp.x, trapezoid.top.eval(trapezoid.rightp.x))
		p4 = Point(trapezoid.rightp.x, trapezoid.bot.eval(trapezoid.rightp.x))
		draw_line(canv, p3, p4, scaling, offset)
		
		#~ FIXME this is to test that there are no 0-width trapezoids left
		#~ Remove once this is achieved
		#~ print('Width={0}'.format(trapezoid.rightp.x - trapezoid.leftp.x))
	
	root.mainloop()
















