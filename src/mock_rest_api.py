from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)

# In-memory data store
products = {
    "1": {"id": "1", "name": "Laptop", "price": 1200.00, "stock": 10},
    "2": {"id": "2", "name": "Mouse", "price": 25.00, "stock": 50},
    "3": {"id": "3", "name": "Keyboard", "price": 75.00, "stock": 30},
}

orders = {
    # order_id: {order_details}
    "1": {"id": "1", "product_id": "1", "product_name": "Laptop", "quantity": 2, "total_price": 2400.00, "status": "pending"},
    "2": {"id": "2", "product_id": "2", "product_name": "Mouse", "quantity": 1, "total_price": 25.00, "status": "shipped"},     
}

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(list(products.values()))

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product = products.get(product_id)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route('/orders', methods=['GET'])
def get_orders():
    return jsonify(list(orders.values()))

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({"error": "Missing product_id or quantity"}), 400

    product_id = data['product_id']
    quantity = data['quantity']

    product = products.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if product['stock'] < quantity:
        return jsonify({"error": f"Not enough stock for product {product['name']}. Available: {product['stock']}"}), 400

    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "product_id": product_id,
        "product_name": product['name'],
        "quantity": quantity,
        "total_price": product['price'] * quantity,
        "status": "pending"
    }
    orders[order_id] = order
    product['stock'] -= quantity # Deduct stock
    return jsonify(order), 201

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.get(order_id)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
