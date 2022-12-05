from django.contrib.auth import get_user_model
from django.test import TestCase

from .. import constants
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test title',
            slug=' test slug',
            description=' test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post'[:constants.SYMBOLS_IN_SELF_TEXT]
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        str_names = {
            self.post.text: 'test post',
            self.group.title: 'test title',
        }
        for model_type, expected_str in str_names.items():
            with self.subTest():
                self.assertEqual(str(model_type), expected_str)
