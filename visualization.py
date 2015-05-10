import tkinter as tk

canvasSizeX = 400
canvasSizeY = 400

def getUpperLimits(pointSets):
	maxX, maxY = pointSets[0][0].x, pointSets[0][0].y
	for pointSet in pointSets:
		for point in pointSet:
			maxX = max(point.x, maxX)
			maxY = max(point.y, maxY)
	return maxX, maxY

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
		xI = scaling * edge.left.x + offset
		yI = canvasSizeY - (scaling * edge.left.y + offset)
		xJ = scaling * edge.right.x + offset
		yJ = canvasSizeY - (scaling * edge.right.y + offset)
		surface.create_line(xI, yI, xJ, yJ, width = 2)
	for query in queries:
		x = scaling * query.x + offset
		y = canvasSizeY - (scaling * query.y + offset)
		surface.create_oval(x-4, y-4, x+4, y+4, fill = 'black')
		
	root.mainloop()
