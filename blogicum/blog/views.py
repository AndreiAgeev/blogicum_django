from typing import Any
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth import get_user_model

from .models import Post, Category
from .forms import UserEditForm


User = get_user_model()
POST_PER_PAGE = 5
join_parameters = ('location', 'author', 'category')


def get_posts_qs(posts, *joins, **filters):
    return posts.select_related(*joins).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        **filters
    )


def index(request):
    template_name = 'blog/index.html'
    posts = get_posts_qs(
        Post.objects,
        *join_parameters,
        **{'category__is_published': True}
    )[:POST_PER_PAGE]
    context = {'posts': posts}
    return render(request, template_name, context)


def post_detail(request, post_id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.exclude(
            Q(pub_date__gte=timezone.now())
            | Q(is_published=False)
            | Q(category__is_published=False)
        ),
        pk=post_id
    )
    context = {'post': post}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category_data = get_object_or_404(
        Category.objects.filter(
            is_published=True
        ),
        slug=category_slug)
    posts = get_posts_qs(
        Post.objects,
        *join_parameters,
        **{'category__slug': category_slug}
    )
    context = {
        'category': category_data,
        'posts': posts
    }
    return render(request, template_name, context)


def profile_page(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author_id=profile.id)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'page_obj': page_obj
    }
    print(request.user.id)
    return render(request, 'blog/profile.html', context)


class ProfileEditView(generic.UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return User.objects.get(pk=self.request.user.id)

    def get_success_url(self) -> str:
        return reverse('blog:profile', kwargs={'username': self.request.user.username})

def create_post(request):
    pass
