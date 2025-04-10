from fastapi.testclient import TestClient
from fastapi import status

from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': "nonexistent@mail.com"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        'name': 'New User',
        'email': 'new.user@mail.com'
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == status.HTTP_201_CREATED
    assert isinstance(response.json(), int)  # Проверяем что возвращается ID

    # Проверяем что пользователь действительно создан
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_response.status_code == 200
    assert get_response.json()['name'] == new_user['name']
    assert get_response.json()['email'] == new_user['email']

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_email = users[0]['email']
    new_user = {
        'name': 'Duplicate User',
        'email': existing_email
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "User with this email already exists"}

def test_delete_user():
    '''Удаление пользователя'''
    # Сначала создадим тестового пользователя для удаления
    temp_user = {
        'name': 'Temp User',
        'email': 'temp.user@mail.com'
    }
    create_response = client.post("/api/v1/user", json=temp_user)
    user_id = create_response.json()
    
    # Проверяем что пользователь существует
    get_response = client.get("/api/v1/user", params={'email': temp_user['email']})
    assert get_response.status_code == 200
    
    # Удаляем пользователя
    delete_response = client.delete("/api/v1/user", params={'email': temp_user['email']})
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # Проверяем что пользователь больше не существует
    get_response_after_delete = client.get("/api/v1/user", params={'email': temp_user['email']})
    assert get_response_after_delete.status_code == status.HTTP_404_NOT_FOUND
