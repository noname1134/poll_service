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