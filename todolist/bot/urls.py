
from django.urls import path

from bot.tg.bot_view import VerificationView

urlpatterns = [
    path('verify', VerificationView.as_view(), name='bot-verify')
]