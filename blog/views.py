import copy

from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from django.contrib.postgres.search import SearchVector
from .models import News, Category, NewsIss
from .forms import NewsForm, ContactForm, CommentForm, SearchForm
from django.core.mail import send_mail
import requests
import datetime
from django.core.paginator import Paginator


'''def get_iss(request):
    r = requests.get('http://iss.moex.com/iss/sitenews')
    r_status = r.status_code
    if r_status == 200:
        r = requests.get('http://iss.moex.com/iss/sitenews.json')
        data = r.json()
        yesterday = datetime.date.today() - datetime.timedelta(days=5)
        for d in data['sitenews']['data']:
            if d[3] >= yesterday.strftime('%Y-%m-%d %H:%M:%S'):  # need additional verification api moex lags sometime
                NewsIss.objects.update_or_create(
                    id_iss=d[0],
                    tag=d[1],
                    title=d[2],
                    published_at=d[3],
                    modified_at=d[4],
                )
    else:
        return render(request, 'news/500.html', status=500)
    return redirect('blog:home')'''


def get_iss(request):
    r = requests.get('http://iss.moex.com/iss/sitenews')
    r_status = r.status_code
    context_data = dict()
    if r_status == 200:
        r = requests.get('http://iss.moex.com/iss/sitenews.json')
        data = r.json()
        context_data = copy.deepcopy(data)
        paginator = Paginator(context_data['sitenews']['data'], 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        return render(request, 'news/500.html', status=500)
    return render(request, 'blog/iss.html', {'page_obj': page_obj})


def test_email(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            mail = send_mail(form.cleaned_data['subject'],
                             form.cleaned_data['content'],
                             'rok5a@yandex.ru',
                             ['mr.satanaa@gmail.com'],
                             fail_silently=False)
            if mail:
                messages.success(request, 'Письмо отправлено')
                return redirect('test')
            else:
                messages.error(request, 'Ошибка отправки')
    else:
        form = ContactForm()
    return render(request, 'blog/test.html', {"form": form})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['query']
        results = News.objects.annotate(search=SearchVector('title', 'content')).filter(search=query)
    return render(request, 'blog/search.html', {'form': form,
                                                'query': query,
                                                'results': results})


class HomeNews(ListView):
    model = News, NewsIss
    template_name = 'blog/home_news_list.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super(HomeNews, self).get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        from django.core.paginator import Paginator
        p = Paginator(NewsIss.objects.all().select_related('category'), self.paginate_by)
        context['newsiss'] = p.page(context['page_obj'].number)
        return context

    def get_queryset(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        if (NewsIss.objects.all().exists() is False) or now - NewsIss.objects.all().last().published_bd > datetime.timedelta(
                hours=1):
            get_iss(self.request)
        return News.objects.filter(is_published=True).select_related('category')


class ViewNews(FormMixin, DetailView):
    form_class = CommentForm
    model = News
    context_object_name = 'news_item'
    template_name = 'blog/news_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ViewNews, self).get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('blog:view_news', kwargs={'slug': self.get_object().slug})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.post = self.get_object()
        self.object.email = self.request.user
        self.object.name = form.cleaned_data['name']
        self.object.save()
        return super().form_valid(form)


class CreateNews(LoginRequiredMixin, CreateView):
    form_class = NewsForm
    template_name = 'blog/add_news.html'
    success_url = reverse_lazy('blog:home')
    login_url = '/admin/'

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            form = NewsForm(request.POST, request.FILES)
            if form.is_valid():
                self.object = form.save(commit=False)
                self.object.photo = form.cleaned_data['photo']
                self.object.slug = form.cleaned_data['slug']
                self.object.is_published = form.cleaned_data['is_published']
                self.object.save()
                return super().form_valid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateNews, self).form_valid(form)


def get_category(request, category_id):
    news = News.objects.filter(category_id=category_id)
    category = Category.objects.get(pk=category_id)
    return render(request, template_name='blog/category.html', context={'news': news, 'category': category})


class NewsByCategory(ListView):
    model = News
    template_name = 'blog/news_list.html'
    context_object_name = 'news'
    allow_empty = True
    paginate_by = 10

    def get_queryset(self):
        return News.objects.filter(category_id=self.kwargs['category_id']).select_related('category') \
               or NewsIss.objects.filter(category_id=self.kwargs['category_id']).select_related('category')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(NewsByCategory, self).get_context_data(**kwargs)
        context['title'] = Category.objects.get(pk=self.kwargs['category_id'])
        return context
