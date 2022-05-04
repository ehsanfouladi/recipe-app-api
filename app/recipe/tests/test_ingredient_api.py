from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.Serializers import IngredientSerializer


INGREDIENTS_URl = reverse('recipe:ingredient-list')


class PublicIngredientApiTest(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(INGREDIENTS_URl)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test the private ingredient can be retrieved by authenticated user"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'Testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(
            user=self.user, name='Kale'
        )
        Ingredient.objects.create(
            user=self.user, name='Salt'
        )

        res = self.client.get(INGREDIENTS_URl)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for authenticated users can be returned"""
        user2 = get_user_model().objects.create_user(
            'other@example.com',
            'pass12345'
            )
        Ingredient.objects.create(
            user=user2, name='Vinger'
        )
        ingredient = Ingredient.objects.create(
            user=self.user, name='Tumeric'
        )

        res = self.client.get(INGREDIENTS_URl)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test create a new ingredient"""
        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENTS_URl, payload)

        exists = Ingredient.objects.filter(
            user=self.user, name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test create an invalid ingredient fails"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URl, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """Test filtering ingredients by those assigned to recipe."""
        ingrediant1 = Ingredient.objects.create(
            user=self.user,
            name="Breakfast"
            )
        ingrediant2 = Ingredient.objects.create(
            user=self.user,
            name="Lunch"
            )

        recipe = Recipe.objects.create(
            title="coriander eggs on toast",
            time_minutes=10,
            price=100,
            user=self.user
        )
        recipe.ingredients.add(ingrediant1)
        res = self.client.get(INGREDIENTS_URl, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingrediant1)
        serializer2 = IngredientSerializer(ingrediant2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

