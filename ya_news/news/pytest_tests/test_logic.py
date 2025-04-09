from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


BAD_WORDS_COMMENT = {'text': f'Текст {BAD_WORDS[0]} текст'}


def test_anonymous_user_cant_create_comment(client, new_comment, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=new_comment)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, new_comment, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    author_client.post(url, data=new_comment)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == new_comment['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    """Если комментарий содержит запрещённые слова, он не будет
    опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=BAD_WORDS_COMMENT)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(author_client, new_comment, news, comment):
    """Авторизованный пользователь может редактировать
    свои комментарии.
    """
    news_url = reverse('news:detail', args=(news.id,))
    comment_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(comment_url, data=new_comment)
    assertRedirects(response, news_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == new_comment['text']


def test_author_can_delete_comment(author_client, news, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    news_url = reverse('news:detail', args=(news.id,))
    comments_count = Comment.objects.count()
    comment_url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(comment_url)
    new_comments_count = Comment.objects.count()
    assertRedirects(response, news_url + '#comments')
    assert new_comments_count == comments_count - 1


def test_user_cant_edit_comment_of_another_user(admin_client, new_comment,
                                                comment):
    """Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    original_text = comment.text
    comment_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(comment_url, data=new_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_text


def test_user_cant_delete_comment_of_another_user(admin_client, new_comment,
                                                  comment):
    """Авторизованный пользователь не может редактировать
    или удалять чужие комментарии.
    """
    comment_url = reverse('news:delete', args=(comment.id,))
    response = admin_client.post(comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1
