# app/routes/calculations.py

"""
Calculation Routes

This module defines BREAD API endpoints for calculation management.
- Browse: GET /calculations
- Read: GET /calculations/{id}
- Edit: PUT /calculations/{id}
- Add: POST /calculations
- Delete: DELETE /calculations/{id}

All routes require JWT authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.calculation import Calculation, OperationType as ModelOperationType
from app.models import User
from app.schemas.calculation import CalculationCreate, CalculationRead
from app.dependencies import get_current_user

# Create a router for calculation-related endpoints
router = APIRouter(
    prefix="/calculations",
    tags=["calculations"]
)


@router.post("/", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(
    calc_data: CalculationCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a new calculation (requires authentication).
    
    Args:
        calc_data: Calculation data (a, b, type)
        db: Database session dependency
        current_user: Authenticated user from JWT token
        
    Returns:
        CalculationRead: The created calculation with computed result
    """
    # Convert schema OperationType to model OperationType
    model_type = ModelOperationType(calc_data.type.value)
    
    # Create new calculation
    new_calc = Calculation(
        a=calc_data.a,
        b=calc_data.b,
        type=model_type
    )
    
    # Compute the result
    new_calc.compute()
    
    # Add to database
    db.add(new_calc)
    db.commit()
    db.refresh(new_calc)
    
    return new_calc


@router.get("/", response_model=List[CalculationRead])
def browse_calculations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Browse all calculations (paginated, requires authentication).
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session dependency
        current_user: Authenticated user from JWT token
        
    Returns:
        List[CalculationRead]: List of calculations
    """
    calculations = db.query(Calculation).offset(skip).limit(limit).all()
    return calculations


@router.get("/{calculation_id}", response_model=CalculationRead)
def read_calculation(
    calculation_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Read a specific calculation by ID (requires authentication).
    
    Args:
        calculation_id: The calculation's ID
        db: Database session dependency
        current_user: Authenticated user from JWT token
        
    Returns:
        CalculationRead: The calculation details
        
    Raises:
        HTTPException: If calculation not found
    """
    calculation = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    return calculation


@router.put("/{calculation_id}", response_model=CalculationRead)
def edit_calculation(
    calculation_id: int, 
    calc_data: CalculationCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Edit/Update an existing calculation (requires authentication).
    
    Args:
        calculation_id: The calculation's ID
        calc_data: New calculation data (a, b, type)
        db: Database session dependency
        current_user: Authenticated user from JWT token
        
    Returns:
        CalculationRead: The updated calculation with recomputed result
        
    Raises:
        HTTPException: If calculation not found
    """
    calculation = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    # Convert schema OperationType to model OperationType
    model_type = ModelOperationType(calc_data.type.value)
    
    # Update fields
    calculation.a = calc_data.a
    calculation.b = calc_data.b
    calculation.type = model_type
    
    # Recompute the result
    calculation.compute()
    
    db.commit()
    db.refresh(calculation)
    
    return calculation


@router.delete("/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(
    calculation_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a calculation (requires authentication).
    
    Args:
        calculation_id: The calculation's ID
        db: Database session dependency
        current_user: Authenticated user from JWT token
        
    Raises:
        HTTPException: If calculation not found
    """
    calculation = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    db.delete(calculation)
    db.commit()
    
    return None
