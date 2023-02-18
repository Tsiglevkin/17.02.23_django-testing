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
def test_get_one_course(user, client, courses_factory):
    course = courses_factory(_quantity=1)

    response = client.get('/api/v1/courses/')

    assert response.status_code == 200

    data = response.json()
    request_course = data[0].get('name')

    assert request_course == course[0].name


@pytest.mark.django_db
def test_get_a_few_courses(user, client, courses_factory):
    courses = courses_factory(_quantity=10)

    response = client.get('/api/v1/courses/')
    assert response.status_code == 200

    courses_list = response.json()

    for index_, course_data in enumerate(courses_list):
        assert course_data.get('name') == courses[index_].name


@pytest.mark.django_db
def test_check_id_filter(user, client, courses_factory):
    courses = courses_factory(_quantity=10)

    response = client.get('/api/v1/courses/1/')

    assert response.status_code == 200

    data = response.json()
    assert data.get('id') == courses[0].pk  # почему-то не видит атрибута id, поэтому pk.


@pytest.mark.django_db
def test_check_name_filter(user, client, courses_factory):
    courses = courses_factory(_quantity=10)

    response = client.get(f'/api/v1/courses/1/?name={courses[0].name}')

    assert response.status_code == 200

    data = response.json()
    assert data.get('name') == courses[0].name


@pytest.mark.django_db
def test_create_course(client, user):
    data = {'name': 'python-разработчик'}  #  данные для создания модели
    response = client.post(
        path='/api/v1/courses/',
        data=data,
    )  # формат не указываем, т.к. прописаны настройки в REST_FRAMEWORK

    assert response.status_code == 201

    response_data = response.json()
    assert response_data.get('name') == data.get('name')


@pytest.mark.django_db
def test_update_course(courses_factory, client, user):
    courses = courses_factory(_quantity=2)
    new_data = {'pk': courses[0].pk, 'name': 'update name'}

    patch_response = client.patch(path=f'/api/v1/courses/{courses[0].pk}/', data=new_data)
    assert patch_response.status_code == 200

    get_response = client.get(path=f'/api/v1/courses/{courses[0].pk}/')
    data = get_response.json()

    assert data.get('name') == new_data.get('name')


@pytest.mark.django_db
def test_delete_course(user, client, courses_factory):
    courses = courses_factory(_quantity=5)
    count = Course.objects.count()

    response = client.delete(path=f'/api/v1/courses/{courses[0].pk}/')

    assert response.status_code == 204

    next_count = Course.objects.count()

    assert next_count == count - 1

