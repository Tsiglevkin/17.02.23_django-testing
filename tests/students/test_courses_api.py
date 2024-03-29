import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django_testing import settings
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
    course = courses_factory(_quantity=5)  # изменил количество курсов
    course_id = course[0].pk  # взял значение первого для проверки.

    # url = f"{reverse('courses-list')}{course_id}/"  # мое написание
    url = reverse('courses-detail', args=[course_id])  # совет преподавателя.
    response = client.get(url)

    assert response.status_code == 200

    response_data = response.json()
    response_course_name = response_data.get('name')

    assert response_course_name == course[0].name


@pytest.mark.django_db
def test_get_a_few_courses(user, client, courses_factory):
    courses = courses_factory(_quantity=10)
    url = reverse('courses-list')
    response = client.get(url)
    assert response.status_code == 200

    courses_list = response.json()

    for index_, course_data in enumerate(courses_list):
        assert course_data.get('name') == courses[index_].name


@pytest.mark.django_db
def test_check_id_filter(user, client, courses_factory):
    courses = courses_factory(_quantity=10)
    course_id = courses[0].pk

    # url = f"{reverse('courses-list')}{course_id}/"
    filter_data = {'pk': course_id}
    url = reverse('courses-list')

    response = client.get(url, data=filter_data)

    assert response.status_code == 200

    data = response.json()
    assert data[0].get('id') == courses[0].pk  # почему-то не видит атрибута id, поэтому pk.


@pytest.mark.django_db
def test_check_name_filter(user, client, courses_factory):
    courses = courses_factory(_quantity=10)
    course_id = courses[0].pk
    course_name = courses[0].name
    filter_data = {
        'id': course_id,
        'name': course_name,
    }

    url = reverse('courses-list')
    response = client.get(url, data=filter_data)

    assert response.status_code == 200

    data = response.json()
    assert data[0].get('name') == courses[0].name


@pytest.mark.django_db
def test_create_course(client, user):
    data = {'name': 'python-разработчик'}  # данные для создания модели
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


# Доп. задание.

@pytest.fixture
def students_quantity():
    return settings.MAX_STUDENTS_PER_COURSE


@pytest.mark.parametrize(
    ['students_count', 'expected_status'],
    (
            (25, 400),
            (10, 201),
    )
)
@pytest.mark.django_db
def test_students_quantity(client, students_count, expected_status, students_factory):
    # создаем одного студента, умножаем его id на нужное количество и проверяем

    student = students_factory(_quantity=1)
    students_list = [student[0].pk] * students_count  # список id, по которым идет проверка по количеству.
    url = reverse('courses-list')
    response_data = {
        'name': 'python',
        'students': students_list
    }  # данные для создания одного курса
    response = client.post(url, data=response_data)
    assert response.status_code == expected_status
