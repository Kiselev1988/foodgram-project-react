from http import HTTPStatus

from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAdminOrAuthor
from .serializers import (
    UsersListSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    RecipeForFollowersSerializer,
    FollowSerializer
)
from recipes.models import (
    Ingredient,
    Recipe,
    Cart,
    Tag,
    IngredientInRecipe,
    Favourite
)
from users.models import Follow, User
from .utils import add_or_delete


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrAuthor,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrAuthor,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = IngredientFilter


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersListSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user.id == author.id:
                raise ValidationError('Нельзя подписаться на себя')
            else:
                serializer = FollowSerializer(
                    Follow.objects.create(user=request.user, author=author),
                    context={'request': request},
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if Follow.objects.filter(
                    user=request.user, author=author
            ).exists():
                Follow.objects.filter(
                    user=request.user, author=author
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        return RecipeSerializer if self.action in (
            'list', 'retrieve'
        ) else RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(
                recipe=recipe,
                user=request.user,
        ).exists():
            return Response(status=HTTPStatus.BAD_REQUEST)
        model.objects.create(recipe=recipe, user=request.user)
        serializer = RecipeForFollowersSerializer(recipe)
        return Response(data=serializer.data, status=HTTPStatus.CREATED)

    def delete_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(
                user=request.user,
                recipe=recipe,
        ).exists():
            model.objects.filter(
                user=request.user,
                recipe=recipe,
            ).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favourite(self, request, pk=None):
        return add_or_delete(request, Favourite, pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def cart(self, request, pk):
        return add_or_delete(request, Cart, pk)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_cart(self, request):
        user = request.user
        if not user.cart.exists():
            return Response(status=HTTPStatus.BAD_REQUEST)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__cart__user=user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit',
        ).annotate(
            value=Sum('amount')
        ).order_by('ingredients__name')
        response = HttpResponse(
            content_type='text/plain',
            charset='utf-8',
        )
        response['Content-Disposition'] = 'attachment; filename="listbuy.txt"'
        response.write('Список продуктов:\n')
        for ingredient in ingredients:
            response.write(
                f'{ingredient["ingredients__name"]} '
                f'{ingredient["value"]} '
                f'{ingredient["ingredients__measurement_unit"]}'
            )
        return response
