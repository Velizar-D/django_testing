import pytest
from django.urls import reverse
from news.models import Comment
from news.forms import BAD_WORDS, WARNING
from http import HTTPStatus


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_detail_url, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(news_detail_url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(client_loggin, news_detail_url,
                                  news, author, form_data):
    """Авторизованный пользователь может отправить комментарий."""
    response = client_loggin.post(news_detail_url, data=form_data)
    assert response.status_code == 302
    assert response.url == f'{news_detail_url}#comments'
    assert Comment.objects.count() == 1
    comment = Comment.objects.first()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(client_loggin, news_detail_url):
    """Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    form_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = client_loggin.post(news_detail_url, data=form_data)
    assert response.status_code == 200
    form = response.context['form']
    assert form.errors['text'] == [WARNING]
    assert Comment.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize('url_name,method',
                         [('news:edit', 'post'), ('news:delete', 'delete')])
def test_user_can_edit_or_delete_own_comment(client_loggin,
                                               news,
                                               comment,
                                               url_name,
                                               method):
    """Авторизованный пользователь может редактировать
    и удалять свои комментарии.
    """
    url = reverse(url_name, args=(comment.id,))
    form_data = {'text': 'Обновленный текст комментария'}
    response = getattr(client_loggin, method)(url, data=form_data)
    assert response.status_code == 302
    assert response.url == reverse('news:detail',
                                   args=(news.id,)) + '#comments'
    if method == 'post':
        comment.refresh_from_db()
        assert comment.text == form_data['text']
    else:
        assert Comment.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_user_cant_edit_or_delete_comment_of_another_user(client,
                                                           comment,
                                                           auth_user,
                                                           url_name):
    """Авторизованный пользователь не может редактировать
    или удалять чужой комментарий.
    """
    client.force_login(auth_user)
    url = reverse(url_name, args=(comment.id,))
    form_data = {'text': 'Обновленный текст комментария'}
    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
