from django.conf import settings

import pytest

from django.test.client import Client

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):  
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):  
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    new_news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return new_news


@pytest.fixture
def comment(author, news):
    new_comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return new_comment


@pytest.fixture
def list_news():
    news_list = [
        News.objects.create(title=f'Заголовок {i}', text=f'Текст новости {i}')
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]
    return news_list


@pytest.fixture
def list_comments(author, news):
    comments = [
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {i}'
        ) for i in range(5)
    ]
    return news, comments
