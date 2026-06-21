from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/products", methods=["GET"])
def get_products():
    data = [
        {"product_id": "P001", "product_name": "UltraWidget", "category": "Widgets", "unit_price": 19.99},
        {"product_id": "P002", "product_name": "MegaGadget", "category": "Gadgets", "unit_price": 29.99},
        {"product_id": "P003", "product_name": "PowerTool", "category": "Tools", "unit_price": 49.99},
        {"product_id": "P004", "product_name": "SmartDevice", "category": "Devices", "unit_price": 99.99},
        {"product_id": "P005", "product_name": "ClearanceItem", "category": "Accessories", "unit_price": 9.99},
    ]
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
