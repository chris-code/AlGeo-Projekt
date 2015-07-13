import sys
import collections as col
import argparse
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

def write_result(filename, paths):
	with open(filename, 'w') as f:
		for path in paths:
			f.write('{0}\n'.format(len(path)))
			for point in path:
				f.write('{0} {1}\n'.format(point.x, point.y))

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
	
	# Backtrace path
	path = [end_node]
	while path[-1] is not start_node:
		path.append(path[-1].pred)
	path.reverse()
	
	# Add nodes for real start and end position
	path.insert(0, start)
	path.append(end)
	
	return path

def main():
	sys.setrecursionlimit(100000)
	
	argparser = argparse.ArgumentParser()
	argparser.add_argument('in_file', help='The file to read data from')
	argparser.add_argument('out_file', help='The file to store results in')
	argparser.add_argument('-d', '--visualize_decomposition', help='Draw trapezoid decomposition on screen', action='store_true')
	argparser.add_argument('-r', '--visualize_road_map', help='Draw road map on screen', action='store_true')
	argparser.add_argument('-p', '--visualize_paths', help='Draw calculated paths on screen', action='store_true')
	args = argparser.parse_args()
	dataset_filename = args.in_file
	result_filename = args.out_file
	
	obstacle_points, obstacle_lines, queries = read_dataset(dataset_filename)

	obstacle_points_flat = [point for sublist in obstacle_points for point in sublist]
	obstacle_lines_flat = [line for sublist in obstacle_lines for line in sublist]

	T, D = decomp.construct_trapezoid_decomposition(obstacle_lines_flat)
	decomp.assign_faces(T)

	# Using first query point as cue what the valid face is
	remove_obstructed_space(T, D, queries[0][0])
	construct_road_map(T)

	paths = []
	for query in queries:
		try:
			path = find_path(T, D, query[0], query[1])
			paths.append(path)
		except Exception:
			# No there is no path
			pass
	
	if args.visualize_decomposition:
		vis.draw_decomposition(T)
	if args.visualize_road_map:
		vis.draw_road_map(T)
	if args.visualize_paths:
		for path in paths:
			vis.draw_path(path)
	if args.visualize_decomposition or args.visualize_road_map:
		vis.show_surface()
	
	write_result(result_filename, paths)
	
	sys.setrecursionlimit(1000)

if __name__ == '__main__':
	main()






