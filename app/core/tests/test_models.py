"""
test for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models
from unittest.mock import patch

def create_user(email='user@example.com', password='userpass'):
    return get_user_model().objects.create_user(
        'user@example.com',
        'userpass',
    )

class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        email = 'test@example.com'
        password = 'changeme'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['test2@Example.com', 'test2@example.com'],
            ['test3@EXAMPLE.COM', 'test3@example.com'],
            ['test4@Example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected )

    def test_new_user_without_email_raises_error(self):

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
             'test1@example.com',
             'test123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        user = get_user_model().objects.create_user(
            'test@example.com'
            'testpass',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='test sample recipe',
            time_minutes=5,
            price=Decimal('5.50'),
            description='recipe description',
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')
        self.assertEqual(str(tag), tag.name)

    def test_create_ingrediant(self):
        user = create_user()
        ingrediant = models.Ingrediant.objects.create(
            user=user,
            name='ingrediant'
        )
        self.assertEqual(str(ingrediant), ingrediant.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpeg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpeg')

    