# Vend-O-Matic

A simple FastAPI service that simulates a vending machine accepting quarters and dispensing items.

## Requirements
- Python 3.10+
- pip

## Setup (Windows / PowerShell)
```powershell
# From the project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn pydantic
```

## Setup (macOS / Linux)
```bash
# From the project root
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn pydantic
```

## Run (Windows / PowerShell)
```powershell
uvicorn index:app --reload
```
- Server: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Postman Collection

This folder includes a Postman collection file that you can import directly:
- File: Vend-O-Matic.postman_collection.json
- How to import: Open Postman → File → Import → select the file.
- The requests assume the server is running at http://localhost:8000.

## Run (macOS / Linux)
```bash
uvicorn index:app --reload
```

## API

- PUT `/` (Insert Coin)
  - Body: `{ "coin": 1 }` (only one quarter per request)
  - Headers: `X-Coins: <total accepted quarters>`
  - Status: `204 No Content`

- DELETE `/` (Dispense Coins)
  - Headers: `X-Coins: <quarters returned>`
  - Status: `204 No Content`

- GET `/inventory` (All Items)
  - Body: `[<qty_item_1>, <qty_item_2>, <qty_item_3>]`
  - Status: `200 OK`

- GET `/inventory/{item_id}` (Single Item)
  - Body: `{ "quantity": <remaining> }`
  - Status: `200 OK`
  - Errors: `404 Not Found` (invalid item id)

- PUT `/inventory/{item_id}` (Dispense Item)
  - Requires: 2 quarters inserted total
  - Body: `{ "quantity": 1 }` on success
  - Headers: `X-Coins: <quarters returned>`, `X-Inventory-Remaining: <remaining>`
  - Status: `200 OK`
  - Errors:
    - `403 Forbidden` (insufficient funds)
    - `404 Not Found` (invalid item id or out of stock)

- GET `/coins-inserted`
  - Body: `{ "coins_inserted": <current total> }`
  - Status: `200 OK`

Notes:
- `item_id` is 1-based (1..3).
- Initial inventory: 5 per item.

## Quick Examples (Windows / PowerShell)

Insert two quarters and vend item 1:
```powershell
# Insert quarter 1
curl.exe -X PUT "http://localhost:8000/" -H "Content-Type: application/json" -d "{\"coin\":1}"
# Insert quarter 2
curl.exe -X PUT "http://localhost:8000/" -H "Content-Type: application/json" -d "{\"coin\":1}"
# Vend item 1 (shows headers and body)
curl.exe -i -X PUT "http://localhost:8000/inventory/1"
```

Check inventory and single item quantity:
```powershell
curl.exe "http://localhost:8000/inventory"
curl.exe "http://localhost:8000/inventory/1"
```

Return any inserted coins without purchase:
```powershell
curl.exe -i -X DELETE "http://localhost:8000/"
```

## Quick Examples (macOS / Linux)

Insert two quarters and vend item 1:
```bash
# Insert quarter 1
curl -X PUT "http://localhost:8000/" -H "Content-Type: application/json" -d '{"coin":1}'
# Insert quarter 2
curl -X PUT "http://localhost:8000/" -H "Content-Type: application/json" -d '{"coin":1}'
# Vend item 1 (shows headers and body)
curl -i -X PUT "http://localhost:8000/inventory/1"
```

Check inventory and single item quantity:
```bash
curl "http://localhost:8000/inventory"
curl "http://localhost:8000/inventory/1"
```

Return any inserted coins without purchase:
```bash
curl -i -X DELETE "http://localhost:8000/"
```

## Troubleshooting
- If imports fail, run: `pip install fastapi uvicorn pydantic` inside the venv.
- Change port with: `uvicorn index:app --reload --port 8080`.
- If PowerShell aliases conflict, use `curl.exe` instead of `curl`.
- On macOS/Linux, use `python3` and `source .venv/bin/activate`.
