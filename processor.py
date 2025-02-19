from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
import re

app = FastAPI()

# In-memory storage for receipts
receipts_db = {}

class Item(BaseModel):
    shortDescription: str
    price: str

class Receipt(BaseModel):
    retailer: str
    purchaseDate: str
    purchaseTime: str
    items: list[Item]
    total: str

def calculate_points(receipt: Receipt) -> int:
    points = 0
    
    #print("Calculating points for receipt...")
    
    # One point for every alphanumeric character in the retailer name
    retailer_points = sum(c.isalnum() for c in receipt.retailer)
    points += retailer_points
    #print(f"Retailer points: {retailer_points}")
    
    total_amount = float(receipt.total)
    
    # 50 points if the total is a round dollar amount with no cents
    if total_amount.is_integer():
        points += 50
        #print("+50 points: Total is a round dollar amount.")
    
    # 25 points if the total is a multiple of 0.25
    if total_amount % 0.25 == 0:
        points += 25
        #print("+25 points: Total is a multiple of 0.25.")
    
    # 5 points for every two items on the receipt
    item_pairs_points = (len(receipt.items) // 2) * 5
    points += item_pairs_points
    #print(f"+{item_pairs_points} points: {len(receipt.items)} items on receipt.")
    
    # Points based on item descriptions
    # If the trimmed length of the item description is a multiple of 3, 
    # multiply the price by `0.2` and round up to the nearest integer.
    for item in receipt.items:
        trimmed_desc = item.shortDescription.strip()
        if len(trimmed_desc) % 3 == 0:
            item_price = float(item.price)
            item_points = -(-item_price * 0.2 // 1)  # Equivalent to math.ceil
            points += item_points
            #print(f"+{item_points} points: '{trimmed_desc}' (len {len(trimmed_desc)}) price {item.price}.")
    
    # 6 points if the day in the purchase date is odd
    purchase_date = datetime.strptime(receipt.purchaseDate, "%Y-%m-%d")
    if purchase_date.day % 2 == 1:
        points += 6
        #print("+6 points: Purchase date is an odd day.")
    
    # 10 points if the time of purchase is after 2:00pm and before 4:00pm
    purchase_time = datetime.strptime(receipt.purchaseTime, "%H:%M")
    if 14 <= purchase_time.hour < 16:
        points += 10
        #print("+10 points: Purchase time is between 2:00pm and 4:00pm.")
    
    #print(f"Total points awarded: {points}")
    return points

'''
### Endpoint: Process Receipts

* Path: `/receipts/process`
* Method: `POST`
* Payload: Receipt JSON
* Response: JSON containing an id for the receipt.
'''

@app.post("/receipts/process")
def process_receipt(receipt: Receipt):
    # generate unique user id, calculate points, store in local db, return JSON with id
    # Example Response:
    # ```json
    # { "id": "7fb1377b-b223-49d9-a31a-5a02701dd310" }
    # ```
    try:
        receipt_id = str(uuid4())
        points = calculate_points(receipt)
        receipts_db[receipt_id] = points
        return {"id": receipt_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid receipt format. Please verify input.")



'''
## Endpoint: Get Points

* Path: `/receipts/{id}/points`
* Method: `GET`
* Response: A JSON object containing the number of points awarded.
'''

@app.get("/receipts/{receipt_id}/points")
def get_points(receipt_id: str):
    # checks if the id is in the receipts database and returns a JSON in the format
    #```json
    # { "points": 32 }
    # ```
    if receipt_id not in receipts_db:
        raise HTTPException(status_code=404, detail="No receipt found for that ID.")
    return {"points": receipts_db[receipt_id]}
