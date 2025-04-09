from http import HTTPStatus

from .base_tests import BaseTestCase


class TestRoutes(BaseTestCase):

    def test_pages_status_codes(self):
        """Проверка статус-кодов для разных URL и клиентов."""
        test_cases = [
            (self.URL_HOME, self.client, HTTPStatus.OK),
            (self.URL_SIGNUP, self.client, HTTPStatus.OK),
            (self.URL_LOGIN, self.client, HTTPStatus.OK),
            (self.URL_LOGOUT, self.client, HTTPStatus.OK),

            (self.URL_LIST, self.author_client, HTTPStatus.OK),
            (self.URL_SUCCESS, self.author_client, HTTPStatus.OK),
            (self.URL_ADD, self.author_client, HTTPStatus.OK),
            (self.URL_DETAIL, self.author_client, HTTPStatus.OK),
            (self.URL_EDIT, self.author_client, HTTPStatus.OK),
            (self.URL_DELETE, self.author_client, HTTPStatus.OK),

            (self.URL_DETAIL, self.auth_user_client, HTTPStatus.NOT_FOUND),
            (self.URL_EDIT, self.auth_user_client, HTTPStatus.NOT_FOUND),
            (self.URL_DELETE, self.auth_user_client, HTTPStatus.NOT_FOUND),
        ]

        for url, client, expected_status in test_cases:
            with self.subTest(url=url, client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        """
        Анонимный пользователь перенаправляется на страницу логина
        при попытке доступа к защищенным страницам.
        """
        urls = (
            self.URL_LIST,
            self.URL_SUCCESS,
            self.URL_ADD,
            self.URL_DETAIL,
            self.URL_EDIT,
            self.URL_DELETE,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.URL_LOGIN}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
