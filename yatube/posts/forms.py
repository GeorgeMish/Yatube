from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    """Форма Post для создания формы для работы с моделью User."""

    class Meta:

        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(ModelForm):
    """Форма Comment для создания формы для работы с моделью User"""
    class Meta:

        model = Comment
        fields = ('text',)
