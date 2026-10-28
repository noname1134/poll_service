from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    title: str = Field(min_length=1)
    option_1: str = Field(min_length=1)
    option_2: str = Field(min_length=1)
    option_3: str = Field(min_length=1)
    option_4: str = Field(min_length=1)

class QuestionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    option_1: str | None = Field(default=None, min_length=1)
    option_2: str | None = Field(default=None, min_length=1)
    option_3: str | None = Field(default=None, min_length=1)
    option_4: str | None = Field(default=None, min_length=1)


class QuestionResponse(BaseModel):
    id: int
    title: str = Field(min_length=1)
    option_1: str = Field(min_length=1)
    option_2: str = Field(min_length=1)
    option_3: str = Field(min_length=1)
    option_4: str = Field(min_length=1)


class QuestionStatisticsItem(QuestionResponse):
    option_1_count: int = Field(ge=0)
    option_2_count: int = Field(ge=0)
    option_3_count: int = Field(ge=0)
    option_4_count: int = Field(ge=0)
    total_answers: int = Field(ge=0)


class AnswerCreate(BaseModel):
    user_id: int = Field(gt=0)
    selected_option: int = Field(ge=1, le=4)


class AnswerUpdate(BaseModel):
    selected_option: int = Field(ge=1, le=4)


class AnswerResponse(BaseModel):
    user_id: int
    question_id: int
    selected_option: int = Field(ge=1, le=4)


class QuestionStatisticsResponse(BaseModel):
    question_id: int
    option_counts: dict[int, int]
    total_answers: int


class UserAnswersResponse(BaseModel):
    user_id: int
    answers: list[AnswerResponse]
    total_answers: int