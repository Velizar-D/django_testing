from django.urls import reverse
import pytest
from news.models import News

MAX_NEWS_ON_PAGE = 10


@pytest.mark.django_db
def test_news_count_on_home_page(client, home_url):
    """
    Количество новостей на главной странице — не более 10(MAX_NEWS_ON_PAGE).
    """
    response = client.get(home_url)
    assert len(response.context['news_list']) <= MAX_NEWS_ON_PAGE


@pytest.mark.django_db
def test_news_order_on_home_page(client, home_url):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(home_url)
    news_list = response.context['news_list']
    expected_news_list = list(News.objects.all().order_by('-date'))
    assert list(news_list) == expected_news_list


@pytest.mark.django_db
def test_comments_order_on_news_page(client, second_news, second_comments):
    """Комментарии на странице отдельной новости отсортированы:
    старые в начале списка, новые — в конце."""
    url = reverse('news:detail', args=(second_news[0].id,))
    response = client.get(url)
    comments_list = response.context['news'].comment_set.all()
    assert list(comments_list) == second_comments


@pytest.mark.django_db
@pytest.mark.parametrize('is_authenticated,form_is_available', [
    (False, False),
    (True, True),
])
def test_comment_form_availability(client, auth_user,
                                   news, is_authenticated, form_is_available):
    """Анонимному пользователю недоступна форма для
    отправки комментария на странице отдельной новости,
    а авторизованному доступна."""
    url = reverse('news:detail', args=(news.id,))
    if is_authenticated:
        client.force_login(auth_user)
    response = client.get(url)
    assert ('form' in response.context) == form_is_available
