from django.conf import settings

from news.forms import CommentForm
from news.models import News


def test_news_count(client, list_news, home_url):
    """Количество новостей на главной странице не более 10."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, list_news, home_url):
    """Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_news = News.objects.order_by('-date')[
        :settings.NEWS_COUNT_ON_HOME_PAGE
    ]
    assert list(object_list) == list(all_news)


def test_comments_order(client, news, list_comments, detail_url):
    """Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке.
    """
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = list(news.comment_set.all().order_by('created'))
    assert list(news.comment_set.all()) == all_comments


def test_comment_form_access_for_anonymous_user(client, news, detail_url):
    """Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_comment_form_access_for_authorized_user(author_client, news,
                                                 detail_url):
    """Авторизованному пользователю доступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
