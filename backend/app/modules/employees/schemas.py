from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None


class EmployeeResponse(BaseModel):
    id: str
    business_id: str
    employee_id: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
