from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import random
import os

app = Flask(__name__)

# Allow your specific Azure Static Web App to communicate with this backend
# Allow both your live site AND your local dev server
CORS(app, resources={r"/api/*": {"origins": [
    "https://salmon-desert-059193300.7.azurestaticapps.net", 
    "http://localhost:5173"
]}})

# --- DATABASE CONNECTION ---
# Integrated your Azure Cosmos DB for MongoDB connection string
MONGO_URI = "mongodb+srv://odysseus:sonic_22@radiant-vault-db.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"

client = MongoClient(MONGO_URI)
db = client['radiant_vault']
users_collection = db['users']
skins_collection = db['skins']

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({"username": username}):
        return jsonify({"message": "AGENT ID ALREADY REGISTERED"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "loadout": {},
        "market": []
    })
    return jsonify({"message": "PROTOCOL ESTABLISHED"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({"username": username})
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({
            "username": user['username'],
            "loadout": user.get('loadout', {}),
            "market": user.get('market', [])
        }), 200
    
    return jsonify({"message": "INVALID CREDENTIALS"}), 401

@app.route('/api/save-loadout', methods=['POST'])
def save_loadout():
    data = request.json
    username = data.get('username')
    loadout = data.get('loadout')

    users_collection.update_one(
        {"username": username},
        {"$set": {"loadout": loadout}}
    )
    return jsonify({"message": "LOADOUT SYNCHRONIZED"}), 200

@app.route('/api/night-market/roll', methods=['POST'])
def roll_market():
    data = request.json
    username = data.get('username')

    all_skins = list(skins_collection.find({}, {"_id": 0}))
    
    if len(all_skins) < 6:
        return jsonify({"message": "INSUFFICIENT DATA IN VAULT"}), 500

    selected_skins = random.sample(all_skins, 6)
    market_data = []
    for skin in selected_skins:
        skin['discount'] = random.randint(10, 45)
        market_data.append(skin)

    users_collection.update_one(
        {"username": username},
        {"$set": {"market": market_data}}
    )
    
    return jsonify({"market": market_data}), 200

# app.run MUST stay at the very bottom
if __name__ == '__main__':
    # Azure will ignore debug=True, but it's helpful for your local testing
    app.run(debug=True, port=5000)