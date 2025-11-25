import enum
from sqlalchemy import Column, Integer, Float, Enum as SAEnum
from app.database import Base
from app.operations.calculator_factory import CalculatorFactory


class OperationType(enum.Enum):
    Add = "Add"
    Sub = "Sub"
    Multiply = "Multiply"
    Divide = "Divide"


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(SAEnum(OperationType), nullable=False)
    # store result as optional to allow computing on demand
    result = Column(Float, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Calculation id={self.id} type={self.type} a={self.a} b={self.b} result={self.result}>"

    def compute(self) -> float:
        """Compute the result using the CalculatorFactory and cache it in self.result."""
        op = CalculatorFactory.get(self.type)
        self.result = op.compute(self.a, self.b)
        return self.result
