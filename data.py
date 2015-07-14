import random

#~ m = 3/2 n - 2
#~ 2(m+2)/3 = n

#~ m must be of the form m = 4 + 3x, for x in N_0
M = [4 + 3 * 10**x for x in range(5)]
for m in M:
	n = 2*(m+2)//3
	
	points = []
	length = max(2 * n, 4)
	for i in range(n // 2):
		points.append((2*i, 2*i))
		points.append((2*i+length, 2*i))

	lines = []
	for index, point in enumerate(points[:-2]):
		if index % 2 == 0:
			lines.append((index, index+1))
		lines.append((index, index+2))
	lines.append((len(points)-2, len(points)-1))
	
	queries = []
	for i in range(n // 2 - 1):
		x = random.uniform(2*i + 1, 2*i+length - 1)
		y = random.uniform(2*i, 2*(i+1))
		queries.append((x, y))

	filename = 'data/point_localization_{0}'.format(m)
	n, m, l = len(points), len(lines), len(queries)
	with open(filename, 'w') as f:
		f.write('{0} {1} {2}\n'.format(n, m, l))
		for x, y in points:
			f.write('{0} {1}\n'.format(x, y))
		for p, q in lines:
			f.write('{0} {1}\n'.format(p+1, q+1))
		for x, y in queries:
			f.write('{0} {1}\n'.format(x, y))
