from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
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
        )

    def test_note_in_list_for_author(self):
        """
        Заметка автора присутствует в его списке заметок.
        Страницы создания и редактирования содержат формы.
        """
        users_statuses = (
            (self.author_client, True),
            (self.auth_user_client, False),
        )
        for user, note_in_list in users_statuses:
            with self.subTest():
                url = reverse('notes:list')
                response = user.get(url)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), note_in_list)

    def test_pages_contain_forms(self):
        """Страницы создания и редактирования содержат формы."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
