from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    quotations = relationship("Quotation", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    rate = Column(Float, nullable=False, default=0.0)
    hsn_code = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quote_number = Column(String(100), unique=True, index=True, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    client_name = Column(String(200), nullable=True)
    client_address = Column(Text, nullable=True)
    client_gstin = Column(String(50), nullable=True)
    client_phone = Column(String(50), nullable=True)
    client_email = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    tax_inclusive = Column(String(10), default="inclusive")
    total_amount = Column(Float, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    status = Column(String(50), default="draft")  # draft, sent, accepted, rejected
    terms_json = Column(Text, nullable=True)       # JSON-encoded custom terms dict

    owner = relationship("User", back_populates="quotations")
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")


class QuotationItem(Base):
    __tablename__ = "quotation_items"

    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=False)
    item_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    hsn_code = Column(String(50), nullable=True)
    qty = Column(Integer, nullable=False, default=1)
    rate = Column(Float, nullable=False, default=0.0)
    amount = Column(Float, nullable=False, default=0.0)

    quotation = relationship("Quotation", back_populates="items")
