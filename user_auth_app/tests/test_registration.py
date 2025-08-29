import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_user_registration():
    client = APIClient()
    url = reverse('register')
    data = {
        'email': 'testuser@example.com',
        'password': 'testpassword', 
        'confirmed_password': 'testpassword'
    } 

    response = client.post(url, data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED

    assert 'user' in response.data
    assert 'token' in response.data

    user_data = response.data['user']
    assert user_data['email'] == 'testuser@example.com'
    assert 'id' in user_data
    
    