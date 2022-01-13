from django.contrib.sitemaps import Sitemap
from .models import News

class NewsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return News.published.all()

    def lastmod(self, obj):
        return obj.updated