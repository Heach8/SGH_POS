from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="salesperson")
    store_id = Column(String, default="")

class Store(Base):
    __tablename__ = "stores"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    region = Column(String, default="")
    is_active = Column(Boolean, default=True)

class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True)
    sku = Column(String, unique=True, nullable=False)
    brand = Column(String, nullable=False)
    name = Column(String, nullable=False)
    list_price = Column(Numeric(12,2), nullable=False)
    is_active = Column(Boolean, default=True)

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    brand = Column(String, default="")
    product_id = Column(String, default="")
    min_qty = Column(Integer, default=1)
    min_amount = Column(Numeric(12,2), default=0)
    percent = Column(Float, default=0.0)
    amount_off = Column(Numeric(12,2), default=0)
    start_date = Column(String, default="")
    end_date = Column(String, default="")
    is_active = Column(Boolean, default=True)

class GiftCard(Base):
    __tablename__ = "giftcards"
    id = Column(String, primary_key=True)
    card_number = Column(String, unique=True, nullable=False)
    balance = Column(Numeric(12,2), default=0)
    status = Column(String, default="Active")
    customer_name = Column(String, default="")
    created_date = Column(String, default="")
    last_used_date = Column(String, default="")

class GiftCardTxn(Base):
    __tablename__ = "giftcard_txn"
    id = Column(String, primary_key=True)
    giftcard_id = Column(String, ForeignKey("giftcards.id"))
    txn_type = Column(String)  # Sale/Use/Reload
    amount = Column(Numeric(12,2), default=0)
    date = Column(String, default="")
    sale_id = Column(String, default="")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(String, primary_key=True)
    store_id = Column(String, ForeignKey("stores.id"))
    salesperson_id = Column(String, default="")
    date = Column(String, default="")
    gross_total = Column(Numeric(12,2), default=0)
    discount_total = Column(Numeric(12,2), default=0)
    net_total = Column(Numeric(12,2), default=0)
    status = Column(String, default="Completed")

class SaleLine(Base):
    __tablename__ = "sale_lines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(String, ForeignKey("sales.id"))
    product_id = Column(String, ForeignKey("products.id"))
    qty = Column(Numeric(12,2), default=1)
    unit_price = Column(Numeric(12,2), default=0)
    line_amount = Column(Numeric(12,2), default=0)
    applied_campaign_id = Column(String, default="")
    discount_amount = Column(Numeric(12,2), default=0)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(String, ForeignKey("sales.id"))
    type = Column(String)
    amount = Column(Numeric(12,2), default=0)
    reference = Column(String, default="")

class Target(Base):
    __tablename__ = "targets"
    id = Column(String, primary_key=True)  # e.g., TGT-2025-10-STR-001
    target_type = Column(String)  # 'store' or 'staff'
    target_id = Column(String)    # StoreID or StaffID
    month = Column(String)        # 'YYYY-MM'
    target_amount = Column(Numeric(12,2), default=0)