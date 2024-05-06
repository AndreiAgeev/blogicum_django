from typing import Any
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied 
from django.db.models import Q
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Post, Category, Comment
from .forms import UserEditForm, CreatePostForm, CommentForm


User = get_user_model()
join_parameters = ('location', 'author', 'category')


def get_posts_qs(posts, *joins, **filters):
    return posts.select_related(*joins).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        **filters
    )


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self) -> bool | None:
        object = self.get_object()
        return object.author == self.request.user
    
    # def get_login_url(self) -> str:
    #     string = self.request.build_absolute_uri().split('/')
    #     return ('/'.join(string[0:-2]) + '/')


def index(request):
    template_name = 'blog/index.html'
    posts = get_posts_qs(
        Post.objects,
        *join_parameters,
        **{'category__is_published': True}
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template_name, context)


def post_detail(request, post_id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(
            Post.objects.exclude(
                Q(pub_date__gte=timezone.now())
                | Q(is_published=False)
                | Q(category__is_published=False)
            ),
            pk=post_id
        )
    # if get_object_or_404(Post, pk=post_id).author == request.user:
    #     post = get_object_or_404(Post, pk=post_id)
    # else:
    #     post = get_object_or_404(
    #         Post.objects.exclude(
    #             Q(pub_date__gte=timezone.now())
    #             | Q(is_published=False)
    #             | Q(category__is_published=False)
    #         ),
    #         pk=post_id
    #     )
    context = {'post': post}
    context['form'] = CommentForm()
    context['comments'] = post.comment.select_related('author')
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
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category_data,
        'page_obj': page_obj
    }
    return render(request, template_name, context)


def profile_page(request, username):
    profile = get_object_or_404(User, username=username)
    if profile == request.user:
        posts = Post.objects.select_related(
            'location', 'author', 'category'
        ).filter(author=profile)
    else:
        posts = get_posts_qs(
            Post.objects,
            *join_parameters,
            **{'author': profile}
        )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'page_obj': page_obj
    }
    print(request.user.id)
    return render(request, 'blog/profile.html', context)


class ProfileEditView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return User.objects.get(pk=self.request.user.id)

    def get_success_url(self) -> str:
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class CreatePostView(LoginRequiredMixin, generic.CreateView):
    author = None
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class EditPostView(OnlyAuthorMixin, generic.UpdateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    redirect_field_name = None

    # def get_login_url(self) -> str:
    #     object = self.get_object()
    #     return reverse_lazy('blog:post_detail', args=[object.id])

    def handle_no_permission(self) -> HttpResponseRedirect:
        object = self.get_object()
        return redirect('blog:post_detail', post_id=object.id)



class DeletePostView(OnlyAuthorMixin, generic.DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'
    redirect_field_name = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.object.id)
        context['form'] = CreatePostForm(instance=instance)
        return context

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        post.comment_count = post.comment.count()
        post.save()
    return redirect('blog:post_detail', post_id=post_id)

def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        raise PermissionDenied

    form = CommentForm(request.POST or None, instance=comment)
    context = {'form': form, 'comment': comment}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', context)


def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    post = get_object_or_404(Post, pk=post_id)
    if comment.author != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        comment.delete()
        post.comment_count = post.comment.count()
        post.save()
        return redirect('blog:post_detail', post_id=post_id)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)
