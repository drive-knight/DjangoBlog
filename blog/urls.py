from django.urls import path
from .views import *


app_name = 'blog'

urlpatterns = [
    path('mail/', test_email, name='mail'),
    path('search/', post_search, name='post_search'),
    path('iss-news/', get_iss, name='iss'),
    path('',  HomeNews.as_view(), name='home'),
    path('add-news/', CreateNews.as_view(), name='add_news'),
    path('category/<int:category_id>/', NewsByCategory.as_view(), name='category'),
    path('<slug:slug>/', ViewNews.as_view(), name='view_news'),

]