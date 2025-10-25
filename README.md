
# Retail Sales App v3 (Gift Cards + Targets Dashboard)

Generated: 2025-10-25T17:19:01.104176Z

## Backend
- FastAPI, JWT, SQLite default
- New endpoints:
  - Gift Cards: POST /giftcards/create, /giftcards/reload, /giftcards/balance
  - Targets summary: GET /targets/summary?month=YYYY-MM
- Seed: stores, products, campaigns, targets, users

## Frontend
- React + Vite + Tailwind + React Router + Recharts
- Screens: Dashboard (targets), Sales, Gift Cards, Stores

## Run
1) Backend
```
pip install -r backend/requirements.txt
python -c "from app.seed import seed; seed()" -m backend/app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
2) Frontend
```
cd frontend
npm install
npm run dev
```
