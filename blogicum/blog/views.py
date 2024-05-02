from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from blog.models import Post, Category


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
