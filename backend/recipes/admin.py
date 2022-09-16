from django.contrib import admin

from .models import (
    Ingredient,
    Tag,
    Recipe,
    IngredientInRecipe,
    Favorite,
    Cart
)


class IngredientRecipeInline(admin.TabularInline):

    model = IngredientInRecipe
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    inlines = (IngredientRecipeInline,)
    list_display = (
        'id',
        'name',
        'author',
        'cooking_time',
        'id',
        'favorite_count',
        'pub_date'
    )
    search_fields = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    list_filter = ('name', 'author', 'tags')

    @admin.display(description='Количество избранных рецептов')
    def favorite_count(self, obj):
        return obj.favorite.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    empty_value_display = '-пусто-'


@admin.register(Cart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    empty_value_display = '-пусто-'
