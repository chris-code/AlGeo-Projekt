import sys
import collections as col
import argparse
from shapes import *
import trapezoid_decomposition as decomp
import visualization as vis

# Read obstacles and query points according to specification
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
				points.append( Point(float(x), float(y)) )
			obstacle_points.append(points)
			
			obstacle = []
			for index in range(len(points)):
				if points[index].is_left_of( points[(index + 1) % len(points)] ):
					obstacle.append( Line(points[index], points[(index + 1) % len(points)]) )
				else:
					obstacle.append( Line(points[(index + 1) % len(points)], points[index]) )
			obstacle_lines.append(obstacle)
		
		queries = []
		for _ in range(l):
			a_x, a_y = f.readline().strip().split()
			z_x, z_y = f.readline().strip().split()
			queries.append(( Point(float(a_x), float(a_y)), Point(float(z_x), float(z_y))) )
		
		return obstacle_points, obstacle_lines, queries

# Write calculated paths to file
def write_result(filename, paths):
	with open(filename, 'w') as f:
		for path in paths:
			f.write('{0}\n'.format(len(path)))
			for point in path:
				f.write('{0} {1}\n'.format(point.x, point.y))

# Remove those trapezoids from T that correspond to obstacles.
def remove_obstructed_space(T, D, valid_point):
	# Find the face that is the valid space
	valid_trapezoid = D.find(valid_point)
	valid_face_index = valid_trapezoid.face_index
	
	# Remove the rest
	invalid_trapezoids = set()
	for trapezoid in T:
		if trapezoid.face_index != valid_face_index:
			invalid_trapezoids.add(trapezoid)
	T -= invalid_trapezoids

# Construct road map from 'T' by placing a node in each Trapezoids center.
# Also, each Trapezoid creates the nodes it shares with its right neighbors and
# links them accordingly.
# The trapezoids are given a pointer to their corresponding 'center' node
def construct_road_map(T):
	# Give each trapezoid a 'center' node
	for trap in T:
		center_x = (trap.leftp.x + trap.rightp.x)/2
		center_y = (trap.top.eval(center_x) + trap.bot.eval(center_x))/2
		trap.center = Point(center_x, center_y)
		trap.center.neighbors = []
	
	# Create nodes shared with right neighbors
	for trap in T:
		connecting_point_x = trap.rightp.x
		
		# Node shared with north-east neighbor
		if trap.ne is not None:
			connecting_point_y = (trap.top.eval(trap.rightp.x) + trap.rightp.y)/2
			connecting_point = Point(connecting_point_x, connecting_point_y)
			connecting_point.neighbors = [trap.center, trap.ne.center]
			trap.center.neighbors.append(connecting_point)
			trap.ne.center.neighbors.append(connecting_point)
		
		# Node shared with south-east neighbor
		if trap.se is not None:
			connecting_point_y = (trap.bot.eval(trap.rightp.x) + trap.rightp.y)/2
			connecting_point = Point(connecting_point_x, connecting_point_y)
			connecting_point.neighbors = [trap.center, trap.se.center]
			trap.center.neighbors.append(connecting_point)
			trap.se.center.neighbors.append(connecting_point)

# Uses the search structure 'D' and the road map reachable via 'T' to find
# a valid path from 'start' to 'end'
def find_path(T, D, start, end):
	# Find nodes containing 'start' and 'end'
	start_trap = D.find(start)
	start_node = start_trap.center
	end_trap = D.find(end)
	end_node = end_trap.center
	
	# 'start' and 'end' have to be in the valid space
	if start_trap not in T or end_trap not in T:
		raise Exception('Start or end not in valid region')
	
	# Breadth first search
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
	
	# Construct decomposition and assign 'face_index' to each trapezoid
	T, D = decomp.construct_trapezoid_decomposition(obstacle_lines_flat)
	decomp.assign_faces(T)

	# Using first query point as cue what the valid face is, and remove all
	# Trapezoids not in valid face. Then construct the road map on the remaining
	# Trapezoids
	remove_obstructed_space(T, D, queries[0][0])
	construct_road_map(T)
	
	# Compute path for each query point.
	# Since there is no output format specified for queries that have no
	# valid path, they are ignored.
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
	if args.visualize_decomposition or args.visualize_road_map or args.visualize_paths:
		vis.show_surface()
	
	write_result(result_filename, paths)
	
	sys.setrecursionlimit(1000)

if __name__ == '__main__':
	main()






