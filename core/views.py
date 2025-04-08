
from django.http import JsonResponse
import random
from datetime import datetime
from geopy.distance import geodesic
from sklearn.cluster import DBSCAN
import numpy as np
from math import radians

def generate_mock_orders(n=10):
    base_lat, base_lon = 19.0760, 72.8777 
    orders = []

    for i in range(n):
        lat = base_lat + random.uniform(-0.02, 0.02)
        lon = base_lon + random.uniform(-0.02, 0.02)
        start_hour = random.randint(9, 16)
        end_hour = start_hour + random.randint(1, 3)

        orders.append({
            "order_id": f"ORD{i+1:03}",
            "location": {"lat": lat, "lon": lon},
            "time_window": [f"{start_hour}:00", f"{end_hour}:00"]
        })
    return orders

# def optimize_routes(request):
# 	orders = generate_mock_orders()
# 	unassigned = orders[:]
# 	groups = []
# 	agent_counter = 1
# 	while unassigned:
# 		seed = unassigned.pop(0)
# 		group = [seed]
# 		remaining = []
# 		for orders in unassigned:
# 			dist = geodesic(
# 				(seed['location']['lat'], seed['location']['lon']),
# 				(orders['location']['lat'], orders['location']['lon'])
# 			).km
# 			overlap = time_overlap(seed["time_window"], orders["time_window"])
# 			if dist <= 2.0:
# 				group.append(orders)
# 			else:
# 				remaining.append(orders)

# 		groups.append({
# 			"agent_id": f"AGENT_{agent_counter}",
# 			"orders": [o["order_id"] for o in group]
# 		})
# 		agent_counter += 1
# 		unassigned = remaining
# 	return JsonResponse(groups, safe=False)


def time_overlap(tw1, tw2):
	fmt = "%H:%M"
	start1, end1 = [datetime.strptime(t, fmt) for t in tw1]
	start2, end2 = [datetime.strptime(t, fmt) for t in tw2]

	latest_start = max(start1,start2)
	earliest_end = min(end1, end2)

	return latest_start < earliest_end #true if overlaps

def optimize_routes(request):
	orders = generate_mock_orders()
	# location in radians
	coords = np.array([[radians(o["location"]["lat"]), radians(o["location"]["lon"])] for o in orders])
	# apply DB scan with haversine metrics of 2km which is similar to 0.2 radian
	clustering = DBSCAN(eps = 0.02, min_samples = 1, metric='haversine').fit(coords)
	clusters = {}
	for label, order in zip(clustering.labels_, orders):
		clusters.setdefault(label, []).append(order)

	grouped = []
	agent_id = 1
	for group in clusters.values():
		grouped_order = []
		while group:
			seed = group.pop(0)
			batch = [seed]
			rest = []
			for other in group:
				if time_overlap(seed["time_window"], other["time_window"]):
					batch.append(other)
				else:
					rest.append(other)

			group = rest
			grouped.append({
				"agent_id": f"AGENT_{agent_id}",
				"orders": [o["order_id"] for o in batch]
			})
			agent_id += 1
	return JsonResponse(grouped, safe = False)
