from django.conf import settings
from django.urls import reverse

import pytest


@pytest.mark.django_db
def test_news_count(client, list_news):
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, list_news):
    """Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_news = list(object_list)
    all_news.sort(key=lambda x: x.date, reverse=True)
    assert all_news == list_news


@pytest.mark.django_db
def test_comments_order(client, news, list_comments):
    """Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    if news:
        all_comments = news.comment_set.all()
    else:
        all_comments = []
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_comment_form_access(author_client, not_author_client, client, news):
    """Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости, а авторизованному доступна."""
    url = reverse('news:detail', args=(news.id,))
    response_anonymous = client.get(url)
    assert 'form' not in response_anonymous.context
    response_author = author_client.get(url)
    assert 'form' in response_author.context
