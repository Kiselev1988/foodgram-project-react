from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Ник пользователя',
        help_text='Введите уникальное имя пользователя'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта',
        help_text='Введите электронную почту пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Имя пользователя',
        help_text='Введите имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Фамилия пользователя',
        help_text='Введите фамилию пользователя'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE,
    )


    class Meta:
        ordering = ('author',)
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='follow_user_author_constraint'
            ),
        )

    def __str__(self):
        return (
            f'{self.user.username} подписан на {self.author.username}'
        )
