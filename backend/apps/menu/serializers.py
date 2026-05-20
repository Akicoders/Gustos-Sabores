from rest_framework import serializers

from apps.menu.models import Category, Dish


class DishSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField(source="category.id", read_only=True)

    class Meta:
        model = Dish
        fields = ("id", "category", "category_id", "name", "slug", "description", "price", "is_available", "image_url")


class CategorySerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "dishes")
