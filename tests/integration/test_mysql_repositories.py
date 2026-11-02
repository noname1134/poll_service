import os

import mysql.connector
import pytest

import repositories
from exceptions import AnswerAlreadyExistsError
from schemas import QuestionCreate


@pytest.fixture
def question_factory(monkeypatch):
    if os.getenv("RUN_MYSQL_TESTS") != "1":
        pytest.skip("Set RUN_MYSQL_TESTS=1 and start compose.test.yaml")

    config = {
        "host": "127.0.0.1",
        "port": 3309,
        "database": "poll_test",
        "user": "poll_test_user",
        "password": "local_test_password",
        "connection_timeout": 10,
    }

    def connect():
        return mysql.connector.connect(**config)

    monkeypatch.setattr(repositories, "get_connection", connect)

    questions = repositories.QuestionRepository()
    created_ids = []

    def create_question():
        question = questions.create_question(
            QuestionCreate(
                title="Integration test question",
                option_1="Python",
                option_2="Java",
                option_3="C++",
                option_4="JavaScript",
            )
        )
        created_ids.append(question["id"])
        return question["id"]

    try:
        yield create_question
    finally:
        with connect() as connection:
            with connection.cursor() as cursor:
                for question_id in created_ids:
                    cursor.execute(
                        "DELETE FROM answers WHERE question_id = %s",
                        (question_id,),
                    )
                    cursor.execute(
                        "DELETE FROM questions WHERE id = %s",
                        (question_id,),
                    )
            connection.commit()


def test_duplicate_answer_is_rejected_by_mysql(question_factory):
    question_id = question_factory()
    answers = repositories.AnswerRepository()

    answers.create_answer(
        user_id=1,
        question_id=question_id,
        selected_option=2,
    )

    with pytest.raises(AnswerAlreadyExistsError):
        answers.create_answer(
            user_id=1,
            question_id=question_id,
            selected_option=3,
        )

    assert answers.get_answer(1, question_id) == {
        "user_id": 1,
        "question_id": question_id,
        "selected_option": 2,
    }

    counts = answers.get_option_counts(question_id)
    assert sum(row["total"] for row in counts) == 1


def test_deleting_question_cascades_to_its_answers(question_factory):
    question_id = question_factory()
    other_question_id = question_factory()

    questions = repositories.QuestionRepository()
    answers = repositories.AnswerRepository()

    answers.create_answer(
        user_id=1,
        question_id=question_id,
        selected_option=1,
    )
    answers.create_answer(
        user_id=2,
        question_id=question_id,
        selected_option=4,
    )
    answers.create_answer(
        user_id=1,
        question_id=other_question_id,
        selected_option=2,
    )

    counts = answers.get_option_counts(question_id)
    assert sum(row["total"] for row in counts) == 2

    assert questions.delete_question(question_id) is True

    assert questions.get_question(question_id) is None
    assert answers.get_answer(1, question_id) is None
    assert answers.get_answer(2, question_id) is None
    assert answers.get_option_counts(question_id) == []

    assert questions.get_question(other_question_id) is not None
    assert answers.get_answer(1, other_question_id)["selected_option"] == 2
