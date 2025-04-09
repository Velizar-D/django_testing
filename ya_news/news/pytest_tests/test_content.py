from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm
from news.models import News


def test_news_count(client, list_news):
    """Количество новостей на главной странице не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, list_news):
    """Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_news = News.objects.order_by('-date')
    expected_news = list(all_news[:settings.NEWS_COUNT_ON_HOME_PAGE])
    assert list(object_list) == expected_news


def test_comments_order(client, news, list_comments):
    """Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all() if news else []
    if all_comments.count() > 1:
        assert all_comments[0].created < all_comments[1].created


def test_comment_form_access_for_anonymous_user(client, news):
    """Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_comment_form_access_for_authorized_user(author_client, news):
    """Авторизованному пользователю доступна форма для отправки
    комментария на странице отдельной новости.
    """
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
