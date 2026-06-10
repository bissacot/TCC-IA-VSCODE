from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, jsonify

app = Flask(__name__)

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_products.json"
PORT = int(os.getenv("PRODUCT_API_PORT", "5000"))


@app.route("/api/products", methods=["GET"])
def get_products() -> Any:
    with open(DATA_FILE, encoding="utf-8") as handle:
        payload = json.load(handle)
    return jsonify(payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
