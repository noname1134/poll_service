from fastapi import APIRouter, HTTPException

from exceptions import QuestionNotFoundError, UserNotFoundError, UserNotRegisteredError, AnswerAlreadyExistsError, UserServiceUnavailableError, AnswerNotFoundError
from schemas import QuestionCreate, QuestionUpdate, QuestionResponse, AnswerCreate, AnswerUpdate, AnswerResponse
from services import QuestionService, AnswerService


router = APIRouter(prefix="/questions")
question_service = QuestionService()
answer_service = AnswerService()


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


@router.post("/{question_id}/answers", response_model=AnswerResponse)
def create_answer(question_id: int, answer: AnswerCreate):
    try:
        return answer_service.create_answer(question_id, answer)
    except (QuestionNotFoundError, UserNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except UserNotRegisteredError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except AnswerAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except UserServiceUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.patch("/{question_id}/answers/{user_id}",response_model=AnswerResponse)
def update_answer(question_id: int, user_id: int, update: AnswerUpdate):
    try:
        return answer_service.update_answer(user_id, question_id, update)
    except (QuestionNotFoundError, UserNotFoundError, AnswerNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except UserNotRegisteredError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except UserServiceUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))