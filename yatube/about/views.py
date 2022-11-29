from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Возвращает статичную страницу на основе указанного шаблона."""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Возвращает статичную страницу на основе указанного шаблона."""

    template_name = 'about/tech.html'
