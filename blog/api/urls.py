from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'blog'

router = routers.DefaultRouter()
router.register('news', views.NewsViewSet)
router.register('user', views.UserViewSet)
router.register('category', views.CategoryViewSet)


urlpatterns = [
    path('', include(router.urls)),
]