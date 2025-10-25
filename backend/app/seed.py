from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from . import models
from .auth import hash_password

def seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Stores
    for s in [models.Store(id="STR-001", name="Ankara Kızılay", region="IC ANADOLU"),
              models.Store(id="STR-002", name="İzmir Alsancak", region="EGE")]:
        if not db.query(models.Store).filter_by(id=s.id).first(): db.add(s)

    # Products
    for p in [models.Product(id="PRD-100", sku="RB-3025", brand="Ray-Ban", name="Aviator 58mm", list_price=5690.00),
              models.Product(id="PRD-101", sku="PL-0001", brand="Polaroid", name="PLD 101", list_price=1890.00)]:
        if not db.query(models.Product).filter_by(id=p.id).first(): db.add(p)

    # Campaigns
    for c in [models.Campaign(id="CMP-001", name="Brand 10% Ray-Ban", type="PercentOff", brand="Ray-Ban", percent=10.0, min_qty=1),
              models.Campaign(id="CMP-002", name="Buy 3 Pay 2", type="BuyXPayY", min_qty=3)]:
        if not db.query(models.Campaign).filter_by(id=c.id).first(): db.add(c)

    # Targets (store-level sample)
    for t in [models.Target(id="TGT-2025-10-STR-001", target_type="store", target_id="STR-001", month="2025-10", target_amount=600000),
              models.Target(id="TGT-2025-10-STR-002", target_type="store", target_id="STR-002", month="2025-10", target_amount=450000)]:
        if not db.query(models.Target).filter_by(id=t.id).first(): db.add(t)

    # Users
    if not db.query(models.User).filter_by(email="admin@retail.com").first():
        db.add(models.User(email="admin@retail.com", password_hash=hash_password("Admin123!"), role="admin", store_id=""))
    if not db.query(models.User).filter_by(email="manager@retail.com").first():
        db.add(models.User(email="manager@retail.com", password_hash=hash_password("Manager123!"), role="manager", store_id="STR-001"))
    if not db.query(models.User).filter_by(email="sales@retail.com").first():
        db.add(models.User(email="sales@retail.com", password_hash=hash_password("Sales123!"), role="salesperson", store_id="STR-001"))

    db.commit(); db.close()

if __name__ == "__main__":
    seed()