from http import HTTPStatus

from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from .base_tests import BaseTestCase
from notes.forms import WARNING


class TestNoteLogic(BaseTestCase):
    def setUp(self):
        Note.objects.all().delete()
        self.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        self.existing_note = Note.objects.create(
            title='Существующая заметка',
            text='Текст существующей заметки',
            author=self.author,
            slug='unique-slug'
        )

    def test_authenticated_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку"""
        initial_count = Note.objects.count()
        response = self.author_client.post(self.URL_ADD, data=self.form_data)
        self.assertRedirects(response, self.URL_SUCCESS)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        note = Note.objects.get(slug=self.form_data['slug'])
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
        initial_count = Note.objects.count()
        response = self.author_client.post(
            self.URL_ADD,
            data={
                'title': 'Новый заголовок',
                'text': 'Новый текст',
                'slug': self.existing_note.slug
            }
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.existing_note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), initial_count)

    def test_auto_slug_generation(self):
        """Автоматическая генерация slug при его отсутствии"""
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
        }
        response = self.author_client.post(self.URL_ADD, data=form_data)
        self.assertRedirects(response, self.URL_SUCCESS)
        initial_count = Note.objects.count()
        new_note = Note.objects.exclude(slug=self.existing_note.slug).get()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_author_can_edit_note(self):
        """Автор может редактировать свои заметки"""
        note_to_edit = Note.objects.create(
            title='Исходный заголовок',
            text='Исходный текст',
            author=self.author,
            slug='original-slug'
        )
        update_data = {
            'title': 'Обновленный заголовок',
            'text': 'Новый текст',
            'slug': 'updated-slug'
        }

        edit_url = reverse('notes:edit', args=(note_to_edit.slug,))
        response = self.author_client.post(edit_url, data=update_data)

        self.assertRedirects(response, self.URL_SUCCESS)

        updated_note = Note.objects.get(id=note_to_edit.id)

        self.assertEqual(updated_note.title, update_data['title'])
        self.assertEqual(updated_note.text, update_data['text'])
        self.assertEqual(updated_note.slug, update_data['slug'])
        self.assertEqual(updated_note.author, self.author)

    def test_author_can_delete_note(self):
        """Автор может удалять свои заметки"""
        note_to_delete = Note.objects.create(
            title='Заголовок для удаления',
            text='Текст для удаления',
            author=self.author,
            slug='delete-slug'
        )
        initial_count = Note.objects.count()

        delete_url = reverse('notes:delete', args=(note_to_delete.slug,))
        response = self.author_client.post(delete_url)
        self.assertRedirects(response, self.URL_SUCCESS)

        self.assertEqual(Note.objects.count(), initial_count - 1)
        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(slug='delete-slug')

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки"""
        unique_slug = 'super_unique_slug'
        note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=self.author,
            slug=unique_slug
        )
        update_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        edit_url = reverse('notes:edit', args=(note.slug,))
        response = self.auth_user_client.post(edit_url, data=update_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        updated_note = Note.objects.get(slug=unique_slug)
        self.assertEqual(updated_note.title, 'Тестовая заметка')
        self.assertEqual(updated_note.slug, unique_slug)
        self.assertEqual(updated_note.text, 'Текст заметки')

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки"""
        note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=self.author,
            slug='test-note'
        )
        initial_count = Note.objects.count()
        delete_url = reverse('notes:delete', args=(note.slug,))
        response = self.auth_user_client.post(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertTrue(Note.objects.filter(slug='test-note').exists())
