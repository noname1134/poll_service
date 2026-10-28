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