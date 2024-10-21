from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
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
        city_id = self.kwargs['city_id']
        return Establishment.objects.filter(city__id=city_id)