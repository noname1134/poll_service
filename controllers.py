from fastapi import APIRouter, HTTPException

from schemas import QuestionCreate, QuestionUpdate, QuestionResponse
from services import QuestionService


router = APIRouter(prefix="/questions")
question_service = QuestionService()


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int):
    res = question_service.get_question(question_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return res


@router.post("", response_model=QuestionResponse)
def create_question(question: QuestionCreate):
    return question_service.create_question(question)


@router.patch("/{question_id}", response_model=QuestionResponse)
def update_question(question_id: int, question: QuestionUpdate):
    try:
        res = question_service.update_question(question_id, question)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    if res is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return res


@router.delete("/{question_id}")
def delete_question(question_id: int):
    if question_service.delete_question(question_id) is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted"}

