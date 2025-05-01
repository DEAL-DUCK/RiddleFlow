from pydantic import BaseModel, ConfigDict


class CreateTestSchema(BaseModel):
    input: str
    expected_output: str
    is_public: bool


class TestSchema(BaseModel):
    id: int
    input: str
    expected_output: str
    is_public: bool
    model_config = ConfigDict(from_attributes=True)


class TestUpdateSchema(BaseModel):
    input: str | None = None
    expected_output: str | None = None
    is_public: bool | None = None
