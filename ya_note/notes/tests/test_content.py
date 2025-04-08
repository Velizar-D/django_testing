from django.urls import reverse
from .base_tests import BaseTestCase


class TestContent(BaseTestCase):
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
            (self.URL_ADD, None),
            (self.URL_EDIT, None),
        )
        for url_name, args in urls:
            with self.subTest(name=url_name):
                url = url_name if args is None else url_name
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
