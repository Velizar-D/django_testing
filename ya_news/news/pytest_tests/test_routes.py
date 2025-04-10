from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


HOME_URL = lazy_fixture('home_url')
LOGIN_URL = lazy_fixture('login_url')
LOGOUT_URL = lazy_fixture('logout_url')
SIGNUP_URL = lazy_fixture('signup_url')
DETAIL_URL = lazy_fixture('detail_url')
EDIT_COMMENT_URL = lazy_fixture('edit_comment_url')
DELETE_COMMENT_URL = lazy_fixture('delete_comment_url')

CLIENT_FIXTURE = lazy_fixture('client')
AUTHOR_CLIENT_FIXTURE = lazy_fixture('author_client')
NOT_AUTHOR_FIXTURE = lazy_fixture('not_author_client')


@pytest.mark.parametrize(
    'url, client_fixture, expected_status',
    [
        (HOME_URL, CLIENT_FIXTURE, HTTPStatus.OK),
        (LOGIN_URL, CLIENT_FIXTURE, HTTPStatus.OK),
        (LOGOUT_URL, CLIENT_FIXTURE, HTTPStatus.OK),
        (SIGNUP_URL, CLIENT_FIXTURE, HTTPStatus.OK),
        (DETAIL_URL, CLIENT_FIXTURE, HTTPStatus.OK),
        (EDIT_COMMENT_URL, AUTHOR_CLIENT_FIXTURE, HTTPStatus.OK),
        (DELETE_COMMENT_URL, AUTHOR_CLIENT_FIXTURE, HTTPStatus.OK),
        (EDIT_COMMENT_URL, NOT_AUTHOR_FIXTURE, HTTPStatus.NOT_FOUND),
        (DELETE_COMMENT_URL, NOT_AUTHOR_FIXTURE, HTTPStatus.NOT_FOUND),
    ],
)
def test_url_accessibility(url, client_fixture, expected_status, login_url):
    """Проверка доступности страниц."""
    response = client_fixture.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (EDIT_COMMENT_URL, DELETE_COMMENT_URL),
)
def test_redirect_for_anonymous_client(client, url, login_url):
    """При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
