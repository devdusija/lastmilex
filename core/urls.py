from django.urls import path
from .views import generate_mock_orders, optimize_routes

urlpatterns = [
    path('api/orders/', generate_mock_orders, name='mock-orders'),
	path('api/optimize_routes', optimize_routes, name='optimize_routes')
]
