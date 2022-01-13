from django.contrib.sitemaps import Sitemap
from .models import News


class NewsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return News.published_obj.all()

    def lastmod(self, item):
        return item.updated_at