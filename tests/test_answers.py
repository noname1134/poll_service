from exceptions import AnswerAlreadyExistsError


def test_registered_user_can_answer(answer_api):
    client, service = answer_api
    response = client.post("/questions/1/answers", json={"user_id": 1, "selected_option": 2})

    assert response.status_code == 200
    assert response.json() == {"user_id": 1, "question_id": 1, "selected_option": 2}
    service.answer_repository.create_answer.assert_called_once_with(1, 1, 2)


def test_unregistered_user_cannot_answer(answer_api):
    client, service = answer_api
    service.user_client.get_user.return_value = {"id": 1, "is_registered": False}
    response = client.post("/questions/1/answers", json={"user_id": 1, "selected_option": 2})

    assert response.status_code == 403
    service.answer_repository.create_answer.assert_not_called()


def test_duplicate_answer_returns_conflict(answer_api):
    client, service = answer_api
    service.answer_repository.create_answer.side_effect = AnswerAlreadyExistsError(
        "User has already answered this question"
    )
    response = client.post("/questions/1/answers", json={"user_id": 1, "selected_option": 2})

    assert response.status_code == 409
