from unittest.mock import patch

import pytest
from django.urls import reverse

from bot.tg.client import TgClient
from rest_framework import status


@pytest.mark.django_db()
class TestCreateGoalView:
    url = reverse('bot:bot-verify')


    def test_bot_verification_message_send(self, mocked_send_message, auth_client, tg_user):

        response = auth_client.patch(self.url, data={'verification_code': tg_user.verification_code})

        assert response.status_code == status.HTTP_200_OK
        mocked_send_message.assert_called_once_with(tg_user.chat_id, 'Bot token verified')


    def test_bot_user_relation_create(self, mocked_send_message, auth_client, user, tg_user_factory):
        tg_user = tg_user_factory.create(user=None)

        response = auth_client.patch(self.url, data={'verification_code': tg_user.verification_code})

        assert response.status_code == status.HTTP_200_OK
        tg_user.refresh_from_db()
        assert tg_user.user == user


    def test_bot_verification_code_fail(self, mocked_send_message, auth_client, user, tg_user_factory):
        tg_user = tg_user_factory.create(verification_code='code')

        response = auth_client.patch(self.url, data={'verification_code': 'another_code'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        tg_user.refresh_from_db()
        assert tg_user.user is None
        mocked_send_message.assert_not_called()
        assert response.json() == {'verification_code': ['Invalid verification code']}


