from importlib import import_module
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def answer_api(monkeypatch):
    monkeypatch.setenv("USER_SERVICE_URL", "http://user-service.test")

    main = import_module("main")
    controllers = import_module("controllers")
    service = controllers.answer_service

    question_repository = Mock()
    answer_repository = Mock()
    user_client = Mock()

    monkeypatch.setattr(service, "question_repository", question_repository)
    monkeypatch.setattr(service, "answer_repository", answer_repository)
    monkeypatch.setattr(service, "user_client", user_client)

    question_repository.get_question.return_value = {"id": 1}
    user_client.get_user.return_value = {"id": 1, "is_registered": True}
    answer_repository.create_answer.return_value = {
        "user_id": 1,
        "question_id": 1,
        "selected_option": 2,
    }

    with TestClient(main.app) as client:
        yield client, service
