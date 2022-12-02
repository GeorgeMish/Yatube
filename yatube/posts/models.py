from django.db import models
from django.contrib.auth import get_user_model

from . import constants

User = get_user_model()


class Post(models.Model):
    """Создание модели Post."""

    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts')
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-pub_date',)

    def __str__(self):
        """Строковое представление объекта."""
        return self.text[:constants.SYMBOLS_IN_SELF_TEXT]


class Group(models.Model):
    """Создание модели Group."""

    title = models.CharField(
        'Заголовок',
        max_length=200,
        help_text='Заголовок группы.'
    )
    slug = models.SlugField(
        'URL',
        max_length=200,
        unique=True,
        help_text='Уникальный фрагмент адреса.'
    )
    description = models.TextField('Содержание')

    def __str__(self):
        """Возвращает название группы."""
        return self.title


class Comment(models.Model):
    """Создание модели Comment."""

    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Имя автора'
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self):
        """Строковое представление объекта."""
        return self.text[:constants.SYMBOLS_IN_SELF_TEXT]


class Follow(models.Model):
    """Создание модели Follow"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчикии'

    def __str__(self):
        """Строковое представление объекта."""
        return self.text[:constants.SYMBOLS_IN_SELF_TEXT]
