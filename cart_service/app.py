import os
import json
from flask import Flask, jsonify, request
import redis

app = Flask(__name__)

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

@app.route('/health', methods=['GET'])
def health_check():
    try:
        r.ping()
        return jsonify({"status": "healthy", "redis": "connected"}), 200
    except Exception:
        return jsonify({"status": "healthy", "redis": "disconnected"}), 200

@app.route('/api/cart/<user_id>', methods=['GET'])
def get_cart(user_id):
    cart_data = r.get(f"cart:{user_id}")
    cart = json.loads(cart_data) if cart_data else []
    return jsonify({"user_id": user_id, "cart": cart}), 200

@app.route('/api/cart/<user_id>', methods=['POST'])
def add_to_cart(user_id):
    item = request.json
    cart_data = r.get(f"cart:{user_id}")
    cart = json.loads(cart_data) if cart_data else []
    
    found = False
    for i in cart:
        if i['product_id'] == item.get('product_id'):
            i['quantity'] += item.get('quantity', 1)
            found = True
            break
            
    if not found:
        cart.append(item)
        
    r.set(f"cart:{user_id}", json.dumps(cart))
    return jsonify({"message": "Item added", "cart": cart}), 200

@app.route('/api/cart/<user_id>', methods=['DELETE'])
def clear_cart(user_id):
    r.delete(f"cart:{user_id}")
    return jsonify({"message": "Cart cleared"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
