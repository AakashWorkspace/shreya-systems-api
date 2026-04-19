import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, User, Item, Quotation, QuotationItem
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
)

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Shreya Systems Quotation API",
    description="Production-ready quotation management system",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rate: float
    hsn_code: Optional[str] = None
    category: Optional[str] = None


class ItemOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    rate: float
    hsn_code: Optional[str]
    category: Optional[str]

    class Config:
        from_attributes = True


class QuotationItemCreate(BaseModel):
    item_name: str
    description: Optional[str] = None
    hsn_code: Optional[str] = None
    qty: int = 1
    rate: float
    amount: float


class QuotationItemOut(BaseModel):
    id: int
    item_name: str
    description: Optional[str]
    hsn_code: Optional[str]
    qty: int
    rate: float
    amount: float

    class Config:
        from_attributes = True


class QuotationCreate(BaseModel):
    quote_number: str
    date: Optional[datetime] = None
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    client_gstin: Optional[str] = None
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    notes: Optional[str] = None
    tax_inclusive: str = "inclusive"
    total_amount: float = 0.0
    cgst_amount: float = 0.0
    sgst_amount: float = 0.0
    grand_total: float = 0.0
    status: str = "draft"
    items: List[QuotationItemCreate] = []


class QuotationOut(BaseModel):
    id: int
    quote_number: str
    date: datetime
    client_name: Optional[str]
    client_address: Optional[str]
    client_gstin: Optional[str]
    client_phone: Optional[str]
    client_email: Optional[str]
    notes: Optional[str]
    tax_inclusive: str
    total_amount: float
    cgst_amount: float
    sgst_amount: float
    grand_total: float
    status: str
    items: List[QuotationItemOut] = []

    class Config:
        from_attributes = True


# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Shreya Systems API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# ── Auth Routes ───────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=UserOut, tags=["Auth"])
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )
    user = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token, tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@app.get("/auth/me", response_model=UserOut, tags=["Auth"])
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ── Items Routes ──────────────────────────────────────────────────────────────

@app.get("/api/items", response_model=List[ItemOut], tags=["Items"])
def get_items(
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Item)
    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))
    return query.order_by(Item.name).limit(limit).all()


@app.post("/api/items", response_model=ItemOut, tags=["Items"], status_code=201)
def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    existing = db.query(Item).filter(Item.name == item_data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Item with this name already exists")
    item = Item(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.put("/api/items/{item_id}", response_model=ItemOut, tags=["Items"])
def update_item(
    item_id: int,
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for k, v in item_data.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/items/{item_id}", tags=["Items"])
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"detail": "Item deleted"}


# ── Quotations Routes ─────────────────────────────────────────────────────────

@app.get("/api/quotations", response_model=List[QuotationOut], tags=["Quotations"])
def get_quotations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Quotation)
        .filter(Quotation.user_id == current_user.id)
        .order_by(Quotation.date.desc())
        .all()
    )


@app.post("/api/quotations", response_model=QuotationOut, tags=["Quotations"], status_code=201)
def create_quotation(
    quote_data: QuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Quotation).filter(Quotation.quote_number == quote_data.quote_number).first()
    if existing:
        raise HTTPException(status_code=409, detail="Quote number already exists")

    items_data = quote_data.items
    quote_dict = quote_data.model_dump(exclude={"items"})
    if not quote_dict.get("date"):
        quote_dict["date"] = datetime.utcnow()

    quotation = Quotation(**quote_dict, user_id=current_user.id)
    db.add(quotation)
    db.flush()

    for item_data in items_data:
        qi = QuotationItem(**item_data.model_dump(), quotation_id=quotation.id)
        db.add(qi)

    db.commit()
    db.refresh(quotation)
    return quotation


@app.get("/api/quotations/{quote_id}", response_model=QuotationOut, tags=["Quotations"])
def get_quotation(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quote = (
        db.query(Quotation)
        .filter(Quotation.id == quote_id, Quotation.user_id == current_user.id)
        .first()
    )
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quote


@app.delete("/api/quotations/{quote_id}", tags=["Quotations"])
def delete_quotation(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quote = (
        db.query(Quotation)
        .filter(Quotation.id == quote_id, Quotation.user_id == current_user.id)
        .first()
    )
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    db.delete(quote)
    db.commit()
    return {"detail": "Quotation deleted"}
