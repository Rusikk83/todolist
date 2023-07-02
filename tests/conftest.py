from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from bot.tg.client import TgClient

pytest_plugins = "tests.fixtures"

@pytest.fixture()
def client() -> APIClient:
    return APIClient()

@pytest.fixture()
def auth_client(client, user) -> APIClient:
    client.force_login(user)
    return client

@pytest.fixture()
def mocked_send_message():
    with patch.object(TgClient, 'send_message') as mock:
        yield mock
