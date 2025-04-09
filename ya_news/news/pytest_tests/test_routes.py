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


@pytest.mark.parametrize(
    'url, client_fixture, expected_status',
    [
        (HOME_URL, lazy_fixture('client'), HTTPStatus.OK),
        (LOGIN_URL, lazy_fixture('client'), HTTPStatus.OK),
        (LOGOUT_URL, lazy_fixture('client'), HTTPStatus.OK),
        (SIGNUP_URL, lazy_fixture('client'), HTTPStatus.OK),
        (DETAIL_URL, lazy_fixture('client'), HTTPStatus.OK),
        (EDIT_COMMENT_URL, lazy_fixture('author_client'), HTTPStatus.OK),
        (DELETE_COMMENT_URL, lazy_fixture('author_client'), HTTPStatus.OK),
        (EDIT_COMMENT_URL, lazy_fixture('admin_client'),
         HTTPStatus.NOT_FOUND),
        (DELETE_COMMENT_URL, lazy_fixture('admin_client'),
         HTTPStatus.NOT_FOUND),
    ],
)
def test_url_accessibility(url, client_fixture, expected_status, login_url):
    """Проверка доступности страниц."""
    response = client_fixture.get(url)
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.FOUND:
        expected_redirect = f'{login_url}?next={url}'
        assert response.headers['Location'] == expected_redirect


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
