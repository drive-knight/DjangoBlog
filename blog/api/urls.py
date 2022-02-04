from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'blog'

router = routers.DefaultRouter()
router.register('courses', views.NewsViewSet)

urlpatterns = [
    path('news/', views.NewsListView.as_view(), name='subject_list'),
    path('news/<pk>/', views.NewsDetailView.as_view(), name='subject_detail'),
    path('', include(router.urls)),
]