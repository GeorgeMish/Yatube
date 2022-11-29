from datetime import datetime


def year(request):
    """Добавляет в контекст шаблона страницы переменную year."""
    current_year = datetime.now().year

    return {'year': current_year}
