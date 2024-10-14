from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'phone_number', 'age', 'status']
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
                'status': instance.status,
               # 'phone_number': instance.phone_number,
            },
            #'access': str(refresh.access_token),
            #'refresh': str(refresh),
        }

class LoginSerializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Неверные учетные данные')

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

class EmptySerializer(serializers.Serializer):
    pass

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = '__all__'

    def validate_age(self, value):
        if value < 18:
            raise serializers.ValidationError("Возраст должен быть не менее 18.")
        return value

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['country_name']

class DirectorSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = ['director_name', 'age']


class ActorSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['actor_name', 'age']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['genre_name']

class FavoriteSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format=('%d-%m-%Y %H:%M'))
    class Meta:
        model = Favorite
        fields = ['user', 'created_date']

class MovieListSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField(read_only=True)
    genre = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['movie_name', 'year', 'country', 'genre', 'movie_trailer', 'average_rating']

    def get_average_rating(self, obj):
            return obj.get_average_rating()

    def get_country(self, obj):
        return ", ".join([country.country_name for country in obj.country.all()])

    def get_genre(self, obj):
        return ", ".join([genre.genre_name for genre in obj.genre.all()])

class ActorSerializer(serializers.ModelSerializer):
    movies = MovieListSerializer(many=True, read_only=True)
    class Meta:
        model = Actor
        fields = ['actor_name', 'bio', 'age', 'actor_image', 'movies']

class MovieLanguagesSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    class Meta:
        model = MovieLanguages
        fields = '__all__'

class HistorySerializer(serializers.ModelSerializer):
    viewed_at = serializers.DateTimeField(format=('%d-%m-%Y'))
    movie = MovieListSerializer(read_only=True)
    class Meta:
        model = History
        fields = ['user', 'movie', 'viewed_at']

class MomentsSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    class Meta:
        model = Moments
        fields = ['movie', 'movie_moments']

class RatingSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format=('%d-%m-%Y'))
    movie = MovieListSerializer(read_only=True)
    class Meta:
        model = Rating
        fields = ['user', 'movie', 'stars', 'parent', 'text', 'created_date']

class FavoriteMovieSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    cart = FavoriteSerializer(read_only=True)
    class Meta:
        model = FavoriteMovie
        fields = ['cart', 'movie']

class DirectorSerializer(serializers.ModelSerializer):
    movies = MovieListSerializer(many=True, read_only=True)
    class Meta:
        model = Director
        fields = ['director_name', 'bio', 'age', 'director_image', 'movies']

class MovieSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField(read_only=True)
    genre = serializers.SerializerMethodField(read_only=True)
    director = serializers.SerializerMethodField(read_only=True)
    actor = serializers.SerializerMethodField(read_only=True)
    types = serializers.ListField(child=serializers.CharField())
    average_rating = serializers.SerializerMethodField()
    languages = MovieLanguagesSerializer(many=True, read_only=True)
    momenty = MomentsSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    class Meta:
        model = Movie
        fields = ['movie_name', 'year',  'movie_time', 'description', 'movie_image', 'status_movie',
                  'country', 'genre', 'director', 'actor', 'types', 'average_rating', 'languages',
                  'momenty', 'ratings']


    def get_average_rating(self, obj):
            return obj.get_average_rating()

    def get_country(self, obj):
        return obj.country.first().country_name if obj.country.exists() else None

    def get_genre(self, obj):
        return obj.genre.first().genre_name if obj.genre.exists() else None

    def get_director(self, obj):
        return f"{obj.director.first().director_name}, age: {obj.director.first().age}" if obj.director.exists() else None

    def get_actor(self, obj):
        return f"{obj.actor.first().actor_name}, age: {obj.actor.first().age}" if obj.actor.exists() else None