from rest_framework import serializers
from product.models import Service, Flowers, Establishment, Taxi, Image, Dish, Review, Decoration, City


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['src', 'alt']
        read_only_fields = ['src', 'alt']


class FlowersSerializer(serializers.ModelSerializer):
    photo = ImageSerializer()

    class Meta:
        model = Flowers
        fields = ['id', 'name', 'description', 'photo', 'count', 'price', 'comment']
        read_only_fields = ['name', 'description', 'photo', 'count', 'price']


class EstablishmentSerializer(serializers.ModelSerializer):
    photo = ImageSerializer()

    class Meta:
        model = Establishment
        fields = ['id', 'name', 'description', 'photo', 'address', 'comment']
        read_only_fields = ['name', 'description', 'photo', 'address']


class DishSerializer(serializers.ModelSerializer):
    photo = ImageSerializer()
    establishment = EstablishmentSerializer()

    class Meta:
        model = Dish
        fields = ['id', 'establishment', 'name', 'description', 'photo', 'count', 'price', 'comment']
        read_only_fields = ['name', 'description', 'photo']


class TaxiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxi
        fields = ['id', 'boarding_address', 'dropoff_address', 'date_time', 'price', 'comment']


class DecorationSerializer(serializers.ModelSerializer):
    photo = ImageSerializer()

    class Meta:
        model = Decoration
        fields = ['id', 'name', 'description', 'photo', 'price', 'comment']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'author', 'text', 'rating', 'data', 'service']
        read_only_fields = ['author', 'data']


class ServiceSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка услуг.
    """
    photo = ImageSerializer()
    flowers = FlowersSerializer(many=True)
    establishments = EstablishmentSerializer(many=True, read_only=True)
    taxis = TaxiSerializer(many=True)
    decorations = DecorationSerializer(many=True)
    # price = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'photo', 'discount', 'dateFrom', 'dateTo', 'comment', 'flowers',
                  'establishments', 'taxis', 'decorations']   # 'price'

    # def get_price(self, obj):
    #     return obj.calculate_total_price()


class ServiceListSerializer(serializers.ModelSerializer):
    photo = ImageSerializer()

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'photo', 'discount', 'dateFrom', 'dateTo', 'comment']
        read_only_fields = ['name', 'description', 'photo', 'discount', 'dateFrom', 'dateTo']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']
        read_only_fields = ['name', ]
