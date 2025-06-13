from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

@dataclass
class User:
    first_name: str
    last_name: Optional[str]
    rut: str
    address: str
    region: str
    commune: str
    phones: Optional[str]
    gender: Optional[str]
    annual_payment: bool
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    type_payment_source: str  # Manual, Transferencia, PAT, MercadoPago, Transbank, Stripe
    source: Optional[str]
    amount: float
    plan_name: str
    es_empresa: bool
    email: str
    advisor_full_name: Optional[str]
    advisor_email: Optional[str]
    advisor_phone: Optional[str]
    created_at: str  # ISO format datetime string
    updated_at: Optional[str]  # ISO format datetime string

    @classmethod
    def from_model(cls, model: 'UserModel') -> 'User':
        return cls(
            first_name=model.first_name,
            last_name=model.last_name,
            rut=model.rut,
            address=model.address,
            region=model.region,
            commune=model.commune,
            phones=model.phones,
            gender=model.gender,
            annual_payment=model.annual_payment,
            start_date=model.start_date,
            end_date=model.end_date,
            type_payment_source=model.type_payment_source,
            source=model.source,
            amount=model.amount,
            plan_name=model.plan_name,
            es_empresa=model.es_empresa,
            email=model.email,
            advisor_full_name=model.advisor_full_name,
            advisor_email=model.advisor_email,
            advisor_phone=model.advisor_phone,
            created_at=model.created_at.isoformat(),
            updated_at=model.updated_at.isoformat() if model.updated_at else None
        )

class UserModel(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    rut: str
    address: str
    region: str
    commune: str
    phones: Optional[str] = None
    gender: Optional[str] = None
    annual_payment: bool
    start_date: str
    end_date: str
    type_payment_source: str
    source: Optional[str] = None
    amount: float
    plan_name: str
    es_empresa: bool
    email: str
    advisor_full_name: Optional[str] = None
    advisor_email: Optional[str] = None
    advisor_phone: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }