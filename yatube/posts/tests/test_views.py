import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django import forms

from ..import constants
from ..models import Group, Post

from ..utils import uploaded_img

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_username')
        cls.group = Group.objects.create(
            title='test title',
            slug='1',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post',
            group=cls.group,
            image=uploaded_img
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Проверка шаблона при вызове views через пространство имен."""
        reverse_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/create_post.html',
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}):
            'posts/profile.html',
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}):
            'posts/group_list.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/post_detail.html',
        }
        for reverse_name, template in reverse_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_username')
        cls.group = Group.objects.create(
            title='test title',
            slug='1',
            description='test description',
        )
        cls.group_2 = Group.objects.create(
            title='test title2',
            slug='2',
            description='test description2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post',
            group=cls.group,
            image=uploaded_img,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.id, self.post.id)
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_group_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug':
                                                      self.group.slug}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.id, self.post.id)
        self.assertEqual(response.context['post'].image, self.post.image)
        self.assertEqual(response.context['group'].title, self.group.title)
        self.assertEqual(
            response.context['group'].description, self.group.description)
        self.assertEqual(response.context['group'].slug, self.group.slug)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username':
                                                      self.post.author.username
                                                      }))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id':
                                                      self.post.id}))
        first_object = response.context['post']
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.id, self.post.id)
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': f'{self.post.id}'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.ImageField
        }
        self.assertEqual(response.context['post'], self.post)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_appeared_on_the_wrong_groups_page(self):
        """Пост не сохраняется в другой группе."""
        group_2 = f'/group/{self.group_2.slug}/'
        response = self.authorized_client.get(group_2)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_post_appeared_on_the_groups_page(self):
        """Пост сохраняется в нужной группе."""
        group = f'/group/{self.group.slug}/'
        response = self.authorized_client.get(group)
        self.assertIn(self.post, response.context['page_obj'])

    def test_first_post_appeared_on_the_index_page(self):
        """Пост при создании попадает на 1ю позицию на главной странице."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = Post.objects.first()
        self.assertEqual(response.context['page_obj'][0],
                         first_post)

    def test_first_post_appeared_on_the_group_page(self):
        """Пост при создании попадает на 1ю позицию на странице группы."""
        group_page = f'/group/{self.group.slug}/'
        response = self.authorized_client.get(group_page)
        first_post = Post.objects.first()
        self.assertEqual(response.context['page_obj'][0],
                         first_post)

    def test_first_post_appeared_on_the_profile_page(self):
        """Пост при создании попадает на 1ю позицию на странице профиля."""
        profile_page = f'/profile/{self.user.username}/'
        response = self.authorized_client.get(profile_page)
        first_post = Post.objects.first()
        self.assertEqual(response.context['page_obj'][0],
                         first_post)

    def test_index_cache(self):
        """Главная страница кэшируется"""
        response_first = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(
            author=self.user,
            text='test post',
        )
        response_second = self.authorized_client.get(
            (reverse('posts:index'))
        )
        self.assertEqual(response_first.content,
                         response_second.content)
        cache.clear()
        response_after_clear = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(response_first.content,
                            response_after_clear.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_username')
        cls.group = Group.objects.create(
            title='test title',
            slug='1',
            description='test description',
        )
        cls.posts = [Post.objects.create(
            author=cls.user,
            text='test post',
            group=cls.group,
        )
            for i in range(constants.POSTS_PER_PAGE
                           + constants.POSTS_PER_SECOND_PAGE)]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_first_page_contains_ten_records(self):
        """Проверит количество постов на первой странице."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                            (constants.POSTS_PER_PAGE)
                         )

    def test_second_page_contains_three_records(self):
        """Проверит количество постов на второй странице."""
        response = self.authorized_client.get(reverse(
            'posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                            (constants.POSTS_PER_SECOND_PAGE)
                         )

    def test_group_page_contains_ten_records(self):
        """Проверит количество постов на странице группы."""
        group_page = f'/group/{self.group.slug}/'
        response = self.authorized_client.get(group_page)
        self.assertEqual(len(response.context['page_obj']),
                            (constants.POSTS_PER_PAGE)
                         )

    def test_second_group_page_contains_three_records(self):
        """Проверит количество постов на 2й странице группы."""
        group_page = f'/group/{self.group.slug}/'
        response = self.authorized_client.get((group_page) + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                            (constants.POSTS_PER_SECOND_PAGE)
                         )

    def test_profile_page_contains_ten_records(self):
        """Проверит количество постов на странице профиля."""
        profile_page = f'/profile/{self.user.username}/'
        response = self.authorized_client.get(profile_page)
        self.assertEqual(len(response.context['page_obj']),
                            (constants.POSTS_PER_PAGE),
                         )

    def test_second_profile_page_contains_three_records(self):
        """Проверит количество постов на 2й странице профиля."""
        profile_page = f'/profile/{self.user.username}/'
        response = self.authorized_client.get((profile_page) + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                            (constants.POSTS_PER_SECOND_PAGE),
                         )
