from http import HTTPStatus

from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.response import Response

from recipes.models import IngredientInRecipe


def get_ingredients_and_make_txt(user):
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
