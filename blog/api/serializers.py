from rest_framework import serializers
from ..models import News, Category
from users.models import CustomUser


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['url', 'title']


class NewsSerializer(serializers.HyperlinkedModelSerializer):
    category = CategorySerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='blog:view_news',
        lookup_field='slug'
    )

    class Meta:
        model = News
        fields = ['url', 'id', 'title', 'slug', 'created_at', 'updated_at', 'category']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'is_staff', 'is_active', 'is_superuser']

