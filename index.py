from fastapi import FastAPI, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Vend-O-Matic")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
    expose_headers=["X-Coins", "X-Inventory-Remaining"],  # Expose custom headers to frontend
)

NUMBER_OF_ITEMS_IN_MACHINE = 12
INITIAL_STOCK_PER_ITEM = 5

# Price per item in quarters
ITEM_PRICES = {
    1: 2,
    2: 3,
    3: 2,
    4: 4,
    5: 2,
    6: 3,
    7: 2,
    8: 5,
    9: 2,
    10: 3,
    11: 2,
    12: 4,
}

class State:
    def __init__(self) -> None:
        self.coins_inserted = 0
        self.inventory = [INITIAL_STOCK_PER_ITEM] * NUMBER_OF_ITEMS_IN_MACHINE

CURRENT_STATE = State()

class InsertedCoin(BaseModel):
    coin: int

# Response Headers: 
    # - X-Coins: $[# of coins accepted]
@app.put("/", status_code=status.HTTP_204_NO_CONTENT)
def insert_coin(body: InsertedCoin, response: Response):
    if body.coin != 1:
        raise HTTPException(status_code=400, detail="Only one quarter may be inserted at a time.")

    CURRENT_STATE.coins_inserted += 1

    response.headers["X-Coins"] = str(CURRENT_STATE.coins_inserted)
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=response.headers)

# Response Headers: 
    # - X-Coins: $[# of coins to be returned]
@app.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def dispense_coins(response: Response):
    inserted_coins = CURRENT_STATE.coins_inserted
    CURRENT_STATE.coins_inserted = 0
    response.headers["X-Coins"] = str(inserted_coins)
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=response.headers)

# Response Body: 
    # - Array of remaining item quantities, (an array of integers)
@app.get("/inventory", status_code=status.HTTP_200_OK)
def inventory():
    return CURRENT_STATE.inventory

# Response Body: 
    # - Remaining item quantity (an integer)
@app.get("/inventory/{item_id}")
def remaining_item_quantity(item_id: int, response: Response):
    index = item_id - 1

    # Invalid item ID
    if index < 0 or index >= NUMBER_OF_ITEMS_IN_MACHINE:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return CURRENT_STATE.inventory[index]

# Response Headers:
    # - X-Coins: X-Coins: $[# of coins to be returned]
    # - X-Inventory-Remaining: $[item quantity]
# Response Body: 
    # - The number of items vended. {"quantity": $[number of items vended]}
@app.put("/inventory/{item_id}", status_code=status.HTTP_200_OK)
def dispense_items(item_id: int, response: Response):
    index = item_id - 1

    # Invalid item ID
    """ 
        Note: 
            The problem statement doesn't explicitly say to return a 404 for an invalid item ID, but it seems reasonable to do so.
            Commenting out in order to adhere strictly to the provided specifications.
            Feel free to uncomment if you think it makes sense to return a 404 for an invalid item ID.
    """
    # if index < 0 or index >= NUMBER_OF_ITEMS_IN_MACHINE:
    #     response.headers["X-Coins"] = str(CURRENT_STATE.coins_inserted)
    #     return Response(status_code=status.HTTP_404_NOT_FOUND, headers=response.headers)

    # Out of stock
    if CURRENT_STATE.inventory[index] <= 0:
        response.headers["X-Coins"] = str(CURRENT_STATE.coins_inserted)
        return Response(status_code=status.HTTP_404_NOT_FOUND, headers=response.headers)

    # Get price for this item
    item_price = ITEM_PRICES.get(item_id, 2)  # Default to 2 quarters if not found

    # Insufficient funds
    if CURRENT_STATE.coins_inserted < item_price:
        response.headers["X-Coins"] = str(CURRENT_STATE.coins_inserted)
        return Response(status_code=status.HTTP_403_FORBIDDEN, headers=response.headers)

    # Dispense
    CURRENT_STATE.inventory[index] -= 1
    change = CURRENT_STATE.coins_inserted - item_price
    CURRENT_STATE.coins_inserted = 0

    response.headers["X-Coins"] = str(change)
    response.headers["X-Inventory-Remaining"] = str(CURRENT_STATE.inventory[index])
    return {"quantity": 1}


# Response Body: 
    # - Array of item prices in quarters
@app.get("/prices", status_code=status.HTTP_200_OK)
def get_prices():
    return ITEM_PRICES


""" 
    Bonus endpoint to check how many coins have been inserted without dispensing an item or returning the coins. 
    This is useful for testing and debugging purposes.
"""
# Response Body: 
    # - {"coins_inserted": $[number of coins currently inserted]}
# @app.get("/coins-inserted")
# def coins_inserted():
#     return {"coins_inserted": CURRENT_STATE.coins_inserted}