import json
from datetime import datetime, timezone, timedelta
import os

# Load product data
with open(os.path.join(os.path.dirname(__file__), "..", "data", "products.json"), "r") as f:
    PRODUCTS = json.load(f)

# Load order data
with open(os.path.join(os.path.dirname(__file__), "..", "data", "orders.json"), "r") as f:
    ORDERS = json.load(f)


def product_search(query=None, price_max=None, tags=None):
    results = []
    for p in PRODUCTS:
        if price_max and p["price"] > price_max:
            continue
        if tags and not all(tag in p["tags"] for tag in tags):
            continue
        results.append(p)
    return results[:2]  # ≤2 items


def size_recommender(user_inputs):
    if "M" in user_inputs and "L" in user_inputs:
        return "M"  # heuristic
    elif "M" in user_inputs:
        return "M"
    elif "L" in user_inputs:
        return "L"
    else:
        return "M"


def eta(zip_code):
    return "2-5 days"  # simple rule-based for now


def order_lookup(order_id, email):
    for order in ORDERS:
        if order["order_id"] == order_id and order["email"] == email:
            return order
    return None


def order_cancel(order_id, email, timestamp):
    order = order_lookup(order_id, email)
    if not order:
        return {"cancel_allowed": False, "reason": "Order not found"}
    
    created_at = datetime.fromisoformat(order["created_at"].replace("Z", "+00:00"))
    diff = timestamp - created_at

    if diff.total_seconds() <= 3600:
        return {"cancel_allowed": True}
    else:
        return {"cancel_allowed": False, "reason": ">60 min"}
