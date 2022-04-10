from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from django.urls import reverse
from autoslug import AutoSlugField
from uuslug import uuslug


def instance_slug(instance):
    return instance.title


def slugify_value(value):
    return value.replace(' ', '-')


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='опубликовано')


class Category(models.Model):
    title = models.CharField(max_length=150, db_index=True, verbose_name='Наименование категории')
    slug = models.SlugField(max_length=60, null=False, unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'category_id': self.pk})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']


class News(models.Model):
    STATUS_CHOICES = (
        ('черновик', 'Черновик'),
        ('опубликовано', 'Опубликовано'),
    )

    title = models.CharField(max_length=150, verbose_name='Название')
    slug = AutoSlugField(max_length=60, null=False, unique=True, verbose_name='URL', populate_from=instance_slug,
                         slugify=slugify_value)
    publish = models.DateTimeField(default=timezone.now)
    content = models.TextField(verbose_name='Контент')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name='Изображние', blank='True')
    status = models.CharField(max_length=13, choices=STATUS_CHOICES, verbose_name='Статус', default='Опубликовано')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория')
    objects = models.Manager()
    published_obj = PublishedManager()
    tags = TaggableManager()
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:view_news', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.slug, instance=self)
        return super(News, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at', 'title']


class Comment(models.Model):
    post = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=60, verbose_name='Имя')
    email = models.EmailField()
    body = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Комментарий {self.name} on {self.post}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class NewsIss(models.Model):
    id_iss = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    tag = models.CharField(max_length=12)
    title = models.TextField()
    published_at = models.CharField(max_length=30)
    modified_at = models.CharField(max_length=30)
    published_bd = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость московской биржи'
        verbose_name_plural = 'Новости московской биржи'
        ordering = ['-id_iss']
