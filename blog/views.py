from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from .models import News, Category
from .forms import NewsForm, UserRegisterForm, UserLoginForm, ContactForm

from django.core.mail import send_mail

'''
settings.DEBUG == True

def bad_request(request):
    raise SuspiciousOperation
    
def server_error(request):
    return render(request, 'news/500.html', status=500)   
       
def permission_denied(request, exception):
    return render(request, 'news/403.html', status=403)
    
def page_not_found(request, exception):
    return render(
        request,
        'news/404.html',
        {'path': request.path},
        status=404
    )
'''


def test_email(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            mail = send_mail(form.cleaned_data['subject'], form.cleaned_data['content'], 'rok5a@yandex.ru', ['mr.satanaa@gmail.com'], fail_silently=False)
            if mail:
                messages.success(request, 'Письмо отправлено')
                return redirect('test')
            else:
                messages.error(request, 'Ошибка отправки')
    else:
        form = ContactForm()
    return render(request, 'blog/test.html', {"form": form})


class HomeNews(ListView):
    model = News
    template_name = 'blog/home_news_list.html'
    context_object_name = 'news'
    paginate_by = 5

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super(HomeNews, self).get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context

    def get_queryset(self):
        return News.objects.filter(is_published=True).select_related('category')


class ViewNews(DetailView):
    model = News
    context_object_name = 'news_item'
    template_name = 'blog/news_detail.html'


class CreateNews(LoginRequiredMixin, CreateView):
    form_class = NewsForm
    template_name = 'blog/add_news.html'
    success_url = reverse_lazy('home')
    login_url = '/admin/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateNews, self).form_valid(form)


def get_category(request, category_id):
    news = News.objects.filter(category_id=category_id)
    category = Category.objects.get(pk=category_id)
    return render(request, template_name='blog/category.html', context={'news': news, 'category': category})


class NewsByCategory(ListView):
    model = News
    template_name = 'blog/home_news_list.html'
    context_object_name = 'news'
    allow_empty = False
    paginate_by = 2

    def get_queryset(self):
        return News.objects.filter(category_id=self.kwargs['category_id'], is_published=True).select_related('category')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(NewsByCategory, self).get_context_data(**kwargs)
        context['title'] = Category.objects.get(pk=self.kwargs['category_id'])
        return context