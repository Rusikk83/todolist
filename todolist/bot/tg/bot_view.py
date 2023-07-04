from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.serializers import TgUserSerializer


class VerificationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TgUserSerializer

    def patch(self, request: Request, *args, **kwargs) -> Response:
        serializer = TgUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tg_user: TgUser = serializer.save(user=request.user)

        TgClient().send_message(tg_user.chat_id, 'Bot token verified')

        return Response(serializer.data)
