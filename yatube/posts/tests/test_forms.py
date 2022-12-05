import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post
from ..utils import uploaded_img

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
        )
        cls.group_new = Group.objects.create(
            title='Тестовое название1',
            slug='slug2',
        )
        cls.small_gif = uploaded_img
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_authorized_client_post_create(self):
        """Публикация поста авторизованным пользователем."""
        cache.clear()
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
            'image': uploaded_img
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=(self.user.username,),))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.first()
        check_post_fields = (
            (post.author, self.post.author),
            (post.text, self.post.text),
            (post.group, self.post.group),
            (post.image, f'posts/{uploaded_img}'),
        )
        for new_post, expected in check_post_fields:
            with self.subTest(new_post=expected):
                self.assertEqual(new_post, expected)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_authorized_client_post_edit(self):
        """Изменение поста авторизованным пользователем."""
        cache.clear()
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test post edit post',
            'group': self.group_new.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        last_edit_post = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, reverse(
            'posts:post_edit',
            kwargs={'post_id': f'{self.post.id}'}))
        self.assertEqual(Post.objects.count(), posts_count)
        last_edit_post_data = ((last_edit_post.text, form_data.get('text')),
                               (last_edit_post.group.title,
                                self.group_new.title),
                               (last_edit_post.author, self.user))
        for value, expected in last_edit_post_data:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_guest_client_post_create(self):
        """Создание поста неавторизованным пользователем."""
        cache.clear()
        posts_count = Post.objects.count()
        response = self.client.post(
            reverse('posts:post_create'),
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/'))


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.form = PostForm
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_client_add_comment(self):
        """Публикация коммента авторизованным пользователем."""
        cache.clear()
        form_data = {
            'author': self.user,
            'post': self.post,
            'text': 'test text'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})
        )
