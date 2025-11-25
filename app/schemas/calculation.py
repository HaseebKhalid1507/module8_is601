from pydantic import BaseModel, Field, model_validator, ConfigDict
from enum import Enum
from typing import Optional


class OperationType(str, Enum):
    Add = "Add"
    Sub = "Sub"
    Multiply = "Multiply"
    Divide = "Divide"


class CalculationCreate(BaseModel):
    a: float = Field(...)
    b: float = Field(...)
    type: OperationType = Field(...)

    @model_validator(mode="after")
    def no_zero_divisor(self):
        if self.type == OperationType.Divide and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self



class CalculationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    a: float
    b: float
    type: OperationType
    result: Optional[float] = None
