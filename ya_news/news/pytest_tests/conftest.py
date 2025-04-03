from django.contrib.auth import get_user_model
from django.urls import reverse
from news.models import News, Comment
import pytest

User = get_user_model()
NEWS_COUNT = 15
COMMENTS_COUNT = 3
SECOND_NEWS_COUNT = 3


@pytest.fixture
def client_loggin(client, author):
    """Возвращает аутентифицированного автора."""
    client.force_login(author)
    return client


@pytest.fixture
def form_data():
    """Предоставляет тестовые данные для формы комментария."""
    return {'text': 'Текст комментария'}


@pytest.fixture
def news():
    """Создает тестовый объект новости с заголовком и текстом."""
    return News.objects.create(
        title='Заголовок',
        text='Текст'
    )


@pytest.fixture
def author():
    """Создает и возвращает пользователя с именем 'author'."""
    return User.objects.create(username='author')


@pytest.fixture
def auth_user():
    """Создает и возвращает аутентифицированного пользователя (не автора)."""
    return User.objects.create(username='auth_user')


@pytest.fixture
def comment(news, author):
    """Создает тестовый комментарий к новости от указанного автора."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def second_news():
    """Создает список из 3 тестовых новостей для проверки отображения."""
    return [
        News.objects.create(title=f'Заголовок {i}', text=f'Текст {i}')
        for i in range(SECOND_NEWS_COUNT)
    ]


@pytest.fixture
def second_comments(second_news, author):
    """Создает 3 тестовых комментария к первой новости из second_news."""
    return [
        Comment.objects.create(
            news=second_news[0],
            author=author,
            text=f'Текст комментария {i}'
        )
        for i in range(COMMENTS_COUNT)
    ]


@pytest.fixture
def home_url():
    """Возвращает URL-адрес домашней страницы новостей."""
    return reverse('news:home')


@pytest.fixture
def comments_url(news):
    """Возвращает URL-адрес страницы с комментариями к новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def news_detail_url(news):
    """Возвращает URL-адрес страницы просмотра новости."""
    return reverse('news:detail', args=(news.id,))
