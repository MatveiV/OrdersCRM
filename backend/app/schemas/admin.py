from pydantic import BaseModel, Field
from typing import Optional


class AdminSettingBase(BaseModel):
    service_name: str = Field(..., min_length=1, max_length=200)
    budget_range: Optional[str] = None
    task_type: Optional[str] = None
    product_interest: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class AdminSettingCreate(AdminSettingBase):
    pass


class AdminSettingUpdate(BaseModel):
    service_name: Optional[str] = Field(None, min_length=1, max_length=200)
    budget_range: Optional[str] = None
    task_type: Optional[str] = None
    product_interest: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AdminSettingResponse(AdminSettingBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
