"""
Schemas for User.
"""
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    """Base schema for User."""
    email: EmailStr
    full_name: str
    current_position: Optional[str] = None
    department: Optional[str] = None
    years_experience: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new User."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a User."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    current_position: Optional[str] = None
    department: Optional[str] = None
    years_experience: Optional[str] = None


class UserResponse(UserBase):
    """Schema for User response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
