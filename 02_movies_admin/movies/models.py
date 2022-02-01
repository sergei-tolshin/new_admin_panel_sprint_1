import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

"""
Возникает проблема, если в миксине не указывать родителя models.Model и
абстрактность, то не применяются поля из миксина в наследуемых классах.
Если посмотреть код Django, то в нем у миксинов указывается родитель и
абстрактность, например class PermissionsMixin(models.Model): ...
Видимо в Django так работаю миксины с полями моделей :)
"""


class UUIDFieldMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedFieldMixin(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class BaseModel(UUIDFieldMixin, TimeStampedFieldMixin):

    class Meta:
        abstract = True


class Genre(BaseModel):
    name = models.CharField(_('name'), max_length=255, unique=True,)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    def __str__(self):
        return self.name


class Person(BaseModel):
    full_name = models.CharField(_('full name'), max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('person')
        verbose_name_plural = _('persons')

    def __str__(self):
        return self.full_name


class Filmwork(BaseModel):

    class Type(models.TextChoices):
        MOVIE = 'movie', _('movie')
        TV_SHOW = 'tv_show', _('tv show')

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation_date'))
    certificate = models.CharField(
        _('certificate'), max_length=512, blank=True, null=True)
    file_path = models.FileField(
        _('file'), blank=True, null=True, upload_to='movies/')
    rating = models.FloatField(_('rating'), blank=True, validators=[
                               MinValueValidator(0), MaxValueValidator(100)])
    type = models.CharField(_('type'), max_length=50, choices=Type.choices)
    genres = models.ManyToManyField(
        Genre, through='GenreFilmwork', verbose_name=_('genres'))
    persons = models.ManyToManyField(
        Person, through='PersonFilmwork', verbose_name=_('persons'))

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('film work')
        verbose_name_plural = _('film works')

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDFieldMixin, models.Model):
    film_work = models.ForeignKey(
        'Filmwork', on_delete=models.CASCADE, verbose_name=_('film work'))
    genre = models.ForeignKey(
        'Genre', on_delete=models.CASCADE, verbose_name=_('genre'))
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        unique_together = [['film_work', 'genre']]
        verbose_name = _('genre of film')
        verbose_name_plural = _('genres of film')


class PersonFilmwork(UUIDFieldMixin, models.Model):
    film_work = models.ForeignKey(
        'Filmwork', on_delete=models.CASCADE, verbose_name=_('film work'))
    person = models.ForeignKey(
        'Person', on_delete=models.CASCADE, verbose_name=_('person'))
    role = models.TextField(_('role'), null=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        unique_together = [['film_work', 'person', 'role']]
        verbose_name = _('person of film')
        verbose_name_plural = _('persons of film')
