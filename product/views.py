from django.utils import timezone
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from product.models import Service, City, Establishment
from product.serializers import ServiceListSerializer, ServiceSerializer, CitySerializer, EstablishmentSerializer


@extend_schema_view(get=extend_schema(tags=["Услуги: список услуг"]))
class ServiceListView(ListAPIView):
    """
    Представление для отображения списка услуг.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.query_params.get('sort', None)  # Получаем параметр сортировки

        if sort_by:
            queryset = queryset.order_by(sort_by)

        return queryset


@extend_schema_view(get=extend_schema(tags=["Услуги: детальная информация об услуге"]))
class ServiceDetailView(RetrieveAPIView):
    """
    Представление для получения деталей услуги и связанных с ней объектов.
    """
    queryset = Service.objects.all().select_related('photo').prefetch_related(
        'flowers', 'establishments', 'establishments__dishes', 'taxis'
    )
    serializer_class = ServiceSerializer
    lookup_field = 'pk'


@extend_schema_view(get=extend_schema(tags=["Услуги: список городов для фильтрации заведений"]))
class CityListViews(ListAPIView):
    """
    Представление для отображения списка городов.
    """
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.query_params.get('sort', None)  # Получаем параметр сортировки

        if sort_by:
            queryset = queryset.order_by(sort_by)

        return queryset


class EstablishmentListAPIView(ListAPIView):
    serializer_class = EstablishmentSerializer

    def get_queryset(self):
        # Начинаем с общего queryset всех активных заведений
        queryset = Establishment.objects.filter(is_active=True)

        # Фильтрация по городу (если city_id передан в запросе)
        city_id = self.request.query_params.get('city_id')
        if city_id:
            queryset = queryset.filter(city_id=city_id)

        # Фильтрация по типу услуги (service_id)
        service_id = self.request.query_params.get('service_id')
        if service_id:
            queryset = queryset.filter(service_id=service_id)

        # Фильтрация по дате (если добавлены соответствующие поля в модель)
        date = self.kwargs.get('date')
        if date:
            queryset = queryset.filter(start_date__gte=date)

        end_date = self.kwargs.get('end_date')
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)

        return queryset

