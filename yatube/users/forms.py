from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """Форма для создания формы для работы с моделью User."""

    class Meta(UserCreationForm.Meta):

        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
