
from django.http import JsonResponse
import random
from geopy.distance import geodesic
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

def optimize_routes(request):
	orders = generate_mock_orders()
	unassigned = orders[:]
	groups = []
	agent_counter = 1
	while unassigned:
		seed = unassigned.pop(0)
		group = [seed]
		remaining = []
		for orders in unassigned:
			dist = geodesic(
				(seed['location']['lat'], seed['location']['lon']),
				(orders['location']['lat'], orders['location']['lon'])
			).km

			if dist <= 2.0:
				group.append(orders)
			else:
				remaining.append(orders)

		groups.append({
			"agent_id": f"AGENT_{agent_counter}",
			"orders": [o["order_id"] for o in group]
		})
		agent_counter += 1
		unassigned = remaining
	return JsonResponse(groups, safe=False)

