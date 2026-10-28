from mysql.connector import IntegrityError, errorcode

from exceptions import AnswerAlreadyExistsError
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

    @staticmethod
    def delete_question(question_id: int):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))
                deleted_count = cursor.rowcount
                connection.commit()
            finally:
                cursor.close()
        finally:
            connection.close()
        if deleted_count == 0:
            return None
        return True


    def create_question(self, question: QuestionCreate):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO questions (title, option_1, option_2, option_3, option_4) VALUES (%s, %s, %s, %s, %s)",
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


    def update_question(self, question_id: int, changes: dict):
        allowed_fields = {"title", "option_1", "option_2", "option_3", "option_4"}

        if not changes:
            return self.get_question(question_id)

        if not set(changes).issubset(allowed_fields):
            raise ValueError("Unsupported update field")

        set_clause = ", ".join(f"{column} = %s" for column in changes)
        values = tuple(changes.values()) + (question_id,)

        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute("UPDATE questions SET " + set_clause + " WHERE id = %s", values)
                connection.commit()
            finally:
                cursor.close()
        finally:
            connection.close()

        return self.get_question(question_id)


class AnswerRepository:
    @staticmethod
    def get_answer(user_id: int, question_id: int):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM answers WHERE user_id = %s AND question_id = %s", (user_id, question_id))
                result = cursor.fetchone()
                return result
            finally:
                cursor.close()
        finally:
            connection.close()


    def create_answer(self, user_id: int, question_id: int, selected_option: int):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO answers (user_id, question_id, selected_option) VALUES (%s, %s, %s)",
                    (
                        user_id,
                        question_id,
                        selected_option
                    )
                )
                connection.commit()
            except IntegrityError as exc:
                connection.rollback()
                if exc.errno == errorcode.ER_DUP_ENTRY:
                    raise AnswerAlreadyExistsError("User has already answered this question") from exc
                raise
            finally:
                cursor.close()
        finally:
            connection.close()

        return self.get_answer(user_id, question_id)