from schemas import QuestionCreate, QuestionUpdate
from repositories import QuestionRepository


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
