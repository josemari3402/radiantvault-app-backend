from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
CORS(app) # Gives React permission to talk to Python

# Connect to the local Vault
client = MongoClient('https://salmon-desert-059193300.7.azurestaticapps.net')
db = client['radiant_vault']
users_collection = db['users']

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({"username": username}):
        return jsonify({"message": "AGENT ID ALREADY REGISTERED"}), 400

    # Scramble the password before storing[cite: 2]
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "loadout": {}
    })
    return jsonify({"message": "PROTOCOL ESTABLISHED"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({"username": username})
    
    # Check if agent exists and password matches[cite: 2]
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({
            "username": user['username'],
            "loadout": user.get('loadout', {})
        }), 200
    
    return jsonify({"message": "INVALID CREDENTIALS"}), 401

@app.route('/api/save-loadout', methods=['POST'])
def save_loadout():
    data = request.json
    username = data.get('username')
    loadout = data.get('loadout')

    # This updates the specific agent's loadout in the Vault
    users_collection.update_one(
        {"username": username},
        {"$set": {"loadout": loadout}}
    )
    return jsonify({"message": "LOADOUT SYNCHRONIZED"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)

@app.route('/api/night-market/roll', methods=['POST'])
def roll_market():
    # 1. Get user from DB
    # 2. Pick 6 random skins from your 'skins' collection
    # 3. Assign each a random discount (e.g., 10% to 45%)
    # 4. Save this 'market' array to the user's document
    return jsonify({"market": market_data})