from database import get_connection
from schemas import QuestionCreate


class QuestionRepository:
    @staticmethod
    def get_question(question_id: int):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
                result = cursor.fetchone()
                return result
            finally:
                cursor.close()
        finally:
            connection.close()

    def create_question(self, question: QuestionCreate):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute("INSERT INTO questions (title, option_1, option_2, option_3, option_4) VALUES (%s, %s, %s, %s, %s, %s)",
                    (
                        question.title,
                        question.option_1,
                        question.option_2,
                        question.option_3,
                        question.option_4
                    )
                )
                connection.commit()
                question_id = cursor.lastrowid
            finally:
                cursor.close()
        finally:
            connection.close()

        return self.get_question(question_id)