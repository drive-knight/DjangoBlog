from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from django.urls import reverse
from django.template.defaultfilters import slugify


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='опубликовано')


class News(models.Model):
    STATUS_CHOICES = (
        ('черновик', 'Черновик'),
        ('опубликовано', 'Опубликовано'),
    )

    title = models.CharField(max_length=150, verbose_name='Название')
    slug = models.SlugField(max_length=250, null=False, unique=True, verbose_name='URL')
    publish = models.DateTimeField(default=timezone.now)
    content = models.TextField(verbose_name='Контент')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name='Фото', blank='True')
    status = models.CharField(max_length=13, choices=STATUS_CHOICES, verbose_name='Статус', default='Опубликовано')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория')
    objects = models.Manager()
    published_obj = PublishedManager()
    tags = TaggableManager()
    views = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('blog:view_news', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super(News, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at', 'title']


class Category(models.Model):
    title = models.CharField(max_length=150, db_index=True, verbose_name='Наименование категории')

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'category_id': self.pk})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']


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

