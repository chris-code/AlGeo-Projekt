from shapes import *
import trapezoid_decomposition as decomp
import visualization as vis

def read_dataset(filename):
	with open(filename, 'r') as f:
		b, h, n, l = f.readline().strip().split()
		b, h, n, l = int(b), int(h), int(n), int(l)
		
		obstacle_points = []
		obstacle_lines = []
		for _ in range(n):
			points = []
			k = int( f.readline() )
			for _ in range(k):
				x, y = f.readline().strip().split()
				points.append( Point(int(x), int(y)) )
			obstacle_points.append(points)
			
			obstacle = []
			for index in range(len(points)):
				if points[index].x < points[(index + 1) % len(points)].x:
					obstacle.append( Line(points[index], points[(index + 1) % len(points)]) )
				else:
					obstacle.append( Line(points[(index + 1) % len(points)], points[index]) )
			obstacle_lines.append(obstacle)
		
		queries = []
		for _ in range(l):
			a_x, a_y = f.readline().strip().split()
			z_x, z_y = f.readline().strip().split()
			queries.append(( Point(int(a_x), int(a_y)), Point(int(z_x), int(z_y))) )
		
		return obstacle_points, obstacle_lines, queries

dataset_filename = 'data/pfadsuche_example'
obstacle_points, obstacle_lines, queries = read_dataset(dataset_filename)

obstacle_points_flat = [point for sublist in obstacle_points for point in sublist]
obstacle_lines_flat = [line for sublist in obstacle_lines for line in sublist]

T, D = decomp.construct_trapezoid_decomposition(obstacle_lines_flat)
print(T)
vis.draw_decomposition(T)

#~ vis.draw_scenario(obstacle_points_flat, obstacle_lines_flat, [])
