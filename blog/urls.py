from django.urls import path
#from django.conf.urls import handler403, handler404, handler500

from .views import *

'''
handler403 = 'news.views.permission_denied'
handler404 = 'news.views.page_not_found'
handler500 = 'news.views.server_error'
'''

app_name = 'blog'

urlpatterns = [
    path('test/', test_email, name='test'),
    path('', HomeNews.as_view(), name='home'),
    path('category/<int:category_id>/', NewsByCategory.as_view(), name='category'),
    path('<slug:slug>', ViewNews.as_view(), name='view_news'),
    path('add-news/', CreateNews.as_view(), name='add_news'),
]