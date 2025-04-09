from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.auth_user = User.objects.create(username='auth_user')
        cls.auth_user_client = Client()
        cls.auth_user_client.force_login(cls.auth_user)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='test-slug'
        )

        cls.URL_HOME = reverse('notes:home')
        cls.URL_SIGNUP = reverse('users:signup')
        cls.URL_LOGIN = reverse('users:login')
        cls.URL_LOGOUT = reverse('users:logout')
        cls.URL_LIST = reverse('notes:list')
        cls.URL_SUCCESS = reverse('notes:success')
        cls.URL_ADD = reverse('notes:add')
        cls.URL_DETAIL = reverse('notes:detail', args=(cls.note.slug,))
        cls.URL_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.URL_DELETE = reverse('notes:delete', args=(cls.note.slug,))
