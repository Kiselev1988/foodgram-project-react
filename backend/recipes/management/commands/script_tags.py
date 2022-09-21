from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Loads tags'

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'суп', 'color': '#fff68f', 'slug': 'soup'},
            {'name': 'салат', 'color': '#a0db8e', 'slug': 'salat'},
        ]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(
            self.style.SUCCESS('Тэги загружены')
        )
