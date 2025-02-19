# Receipt Processor API

This is a FastAPI-based web service for processing receipts and awarding points based on specific criteria.

## Features
- Submit a receipt and get an ID.
- Retrieve awarded points using the receipt ID.
- Runs locally or via Docker.

---

## Getting Started

### **Clone the Repository**
```sh
git clone https://github.com/clairepare/receipt-processor-challenge.git
```

## Run Locally
### Build the Docker Image
```sh
docker build -t receipt-processor .
```
### Run the Container
```sh
docker run -p 8000:8000 receipt-processor
```

## API Endpoints
### 1. Process a Receipt
Endpoint: POST /receipts/process

Example Receipt:
```json
{
  "retailer": "M&M Corner Market",
  "purchaseDate": "2022-03-20",
  "purchaseTime": "14:33",
  "items": [
    { "shortDescription": "Gatorade", "price": "2.25" }
  ],
  "total": "9.00"
}
```
Example Request:
```sh
curl -X POST "http://localhost:8000/receipts/process" \
     -H "Content-Type: application/json" \
     -d '{
  "retailer": "M&M Corner Market",
  "purchaseDate": "2022-03-20",
  "purchaseTime": "14:33",
  "items": [
    { "shortDescription": "Gatorade", "price": "2.25" }
  ],
  "total": "9.00"
}'
```
Example Response:
```json

{ "id": "adb6b560-0eef-42bc-9d16-df48f30e89b2" }
```
### 2. Get Receipt Points
Endpoint: GET /receipts/{id}/points

Example Request:
```sh
curl -X GET "http://localhost:8000/receipts/7fb1377b-b223-49d9-a31a-5a02701dd310/points"
```
Example Response:
```json
{ "points": 109 }
```

## Development Notes
- Uses in-memory storage (data is lost on restart).
- Follows all API rules, including:
    - +1 point per alphanumeric retailer character.
    - +50 points for round-dollar totals.
    - +25 points for totals multiple of 0.25.
    - +5 points per 2 items.
    - +6 points for odd purchase dates.
    - +10 points for purchases between 2:00 PM - 4:00 PM.
