import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Course, Student


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user('тестовый пользователь')


@pytest.fixture
def courses_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


@pytest.fixture
def students_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


@pytest.mark.django_db
def test_get_1st_course(user, client, courses_factory):

    # course = courses_factory(_quantity=5)
    # url = reverse('courses')  # выпадает ошибка использования функции - не найдено имя ссылки

    response = client.get('/courses/')

    assert response.status_code == 200  # тест не проходит - статус 404.

    # data = response.json()
    # request_course = data.get('name')
    #
    # assert request_course == course[0].name
    # print(request_course, course[0].name)
