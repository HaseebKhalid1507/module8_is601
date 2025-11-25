"""Calculator factory that returns operation handlers.

This adapts the simple function-based operations into small classes with a common
interface so the Calculation model can call compute() uniformly.
"""
from __future__ import annotations
from typing import Protocol
from app.operations import add as op_add, subtract as op_sub, multiply as op_mul, divide as op_div


class Operation(Protocol):
    def compute(self, a: float, b: float) -> float:
        ...


class AddOperation:
    def compute(self, a: float, b: float) -> float:
        return op_add(a, b)


class SubOperation:
    def compute(self, a: float, b: float) -> float:
        return op_sub(a, b)


class MulOperation:
    def compute(self, a: float, b: float) -> float:
        return op_mul(a, b)


class DivOperation:
    def compute(self, a: float, b: float) -> float:
        return op_div(a, b)


class CalculatorFactory:
    """Simple factory returning an Operation instance for a given operation type.

    Accepts either a string ('Add', 'Sub', 'Multiply', 'Divide') or an enum with a
    `.value` attribute.
    """

    _map = {
        "Add": AddOperation,
        "Sub": SubOperation,
        "Multiply": MulOperation,
        "Divide": DivOperation,
    }

    @classmethod
    def get(cls, op_type) -> Operation:
        # Accept enum, str, or objects with .value
        if hasattr(op_type, "value"):
            key = str(op_type.value)
        else:
            key = str(op_type)

        if key not in cls._map:
            raise ValueError(f"Unknown operation type: {key}")

        return cls._map[key]()
