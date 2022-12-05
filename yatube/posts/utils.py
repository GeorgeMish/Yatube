from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator

from . import constants


def get_page_context(post_list, request):
    """Пагинация для шаблонов страниц."""
    paginator = Paginator(post_list, constants.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
uploaded_img = SimpleUploadedFile(
    name='small.gif',
    content=small_gif,
    content_type='image/gif'
)
