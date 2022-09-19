from django.http import HttpResponse


def make_cart_txt(user, ingredients):
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
