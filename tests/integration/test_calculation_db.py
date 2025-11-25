import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models.calculation import Calculation, OperationType


def test_calculation_persist_and_compute():
    # Use in-memory SQLite for fast integration test
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        calc = Calculation(a=10, b=5, type=OperationType.Add)
        # compute and store
        res = calc.compute()
        assert res == 15
        session.add(calc)
        session.commit()

        # fetch back
        reloaded = session.get(Calculation, calc.id)
        assert reloaded is not None
        assert reloaded.result == pytest.approx(15)
