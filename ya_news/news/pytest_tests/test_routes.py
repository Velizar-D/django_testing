from http import HTTPStatus
from django.urls import reverse
import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup'),
)
def test_pages_availability(client, name):
    """
    Проверяет доступность главной страницы, входа,
    выхода и регистрации для анонимных пользователей.
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_page_available_for_anonymous_user(client, news):
    """
    Проверяет доступность страницы отдельной новости
    для анонимных пользователей.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(client,
                                                  author,
                                                  auth_user, comment, name):
    """
    Доступность страниц удаления и редактирования комментария для автора.
    И невозможность доступа к этим страницам для других пользователей.
    """
    users_statuses = (
        (author, HTTPStatus.OK),
        (auth_user, HTTPStatus.NOT_FOUND),
    )
    for user, status in users_statuses:
        client.force_login(user)
        url = reverse(name, args=(comment.id,))
        response = client.get(url)
        assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, comment, name):
    """
    Редирект анонимного пользователя на страницу авторизации
    при попытке перейти на страницу редактирования или удаления коммента.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url
