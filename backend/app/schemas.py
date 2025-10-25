from pydantic import BaseModel, EmailStr
from typing import List

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    role: str = "salesperson"
    store_id: str = ""

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class StoreIn(BaseModel):
    id: str
    name: str
    region: str = ""
    is_active: bool = True

class CartLine(BaseModel):
    product_id: str
    brand: str
    name: str
    unit_price: float
    qty: float

class PaymentIn(BaseModel):
    type: str
    amount: float
    reference: str = ""

class SaleIn(BaseModel):
    store_id: str
    salesperson_id: str
    cart: List[CartLine]
    payments: List[PaymentIn]