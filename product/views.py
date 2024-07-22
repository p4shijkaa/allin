from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from product.models import Service
from product.serializers import ServiceListSerializer, ServiceSerializer


@extend_schema_view(get=extend_schema(tags=["Услуги: список услуг"]))
class ServiceListView(ListAPIView):
    """
    Представление для отображения списка услуг
    """
    queryset = Service.objects.all()
    serializer_class = ServiceListSerializer


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

