from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    IngredientInRecipe,
    Favourite,
    Ingredient,
    Recipe,
    Cart,
    Tag
)
from users.models import Follow, User


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'password',
            'username',
            'first_name',
            'last_name'
        )
        extra_kwargs = {'password': {'write_only': True}}


class UsersListSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'amount'
        )

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиентов должно быть больше 0'
            )
        return value


class ReadIngredientsRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(
        source='ingredients.name',
        read_only=True
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit'
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    image = Base64ImageField()
    author = UsersListSerializer(
        read_only=True,
        many=False
        )
    ingredients = ReadIngredientsRecipeSerializer(
        many=True,
        source='amount_ingredient'
    )

    class Meta:
        model = Recipe
        fields = (
            'name',
            'image',
            'text',
            'cooking_time',
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Cart.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favourite.objects.filter(
            user=user,
            recipe=obj
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(use_url=True, )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise serializers.ValidationError(
                ''
            )
        return cooking_time

    def check_ingredients(self, data):
        validated_items = []
        existed = []
        for item in data:
            ingredient = Ingredient.objects.get(pk=item['id']).name
            if ingredient in validated_items:
                existed.append(ingredient)
            validated_items.append(ingredient)
        if existed:
            raise serializers.ValidationError(
                'Этот ингредиент уже добавлен'
            )

    def validate(self, data):
        ingredients = data.get('ingredients')
        self.check_ingredients(ingredients)
        data['ingredients'] = ingredients
        return data

    @staticmethod
    def create_ingredients(ingredients, recipe):
        ingredient_list = []
        for ingredient in ingredients:
            amount = ingredient['amount']
            recipe_ingredient = IngredientInRecipe(
                ingredients=get_object_or_404(
                    Ingredient, id=ingredient['id']
                ),
                recipe=recipe,
                amount=amount
            )
            ingredient_list.append(recipe_ingredient)
        IngredientInRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.create_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        IngredientInRecipe.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        return RecipeSerializer(
            recipe,
            context={'request': self.context.get('request')}
        ).data


class RecipeForFollowersSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'email',
            'id',
            'username'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeForFollowersSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()
