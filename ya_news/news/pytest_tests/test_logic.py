from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


BAD_WORDS_COMMENT = {'text': f'Текст {BAD_WORDS[0]} текст'}


def test_anonymous_user_cant_create_comment(client, new_comment, news,
                                            detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(detail_url, data=new_comment)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, new_comment, news,
                                 detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    author_client.post(detail_url, data=new_comment)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == new_comment['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, detail_url):
    """Если комментарий содержит запрещённые слова, он не будет
    опубликован, а форма вернёт ошибку.
    """
    response = author_client.post(detail_url, data=BAD_WORDS_COMMENT)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(author_client, new_comment, news, comment,
                                 detail_url, edit_comment_url):
    """Авторизованный пользователь может редактировать
    свои комментарии.
    """
    response = author_client.post(edit_comment_url, data=new_comment)
    assertRedirects(response, detail_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == new_comment['text']


def test_author_can_delete_comment(author_client, news, comment, detail_url,
                                   delete_comment_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_count = Comment.objects.count()
    response = author_client.post(delete_comment_url)
    new_comments_count = Comment.objects.count()
    assertRedirects(response, detail_url + '#comments')
    assert new_comments_count == comments_count - 1


def test_user_cant_edit_comment_of_another_user(admin_client, new_comment,
                                                comment, edit_comment_url):
    """Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    comment_id = comment.id
    response = admin_client.post(edit_comment_url, data=new_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=comment_id)
    assert updated_comment.text == comment.text


def test_user_cant_delete_comment_of_another_user(admin_client, new_comment,
                                                  comment, delete_comment_url):
    """Авторизованный пользователь не может редактировать
    или удалять чужие комментарии.
    """
    response = admin_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1
