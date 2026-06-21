from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/products")
def products():
    sample = [
        {"product_id": "P1", "name": "Widget A", "category": "Widgets", "price": 10.0},
        {"product_id": "P2", "name": "Widget B", "category": "Widgets", "price": 15.0},
        {"product_id": "P3", "name": "Gadget X", "category": "Gadgets", "price": 25.0},
    ]
    return jsonify(sample)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
