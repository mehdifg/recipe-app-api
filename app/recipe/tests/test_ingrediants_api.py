"""
Docstring for app.recipe.tests.test_ingrediants_api
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingrediant, Recipe
from recipe.serializers import IngrediantSerializer


INGREDIANTS_URL = reverse('recipe:ingrediant-list')
def detail_url(ingrediant_id):
    return reverse('recipe:ingrediant-detail', args=[ingrediant_id])

def create_user(email='user@example.com', password='userpass'):
    return get_user_model().objects.create_user(
        email=email,
        password=password
    )

class PublicIngrediantsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INGREDIANTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngrediantsApiTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingrediants(self):
        Ingrediant.objects.create(user=self.user, name='test name')
        Ingrediant.objects.create(user=self.user, name='test name 1')

        res = self.client.get(INGREDIANTS_URL)

        ingrediant = Ingrediant.objects.all().order_by('-name')
        serializer = IngrediantSerializer(ingrediant, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingrediant_limited_to_user(self):
        user2 = create_user(email='user2@example.com')
        Ingrediant.objects.create(user=user2, name='salt')
        ingrediant = Ingrediant.objects.create(user=self.user, name='pepper')
        res = self.client.get(INGREDIANTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingrediant.name)
        self.assertEqual(res.data[0]['id'], ingrediant.id)

    def test_update_ingrediant(self):
        ingrediant = Ingrediant.objects.create(user=self.user, name='test name')
        payload = {
            'name': 'update name'
        }
        url = detail_url(ingrediant.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingrediant.refresh_from_db()
        self.assertEqual(ingrediant.name, payload['name'])

    def test_delete_ingrediant(self):
        ingrediant = Ingrediant.objects.create(user=self.user, name='test name')

        url = detail_url(ingrediant.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingrediants = Ingrediant.objects.filter(user=self.user)
        self.assertFalse(ingrediants.exists())

    def test_filter_ingrediants_assigned_to_recipes(self):
        ingrediant1 = Ingrediant.objects.create(user=self.user, name='ingrediant1')
        ingrediant2 = Ingrediant.objects.create(user=self.user, name='ingrediant2')
        recipe = Recipe.objects.create(
            title='recipe title',
            time_minutes=5,
            price=Decimal('2.5'),
            user=self.user
        )
        recipe.ingrediants.add(ingrediant1)
        res = self.client.get(INGREDIANTS_URL, {'assigned_only': 1})

        s1 = IngrediantSerializer(ingrediant1)
        s2 = IngrediantSerializer(ingrediant2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingrediants_unique(self):
        ingrediant = Ingrediant.objects.create(user=self.user, name='ingrediant')
        Ingrediant.objects.create(user=self.user, name='ingrediant6')
        recipe1 = Recipe.objects.create(
            title='recipe title',
            time_minutes=5,
            price=Decimal('2.5'),
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='recipe2 title',
            time_minutes=5,
            price=Decimal('2.5'),
            user=self.user
        )
        recipe1.ingrediants.add(ingrediant)
        recipe2.ingrediants.add(ingrediant)

        res = self.client.get(INGREDIANTS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)




