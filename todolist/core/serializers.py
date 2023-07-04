from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed, NotAuthenticated

USER_MODEL = get_user_model()


class PasswordField(serializers.CharField):

    def __init__(self, **kwargs):  # переопределяем инициализацию пароля
        kwargs['style'] = {'input_type': 'password'}
        kwargs.setdefault('write_only', True)
        super().__init__(**kwargs)
        self.validators.append(validate_password)  # добавление валидатора пароля


class RegistrationSerialiser(serializers.ModelSerializer):
    password = PasswordField(required=True)
    password_repeat = PasswordField(required=True)

    class Meta:
        model = USER_MODEL
        read_only_fields = ('id',)
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'password_repeat',
        )

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_repeat']:  # проверка совпадения паролей
            raise ValidationError("password and password_repeat is not equal")
        return attrs

    def create(self, validated_data: dict) -> USER_MODEL:
        del validated_data['password_repeat']  # удаляем поле повтора пароля
        validated_data['password'] = make_password(validated_data['password'])  # хешируем пароль
        return super().create(validated_data)  # создаем пользователя


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def create(self, validated_data) -> USER_MODEL:
        if not (user := authenticate(  # аутентификация пользователя
            username=validated_data['username'],
            password=validated_data['password']
        )):
            raise AuthenticationFailed
        return user

    class Meta:
        model = USER_MODEL
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = USER_MODEL
        fields = ('id', 'username', 'first_name', 'last_name', 'email',)


class UpdatePasswordSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = PasswordField(required=True, write_only=True)

    def validate(self, attrs: dict) -> dict:  # проверка старого пароля
        if not (user := attrs['user']):
            raise NotAuthenticated
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'incorrect password'})
        return attrs

    def create(self, validated_data: dict) -> None:  # запрет
        raise NotImplementedError

    def update(self, instance: USER_MODEL, validated_data: dict) -> USER_MODEL:
        instance.password = make_password(validated_data['new_password'])  # хеширование пароля
        instance.save(update_fields=('password',))
        return instance
