from rest_framework import serializers
from .models import FoodItem, DailyMenu


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ["id", "name", "price"]


class DailyMenuSerializer(serializers.ModelSerializer):
    items = FoodItemSerializer(many=True, read_only=True)
    item_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=FoodItem.objects.all(), source="items"
    )

    class Meta:
        model = DailyMenu
        fields = ["id", "date", "items", "item_ids"]

    def create(self, validated_data):
        items = validated_data.pop("items", [])
        menu = DailyMenu.objects.create(**validated_data)
        menu.items.set(items)
        return menu

    def update(self, instance, validated_data):
        items = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items is not None:
            instance.items.set(items)
        return instance
