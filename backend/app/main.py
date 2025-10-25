from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal
from typing import List
from .settings import settings
from .database import Base, engine, SessionLocal
from . import models
from .schemas import RegisterIn, LoginIn, StoreIn, CartLine, PaymentIn, SaleIn
from .auth import get_db, hash_password, verify_password, create_token, current_user, require_role
from .utils import apply_campaigns, xml_for_sale

app = FastAPI(title=settings.APP_NAME)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health(): return {"status":"ok"}

# -------- Auth --------
@app.post("/auth/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email=body.email).first(): raise HTTPException(400, "Email already registered")
    user = models.User(email=body.email, password_hash=hash_password(body.password), role=body.role, store_id=body.store_id)
    db.add(user); db.commit(); db.refresh(user)
    return {"ok": True, "user": {"id": user.id, "email": user.email, "role": user.role, "store_id": user.store_id}}

@app.post("/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=body.email).first()
    if not user or not verify_password(body.password, user.password_hash): raise HTTPException(401, "Invalid credentials")
    token = create_token({"uid": user.id, "role": user.role, "store_id": user.store_id})
    return {"token": token, "user": {"id": user.id, "email": user.email, "role": user.role, "store_id": user.store_id}}

# -------- Stores --------
@app.post("/stores")
def create_store(body: StoreIn, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    if db.query(models.Store).filter_by(id=body.id).first(): raise HTTPException(400, "Store ID exists")
    s = models.Store(id=body.id, name=body.name, region=body.region, is_active=body.is_active); db.add(s); db.commit(); return {"ok": True}

@app.get("/stores")
def list_stores(user=Depends(require_role("admin","manager")), db: Session = Depends(get_db)):
    return db.query(models.Store).all()

# -------- Products & Campaigns --------
@app.get("/products")
def products(user=Depends(current_user), db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.is_active==True).all()

@app.get("/campaigns")
def campaigns(user=Depends(current_user), db: Session = Depends(get_db)):
    return [{"id":c.id,"name":c.name,"type":c.type,"brand":c.brand,"product_id":c.product_id,"min_qty":c.min_qty,"min_amount":float(c.min_amount or 0),"percent":c.percent,"amount_off":float(c.amount_off or 0)}
            for c in db.query(models.Campaign).filter(models.Campaign.is_active==True).all()]

@app.post("/cart/price")
def cart_price(cart: List[CartLine], user=Depends(current_user), db: Session = Depends(get_db)):
    campaigns = [{"id":c.id,"type":c.type,"brand":c.brand or "","product_id":c.product_id or "","min_qty":c.min_qty or 1,"min_amount": float(c.min_amount or 0),"percent": c.percent or 0.0,"amount_off": float(c.amount_off or 0),"is_active": c.is_active}
                 for c in db.query(models.Campaign).filter(models.Campaign.is_active==True).all()]
    lines, gross, disc, net = apply_campaigns([l.model_dump() for l in cart], campaigns)
    return {"gross_total": gross, "discount_total": disc, "net_total": net, "lines": lines}

# -------- Gift Cards --------
@app.post("/giftcards/create")
def create_giftcard(body: dict, user=Depends(require_role("admin","manager","salesperson")), db: Session = Depends(get_db)):
    card_number = body.get("card_number"); initial_balance = Decimal(str(body.get("initial_balance",0))); customer_name = body.get("customer_name","")
    if db.query(models.GiftCard).filter_by(card_number=card_number).first(): raise HTTPException(400, "Card number exists")
    gc = models.GiftCard(id=f"GC-{int(datetime.utcnow().timestamp())}", card_number=card_number, balance=initial_balance, status="Active", customer_name=customer_name, created_date=datetime.utcnow().isoformat())
    db.add(gc); db.commit(); return {"ok": True, "card_number": card_number, "balance": float(initial_balance)}

@app.post("/giftcards/reload")
def reload_giftcard(body: dict, user=Depends(require_role("admin","manager","salesperson")), db: Session = Depends(get_db)):
    card_number = body.get("card_number"); amount = Decimal(str(body.get("amount",0)))
    gc = db.query(models.GiftCard).filter_by(card_number=card_number, status="Active").first()
    if not gc: raise HTTPException(404, "Gift card not found or inactive")
    gc.balance = Decimal(gc.balance) + amount; db.add(gc); db.commit(); return {"ok": True, "balance": float(gc.balance)}

@app.post("/giftcards/balance")
def balance_giftcard(body: dict, user=Depends(require_role("admin","manager","salesperson")), db: Session = Depends(get_db)):
    card_number = body.get("card_number")
    gc = db.query(models.GiftCard).filter_by(card_number=card_number).first()
    if not gc: raise HTTPException(404, "Gift card not found")
    return {"card_number": gc.card_number, "balance": float(gc.balance), "status": gc.status}

# -------- Sales --------
@app.post("/sales")
def create_sale(body: SaleIn, user=Depends(current_user), db: Session = Depends(get_db)):
    campaigns = [{"id":c.id,"type":c.type,"brand":c.brand or "","product_id":c.product_id or "","min_qty":c.min_qty or 1,"min_amount": float(c.min_amount or 0),"percent": c.percent or 0.0,"amount_off": float(c.amount_off or 0),"is_active": c.is_active}
                 for c in db.query(models.Campaign).filter(models.Campaign.is_active==True).all()]
    lines, gross, disc, net = apply_campaigns([c.model_dump() for c in body.cart], campaigns)
    pay_sum = round(sum([p.amount for p in body.payments]),2)
    if pay_sum != round(net,2): raise HTTPException(400, f"Payment total ({pay_sum}) must equal net total ({net})")

    sale_id = f"SALE-{int(datetime.utcnow().timestamp())}"
    sale = models.Sale(id=sale_id, store_id=body.store_id, salesperson_id=body.salesperson_id, date=datetime.utcnow().isoformat(),
                       gross_total=gross, discount_total=disc, net_total=net, status="Completed")
    db.add(sale); db.commit()
    for ln in lines:
        db.add(models.SaleLine(sale_id=sale_id, product_id=ln["product_id"], qty=ln["qty"], unit_price=ln["unit_price"], line_amount=ln["line_net"], applied_campaign_id=ln.get("applied_campaign_id",""), discount_amount=ln["discount"]))
    db.commit()
    for p in body.payments: db.add(models.Payment(sale_id=sale_id, type=p.type, amount=p.amount, reference=p.reference))
    db.commit()
    return {"ok": True, "sale_id": sale_id, "totals": {"gross":gross, "discount":disc, "net":net}}

@app.get("/sales/{sale_id}/xml")
def sale_xml(sale_id: str, user=Depends(current_user), db: Session = Depends(get_db)):
    sale = db.query(models.Sale).filter_by(id=sale_id).first()
    if not sale: raise HTTPException(404, "Sale not found")
    lines = db.query(models.SaleLine).filter_by(sale_id=sale_id).all()
    pays = db.query(models.Payment).filter_by(sale_id=sale_id).all()
    sale_dict = {"id": sale.id, "store_id": sale.store_id, "salesperson_id": sale.salesperson_id, "date": sale.date, "gross_total": float(sale.gross_total), "discount_total": float(sale.discount_total), "net_total": float(sale.net_total)}
    ln_list = [{"id": l.id, "product_id": l.product_id, "qty": float(l.qty), "unit_price": float(l.unit_price), "line_amount": float(l.line_amount), "applied_campaign_id": l.applied_campaign_id, "discount_amount": float(l.discount_amount)} for l in lines]
    pay_list = [{"type": p.type, "amount": float(p.amount), "reference": p.reference} for p in pays]
    xml_bytes = xml_for_sale(sale_dict, ln_list, pay_list)
    return {"xml": xml_bytes.decode("utf-8")}

# -------- Targets Summary --------
@app.get("/targets/summary")
def targets_summary(month: str, user=Depends(require_role("admin","manager","salesperson")), db: Session = Depends(get_db)):
    # compute actuals from sales by month prefix
    q = db.query(models.Sale).filter(models.Sale.date.like(f"{month}%"))
    store_actuals = {}
    for s in q:
        store_actuals[s.store_id] = float(store_actuals.get(s.store_id, 0) + float(s.net_total))

    # gather targets relevant to role
    tquery = db.query(models.Target).filter(models.Target.month==month)
    if user.role == "manager" and user.store_id:
        tquery = tquery.filter(models.Target.target_type=="store", models.Target.target_id==user.store_id)
    # salesperson → show only self? We'll map salesperson id to user.id (demo)
    if user.role == "salesperson":
        tquery = tquery.filter(models.Target.target_type=="staff", models.Target.target_id==str(user.id))

    items = []
    for t in tquery:
        actual = 0.0
        if t.target_type == "store":
            actual = float(store_actuals.get(t.target_id, 0.0))
        # for staff, demo keeps 0 unless you map sales table with salesperson_id == target_id
        items.append({
            "id": t.id,
            "type": t.target_type,
            "target_id": t.target_id,
            "month": t.month,
            "target_amount": float(t.target_amount),
            "actual_amount": actual,
            "ach_rate": round((actual / float(t.target_amount) * 100),2) if float(t.target_amount)>0 else 0.0
        })
    return {"month": month, "items": items}

from app import auth
app.include_router(auth.router)
