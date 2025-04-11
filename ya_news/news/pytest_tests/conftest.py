from datetime import timedelta

import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=(comment.id,))


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
    return News.objects.create(title='Заголовок', text='Текст новости',)


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def list_news():
    news_count = settings.NEWS_COUNT_ON_HOME_PAGE + 1
    news_list = [
        News(
            title=f'Заголовок {i}',
            text=f'Текст новости {i}',
            date=timezone.now() - timedelta(days=i)
        ) for i in range(news_count)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def list_comments(author, news):
    for i in range(5):
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {i}'
        )


@pytest.fixture
def new_comment(news):
    return {
        'text': 'Новый комментарий',
        'news': news.id,
    }
