import collections as col
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

def remove_obstructed_space(T, D, valid_point):
	valid_trapezoid = D.find(valid_point)
	valid_face_index = valid_trapezoid.face_index
	
	invalid_trapezoids = set()
	for trapezoid in T:
		if trapezoid.face_index != valid_face_index:
			invalid_trapezoids.add(trapezoid)
	T -= invalid_trapezoids

def construct_road_map(T):
	for trap in T:
		center_x = (trap.leftp.x + trap.rightp.x)/2
		center_y = (trap.top.eval(center_x) + trap.bot.eval(center_x))/2
		trap.center = Point(center_x, center_y)
		trap.center.neighbors = []
	
	for trap in T:
		connecting_point_x = trap.rightp.x
		
		if trap.ne is not None:
			connecting_point_y = (trap.top.eval(trap.rightp.x) + trap.rightp.y)/2
			connecting_point = Point(connecting_point_x, connecting_point_y)
			connecting_point.neighbors = [trap.center, trap.ne.center]
			trap.center.neighbors.append(connecting_point)
			trap.ne.center.neighbors.append(connecting_point)
		if trap.se is not None:
			connecting_point_y = (trap.bot.eval(trap.rightp.x) + trap.rightp.y)/2
			connecting_point = Point(connecting_point_x, connecting_point_y)
			connecting_point.neighbors = [trap.center, trap.se.center]
			trap.center.neighbors.append(connecting_point)
			trap.se.center.neighbors.append(connecting_point)

def find_path(T, D, start, end):
	start_trap = D.find(start)
	start_node = start_trap.center
	end_trap = D.find(end)
	end_node = end_trap.center
	
	if start_trap not in T or end_trap not in T:
		raise Exception('Start or end not in valid region')
	
	visited = set([start_node])
	queue = col.deque([start_node])
	while len(queue) > 0:
		node = queue.popleft()
		visited.add(node)
		if node is end_node:
			break
		else:
			for neighbor in node.neighbors:
				if neighbor not in visited:
					neighbor.pred = node
					queue.append(neighbor)
	else:
		raise Exception('No path found')
	
	path = [end_node]
	#~ while hasattr(path[-1], 'pred'):
	while path[-1] is not start_node:
		path.append(path[-1].pred)
	path.reverse()
	return path

dataset_filename = 'data/pfadsuche_example'
obstacle_points, obstacle_lines, queries = read_dataset(dataset_filename)

obstacle_points_flat = [point for sublist in obstacle_points for point in sublist]
obstacle_lines_flat = [line for sublist in obstacle_lines for line in sublist]

T, D = decomp.construct_trapezoid_decomposition(obstacle_lines_flat)
#~ vis.draw_decomposition(T)
decomp.assign_faces(T)

# Using first query point as cue what the valid face is
remove_obstructed_space(T, D, queries[0][0])
construct_road_map(T)

for query in queries:
	path = find_path(T, D, query[0], query[1])
	for node in path:
		print('{0} '.format(node), end='')
	print()

points = []
lines = []
for trap in T:
	points.append(trap.center)
	for neighbor in trap.center.neighbors:
		points.append(neighbor)
		lines.append(Line(trap.center, neighbor))
#~ surface = vis.make_surface()
#~ vis.draw_scenario(surface, points + obstacle_points_flat, lines + obstacle_lines_flat, [])
#~ vis.show_surface(surface)

surface = vis.make_surface()
vis.draw_scenario(surface, obstacle_points_flat, obstacle_lines_flat, [])
vis.show_surface(surface)






