from schemas import QuestionCreate, QuestionUpdate, AnswerCreate, AnswerUpdate
from repositories import QuestionRepository, AnswerRepository
from clients import UserClient
from exceptions import QuestionNotFoundError, UserNotFoundError, UserNotRegisteredError, AnswerNotFoundError


class QuestionService:
    def __init__(self):
        self.repository = QuestionRepository()

    def create_question(self, question: QuestionCreate):
        return self.repository.create_question(question)

    def get_question(self, question_id: int):
        return self.repository.get_question(question_id)

    def update_question(self, question_id: int, update: QuestionUpdate):
        changes = update.model_dump(exclude_unset=True)
        if any(value is None for value in changes.values()):
            raise ValueError("Question fields cannot be null")
        return self.repository.update_question(question_id, changes)

    def delete_question(self, question_id: int):
        return self.repository.delete_question(question_id)


class AnswerService:
    def __init__(self):
        self.answer_repository = AnswerRepository()
        self.question_repository = QuestionRepository()
        self.user_client = UserClient()

    def create_answer(self, question_id: int, answer: AnswerCreate):
        if self.question_repository.get_question(question_id) is None:
            raise QuestionNotFoundError("Question not found")

        user = self.user_client.get_user(answer.user_id)
        if user is None:
            raise UserNotFoundError("User not found")
        if not user["is_registered"]:
            raise UserNotRegisteredError("User is not registered")

        return self.answer_repository.create_answer(answer.user_id, question_id, answer.selected_option)


    def update_answer(self, user_id: int, question_id: int, update: AnswerUpdate):
        if self.question_repository.get_question(question_id) is None:
            raise QuestionNotFoundError("Question not found")
        user = self.user_client.get_user(user_id)
        if user is None:
            raise UserNotFoundError("User not found")
        if not user["is_registered"]:
            raise UserNotRegisteredError("User is not registered")

        res = self.answer_repository.update_answer(user_id, question_id, update.selected_option)
        if res is None:
            raise AnswerNotFoundError("Answer not found")

        return res
