from django.urls import path

from product.views import ServiceListView, ServiceDetailView, CityListViews

urlpatterns = [
    path('list-services/', ServiceListView.as_view(), name='list_services'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('list-city/', CityListViews.as_view(), name='list-city'),
]
