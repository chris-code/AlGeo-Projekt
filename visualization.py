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

def getUpperLimits(pointSets):
	maxX, maxY = pointSets[0][0].x, pointSets[0][0].y
	for pointSet in pointSets:
		for point in pointSet:
			maxX = max(point.x, maxX)
			maxY = max(point.y, maxY)
	return maxX, maxY

def draw_line(canv, p, q, scaling, offset):
	px = scaling * p.x + offset
	py = canvasSizeY - (scaling * p.y + offset)
	qx = scaling * q.x + offset
	qy = canvasSizeY - (scaling * q.y + offset)
	canv.create_line(px, py, qx, qy, width = 2)

def visualizePointLocalization(vertices, edges, queries):
	maxX, maxY = getUpperLimits([vertices, queries]) # 'largest' point to draw
	offset = max(canvasSizeX, canvasSizeY) / 8 # Min. distance to borders
	scaling = (min(canvasSizeX, canvasSizeY) - 2 * offset) / max(maxX, maxY)
	
	root = tk.Tk()
	root.resizable(tk.FALSE, tk.FALSE)

	surface = tk.Canvas(root, width = canvasSizeX, height = canvasSizeY)
	surface.pack()
	for vertex in vertices:
		x = scaling * vertex.x + offset
		y = canvasSizeY - (scaling * vertex.y + offset)
		surface.create_oval(x-4, y-4, x+4, y+4, fill = 'black')
	for edge in edges:
		xI = scaling * edge.p.x + offset
		yI = canvasSizeY - (scaling * edge.p.y + offset)
		xJ = scaling * edge.q.x + offset
		yJ = canvasSizeY - (scaling * edge.q.y + offset)
		surface.create_line(xI, yI, xJ, yJ, width = 2)
	for query in queries:
		x = scaling * query.x + offset
		y = canvasSizeY - (scaling * query.y + offset)
		surface.create_oval(x-4, y-4, x+4, y+4, fill = 'black')
		
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
	
	root.mainloop()
















