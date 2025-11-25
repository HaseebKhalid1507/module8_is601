import pytest

from app.operations.calculator_factory import CalculatorFactory
from app.schemas.calculation import CalculationCreate, OperationType


def test_factory_add():
    op = CalculatorFactory.get("Add")
    assert op.compute(2, 3) == pytest.approx(5)


def test_factory_sub():
    op = CalculatorFactory.get(OperationType.Sub)
    assert op.compute(5, 2) == pytest.approx(3)


def test_factory_mul():
    op = CalculatorFactory.get("Multiply")
    assert op.compute(3, 4) == pytest.approx(12)


def test_factory_div():
    op = CalculatorFactory.get("Divide")
    assert op.compute(7, 2) == pytest.approx(3.5)


def test_invalid_type_raises():
    with pytest.raises(ValueError):
        CalculatorFactory.get("NotAnOp")


def test_schema_divide_by_zero_validation():
    # Should raise on creating a CalculationCreate with Divide and b == 0
    with pytest.raises(Exception):
        CalculationCreate(a=1, b=0, type=OperationType.Divide)
