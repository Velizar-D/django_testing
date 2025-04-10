from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .base_tests import BaseTestCase


class TestNoteLogic(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'test-logic-new-slug'
        }
        cls.update_data = {
            'title': 'Обновлённый заголовок',
            'text': 'Новый текст после редактирования',
            'slug': 'updated-slug-v2'
        }

    def test_authenticated_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку"""
        Note.objects.all().delete()
        initial_count = Note.objects.count()
        response = self.author_client.post(self.URL_ADD, data=self.form_data)
        self.assertRedirects(response, self.URL_SUCCESS)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку"""
        initial_count = Note.objects.count()
        response = self.client.post(self.URL_ADD, data=self.form_data)
        redirect_url = f'{self.URL_LOGIN}?next={self.URL_ADD}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_duplicate_slug_prevention(self):
        """Невозможно создать две заметки с одинаковым slug"""
        self.form_data['slug'] = self.note.slug
        initial_count = Note.objects.count()
        response = self.author_client.post(self.URL_ADD, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), initial_count)

    def test_auto_slug_generation(self):
        """Автоматическая генерация slug при его отсутствии"""
        Note.objects.all().delete()
        initial_count = Note.objects.count()
        form_data = self.form_data.copy()
        del form_data['slug']
        response = self.author_client.post(self.URL_ADD, data=form_data)
        self.assertRedirects(response, self.URL_SUCCESS)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.get()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свои заметки"""
        response = self.author_client.post(self.URL_EDIT,
                                           data=self.update_data)
        self.assertRedirects(response, self.URL_SUCCESS)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.update_data['title'])
        self.assertEqual(updated_note.text, self.update_data['text'])
        self.assertEqual(updated_note.slug, self.update_data['slug'])
        self.assertEqual(updated_note.author, self.author)

    def test_author_can_delete_note(self):
        """Автор может удалять свои заметки"""
        initial_count = Note.objects.count()
        response = self.author_client.post(self.URL_DELETE)
        self.assertRedirects(response, self.URL_SUCCESS)
        self.assertEqual(Note.objects.count(), initial_count - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки"""
        response = self.auth_user_client.post(
            self.URL_EDIT,
            data=self.update_data
            )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.note.title)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.slug, self.note.slug)

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки"""
        initial_count = Note.objects.count()
        response = self.auth_user_client.post(self.URL_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
