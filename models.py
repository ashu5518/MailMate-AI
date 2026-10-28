from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Result(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Reply(Result):
    reply: str = Field(min_length=1, max_length=20000)


class Analysis(Reply):
    summary: str = Field(min_length=1)
    intent: str = Field(min_length=1)
    urgency: Literal["Low", "Medium", "High"]
    urgency_explanation: str = Field(min_length=1)
    action_items: list[str]
    deadline_text: str | None = None
    deadline_evidence: str | None = None

    @model_validator(mode="after")
    def deadline_requires_evidence(self):
        if bool(self.deadline_text) != bool(self.deadline_evidence):
            raise ValueError("Deadline requires both text and evidence")
        return self


class Proofreading(Result):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)
    corrected_text: str = Field(min_length=1, max_length=20000)
    change_explanations: list[str]
