# from rest_framework import serializers
# from product.models import Service, Flowers, Establishment, Taxi
#
#
# # class ProductSerializer(serializers.ModelSerializer):
# #     """
# #     Сериализатор для списка услуг.
# #     """
# #     price = serializers.SerializerMethodField()
# #
# #     class Meta:
# #         model = Service
# #         fields = (
# #             "id", "name", "description", "photo", "discount", "dateFrom", "dateTo", "date_time", "comment", "is_active",
# #             "publish", "price"
# #         )
# #
# #     def get_price(self, obj):
# #         return obj.calculate_total_price()
#
# class FlowersSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Flowers
#         fields = '__all__'
#
#
# class EstablishmentSerializer(serializers.ModelSerializer):
#     dishes = serializers.StringRelatedField(many=True)
#
#     class Meta:
#         model = Establishment
#         fields = '__all__'
#
#
# class TaxiSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Taxi
#         fields = '__all__'
#
#
# class ServiceSerializer(serializers.ModelSerializer):
#     flowers = FlowersSerializer(many=True, read_only=True)
#     establishments = EstablishmentSerializer(many=True, read_only=True)
#     taxis = TaxiSerializer(many=True, read_only=True)
#     price = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Service
#         fields = '__all__'
#
#     def get_price(self, obj):
#         return obj.calculate_total_price()
