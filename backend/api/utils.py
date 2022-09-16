from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe
from .serializers import RecipeForFollowersSerializer


def add_or_delete(request, model, recipe_id):
    user = request.user
    if request.method == 'DELETE':
        obj = model.objects.filter(
            user=user,
            recipe__id=recipe_id
        )
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            status=status.HTTP_400_BAD_REQUEST)
    if model.objects.filter(
        user=user,
        recipe__id=recipe_id
    ).exists():
        return Response(
            status=status.HTTP_400_BAD_REQUEST)
    recipe = get_object_or_404(
        Recipe,
        id=recipe_id
    )
    model.objects.create(
        user=user,
        recipe=recipe
    )
    serializer = RecipeForFollowersSerializer(recipe)
    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )
