from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post


User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user2 = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(
            title='test title',
            slug='1',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user2,
            text='test post',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_urls_uses_correct_template(self):
        """Проверит, что страницы используют правильные шаблоны."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            f'posts/{self.post.id}/comment/': 'posts/includes/comment.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client2.get(address)
                self.assertTemplateUsed(response, template)

    def test_index_page_not_login_user(self):
        """Главная страница доступна гостю."""
        index_page = '/'
        response = self.client.get(index_page)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_page_not_login_user(self):
        """Просмотр групп доступен гостю."""
        group_page = f'/group/{self.group.slug}/'
        response = self.client.get(group_page, args=[self.group.slug])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_page_not_login_user(self):
        """Просмотр чужого профиля доступен гостю."""
        profile_page = f'/profile/{self.user.username}/'
        response = self.client.get(profile_page, args=[self.user.username])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_page_not_login_user(self):
        """Просмотр чужого поста доступен гостю."""
        post_page = f'/posts/{self.post.id}/'
        response = self.client.get(post_page)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_authorized_client(self):
        """Создавать пост может только авторизованный пользователь."""
        create_post_page = '/create/'
        response = self.authorized_client.get(create_post_page)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_author(self):
        """Редактирование поста автором."""
        edit_post_page = f'/posts/{self.post.id}/edit/'
        response = self.authorized_client2.get(edit_post_page)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_not_author(self):
        """Редактирование поста не автором."""
        edit_post_page = f'/posts/{self.post.id}/edit/'
        response = self.authorized_client.get(edit_post_page)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_post_guest_redirect(self):
        """Редирект гостя при попытке создать пост."""
        create_post_page = '/create/'
        response = self.client.get(create_post_page)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_post_guest_redirect(self):
        """Редирект гостя при попытке редактировать пост."""
        edit_post_page = f'/posts/{self.post.id}/edit/'
        response = self.client.get(edit_post_page)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_non_exist_page(self):
        """Тест на ошибку 404"""
        unexisting_page = '/unexisting_page/'
        response = self.authorized_client.get(unexisting_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_post_url_redirect_anonymous_on_admin_login(self):
        """Страница для создания поста перенаправит анонимного
        пользователя на страницу логина.
        """
        create_post_page = '/create/'
        response = self.client.get(create_post_page)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/'))

    def test_edit_post_url_redirect_anonymous_on_admin_login(self):
        """Страница для редактирования поста перенаправит анонимного
        пользователя на страницу логина.
        """
        edit_post_page = f'/posts/{self.post.id}/edit/'
        response = self.client.get(edit_post_page)
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{self.post.id}/edit/'))

    def test_edit_post_url_redirect_not_author_on_post_detail_page(self):
        """Страница для редактирования поста перенаправит
        не автора на страницу поста.
        """
        edit_post_page = f'/posts/{self.post.id}/edit/'
        response = self.authorized_client.get(edit_post_page)
        self.assertRedirects(
            response, (f'/posts/{self.post.id}/'))

    def test_comment_post_url_redirect_author_on_post_detail_page(self):
        """Страница для комментирования поста перенаправит
        авторизованного пользователя на страницу поста.
        """
        comment_post_page = f'/posts/{self.post.id}/comment/'
        response = self.authorized_client.get(comment_post_page)
        self.assertRedirects(
            response, (f'/posts/{self.post.id}/'))
