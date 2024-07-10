from rest_framework import serializers
from product.models import Service


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка услуг.
    """
    price = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            "id", "name", "description", "photo", "discount", "dateFrom", "dateTo", "date_time", "comment", "is_active",
            "publish", "price"
        )

    def get_price(self, obj):
        return obj.calculate_total_price()
