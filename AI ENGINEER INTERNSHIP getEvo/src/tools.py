import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Load data
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')

with open(PRODUCTS_FILE, 'r') as f:
    products = json.load(f)

with open(ORDERS_FILE, 'r') as f:
    orders = json.load(f)

def product_search(query: str, price_max: int, tags: List[str]) -> List[Dict[str, Any]]:
    """Search for products matching query, under price_max, with given tags."""
    results = []
    for product in products:
        if product['price'] > price_max:
            continue
        if tags and not any(tag in product['tags'] for tag in tags):
            continue
        if query.lower() in product['title'].lower() or any(query.lower() in tag for tag in product['tags']):
            results.append(product)
    # Return up to 2 products
    return results[:2]

def size_recommender(user_inputs: str) -> str:
    """Recommend size based on user inputs. Simple heuristic."""
    inputs_lower = user_inputs.lower()
    if 'between m/l' in inputs_lower or 'm or l' in inputs_lower:
        return 'M'  # Default to M
    elif 'small' in inputs_lower or 'xs' in inputs_lower or 's' in inputs_lower:
        return 'S'
    elif 'large' in inputs_lower or 'l' in inputs_lower:
        return 'L'
    else:
        return 'M'  # Default

def eta(zip_code: str) -> str:
    """Return ETA based on zip code. Rule-based."""
    if zip_code.startswith('5'):
        return '2-5 days'
    else:
        return '3-7 days'

def order_lookup(order_id: str, email: str) -> Optional[Dict[str, Any]]:
    """Lookup order by order_id and email."""
    for order in orders:
        if order['order_id'] == order_id and order['email'] == email:
            return order
    return None

def order_cancel(order_id: str, email: str, timestamp: str) -> Dict[str, Any]:
    """Cancel order if within 60 minutes of created_at."""
    order = order_lookup(order_id, timestamp.split()[0])
    for order in orders:
        if order['order_id'] == order_id:
            created_at = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00'))
            current_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if timestamp else datetime.now()
            time_diff = current_time - created_at
            if time_diff <= timedelta(minutes=60):
                return {'cancel_allowed': True, 'message': 'Order cancelled successfully.'}
            else:
                return {'cancel_allowed': False, 'reason': f'Order created {time_diff.total_seconds() / 60:.0f} minutes ago, exceeds 60-minute limit.'}
    return {'cancel_allowed': False, 'reason': 'Order not found.'}