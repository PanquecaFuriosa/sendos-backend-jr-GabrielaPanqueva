"""
Schemas para User.
"""
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    """Base schema para User."""
    email: EmailStr
    full_name: str
    current_position: Optional[str] = None
    department: Optional[str] = None
    years_experience: Optional[str] = None


class UserCreate(UserBase):
    """Schema para crear un nuevo User."""
    pass


class UserUpdate(BaseModel):
    """Schema para actualizar un User."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    current_position: Optional[str] = None
    department: Optional[str] = None
    years_experience: Optional[str] = None


class UserResponse(UserBase):
    """Schema para la respuesta de User."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
