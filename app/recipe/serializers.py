"""
Docstring for app.recipe.serializers
"""

from rest_framework import serializers
from core.models import Recipe, Tag, Ingrediant

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class IngrediantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingrediant
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, required=False)
    ingrediants = IngrediantSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingrediants']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingrediant(self, ingrediants, recipe):
        auth_user = self.context['request'].user
        for ingrediant in ingrediants:
            ingrediant_obj, created = Ingrediant.objects.get_or_create(
                user=auth_user,
                **ingrediant,
            )
            recipe.ingrediants.add(ingrediant_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingrediants = validated_data.pop('ingrediants', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingrediant(ingrediants, recipe)
        return recipe
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingrediants = validated_data.pop('ingrediants', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingrediants is not None:
            instance.ingrediants.clear()
            self._get_or_create_ingrediant(ingrediants, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}


    