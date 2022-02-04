from rest_framework import serializers
from ..models import News, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title']


class NewsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = News
        fields = ['id', 'title', 'slug', 'created_at', 'updated_at', 'category']

