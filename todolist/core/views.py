from django.contrib.auth import get_user_model, login, logout

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from core.serializers import RegistrationSerialiser, LoginSerializer, UserSerializer, UpdatePasswordSerializer

# Create your views here.
USER_MODEL = get_user_model()

"""представление для регистрации пользователя"""


class RegistrationView(generics.CreateAPIView):
    model = USER_MODEL
    permission_classes = [permissions.AllowAny]
    serializer_class = RegistrationSerialiser


"""представление для аутентификации пользователя"""


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request=request, user=user)
        return Response(serializer.data)


"""представление для профиля клиента"""


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


"""представление для обновления пароля пользователя"""


class UpdatePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    def get_object(self):
        return self.request.user
