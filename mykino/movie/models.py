from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ForeignKey, Avg
from django.utils.translation.template import blankout
from phonenumber_field.formfields import PhoneNumberField
from multiselectfield import MultiSelectField


class UserProfile(AbstractUser):
    age = models.PositiveIntegerField(validators=[MinValueValidator(18)], null=True, blank=True)
    phone_number = PhoneNumberField(region='KG')
    STATUS_CHOICES = (
        ('pro', 'Pro'),
        ('simple', 'Simple'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='simple')


class Country(models.Model):
    country_name = models.CharField(max_length=22, unique=True)

    def __str__(self):
        return f'{self.country_name}'

class Director(models.Model):
    director_name = models.CharField(max_length=22)
    bio = models.TextField(null=True, blank=True)
    age = models.PositiveIntegerField(default=0)
    director_image = models.ImageField(upload_to='director_images/', null=True, blank=True)

    def __str__(self):
        return f'{self.director_name}'

class Actor(models.Model):
    actor_name = models.CharField(max_length=22)
    bio = models.TextField(null=True, blank=True)
    age = models.PositiveIntegerField(default=0)
    actor_image = models.ImageField(upload_to='actor_images/', null=True, blank=True)

    def __str__(self):
        return f'{self.actor_name}'

class Genre(models.Model):
    genre_name = models.CharField(max_length=22, unique=True)

    def __str__(self):
        return f'{self.genre_name}'

class Movie(models.Model):
    TYPE_CHOICES = [
        ('144', '144p'),
        ('360', '360p'),
        ('480', '480p'),
        ('720', '720p'),
        ('1080', '1080p'),
    ]
    STATUS_CHOICES = [
        ('pro', 'Pro'),
        ('simple', 'Simple'),
    ]
    movie_name = models.CharField(max_length=22)
    year = models.IntegerField()
    country = models.ManyToManyField(Country)
    director = models.ManyToManyField(Director, related_name='movies')
    actor = models.ManyToManyField(Actor, related_name='movies')
    genre = models.ManyToManyField(Genre)
    types = MultiSelectField(choices=TYPE_CHOICES, max_choices=22)
    movie_time = models.SmallIntegerField(null=True, blank=True)
    description = models.TextField()
    movie_trailer = models.FileField(upload_to='movie_trailer/', null=True, blank=True)
    movie_image = models.ImageField(upload_to='movie_img/', null=True, blank=True)
    status_movie = models.CharField(max_length=10, choices=STATUS_CHOICES, default='simple', null=True, blank=True)

    def __str__(self):
        return f'{self.movie_name}'

    def get_average_rating(self):
        average = self.ratings.aggregate(Avg('stars'))['stars__avg']
        return round(average, 2) if average is not None else 0

    # def get_average_rating(self):
    #     ratings = self.ratings.all()
    #     if ratings.exists():
    #         return round(sum(ratings.stars for rating in ratings) / ratings.count(), 1)
    #     return 0

class MovieLanguages(models.Model):
    language = models.CharField(max_length=22)
    video = models.FileField(upload_to='videos/')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='languages')

    def __str__(self):
        return f"{self.movie.movie_name} ({self.language})"

class Moments(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='momenty')
    movie_moments = models.ImageField(upload_to='moments/')

    def __str__(self):
        return f"Моменты из {self.movie.movie_name}"

class Rating(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    stars = models.IntegerField(default=1, choices=[(i, str(i)) for i in range(1, 11)], verbose_name='Рейтинг')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movie.movie_name} ({self.stars} stars)"


class Favorite(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"

class FavoriteMovie(models.Model):
    cart = ForeignKey(Favorite, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorite')

    def __str__(self):
        return f"{self.cart} - {self.movie}"

class History(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.movie}'
