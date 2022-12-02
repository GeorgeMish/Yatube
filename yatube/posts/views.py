from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, User
from .forms import PostForm, CommentForm
from .utils import get_page_context
from . import constants


@cache_page(constants.CASH_TIME_FOR_INDEX_PAGE_IN_SECONDS)
def index(request):
    """Выводит шаблон главной страницы."""
    post_list = Post.objects.select_related('author', 'group')
    page_obj = get_page_context(post_list, request)
    context = {
        'page_obj': page_obj,
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Выводит шаблон с постами группы."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').all()
    page_obj = get_page_context(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Выводит страницу профиля пользователя."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = get_page_context(post_list, request)
    context = {
        'author': author,
        'page_obj': page_obj,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Выводит страницу отдельно взятого поста."""
    post_object = get_object_or_404(Post.objects.select_related(
        'group', 'author'), id=post_id)
    comments = post_object.comments.all()
    count = post_object.author.posts.count()
    form = CommentForm(request.POST or None)
    context = {
        'post': post_object,
        'comments': comments,
        'form': form,
        'count': count
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Возможность создать новый пост для авторизованного пользователя."""
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:profile', request.user.username)

    context = {
        'form': form
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Возможность редактировать пост для авторизованного пользователя."""
    post_object = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post_object)
    if post_object.author != request.user:
        return redirect('posts:post_detail', post_id)

    if request.method == 'POST' and form.is_valid():
        form.save()
        if post_object.author == request.user:
            return redirect('posts:post_edit', post_id)
        form = PostForm(instance=post_object)

    context = {
        'form': form,
        'True': True,
        'post': post_object
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Возможность оставлять комментарии для авторизованного пользователя."""
    post_object = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post_object
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post': post_object
    }
    return render(request, 'posts/create_post.html', context)