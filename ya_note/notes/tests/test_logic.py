from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.auth_user = User.objects.create(username='auth_user')
        cls.auth_user_client = Client()
        cls.auth_user_client.force_login(cls.auth_user)
        cls.data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_authenticated_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку"""
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку"""
        url = reverse('notes:add')
        response = self.client.post(url, data=self.data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_duplicate_slug_prevention(self):
        """Невозможно создать две заметки с одинаковым slug"""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:add')
        response = self.author_client.post(url, data={
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': self.note.slug
        })
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_auto_slug_generation(self):
        """Автоматическая генерация slug при его отсутствии"""
        url = reverse('notes:add')
        self.data.pop('slug')
        response = self.author_client.post(url, data=self.data)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get()
        expected_slug = slugify(self.data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_delete_note(self):
        """Автор может редактировать и удалять свои заметки"""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.data['title'])
        self.assertEqual(self.note.text, self.data['text'])
        self.assertEqual(self.note.slug, self.data['slug'])

        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_edit_delete_note(self):
        """Пользователь не может удалять и редактировать чужие заметки"""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_user_client.post(url, self.data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.data['title'])
        self.assertNotEqual(self.note.text, self.data['text'])
        self.assertNotEqual(self.note.slug, self.data['slug'])

        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
