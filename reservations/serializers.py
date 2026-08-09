from rest_framework import serializers
from menus.models import FoodItem
from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    food_item_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "daily_menu",
            "food_item",
            "food_item_id",
            "is_finalized",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "daily_menu",
            "food_item",
            "is_finalized",
            "updated_at",
        ]

    def validate_food_item_id(self, value):
        instance = self.instance
        if instance and not instance.daily_menu.items.filter(id=value).exists():
            raise serializers.ValidationError("این آیتم در منوی انتخابی موجود نیست.")
        return value

    def update(self, instance, validated_data):
        food_item_id = validated_data.pop("food_item_id", None)
        if food_item_id:
            instance.food_item = FoodItem.objects.get(id=food_item_id)
            instance.save()
        return instance
