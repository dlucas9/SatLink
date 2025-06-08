#!/usr/bin/env python3
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def test():
    return jsonify({"message": "Test API is working!"})

if __name__ == '__main__':
    print("Starting test Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
