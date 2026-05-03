from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import random

app = Flask(__name__)
CORS(app) 

# --- 1. CRITICAL FIX: CONNECTION STRING ---
# MongoClient needs a MongoDB URI (mongodb+srv:// or mongodb://), 
# NOT an Azure Static Web App URL. 
# Replace 'YOUR_MONGODB_URI' with your actual connection string.
MONGO_URI = 'mongodb://localhost:27017' # For local dev
client = MongoClient(MONGO_URI)
db = client['radiant_vault']
users_collection = db['users']
skins_collection = db['skins'] # Assumed collection for Night Market logic

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({"username": username}):
        return jsonify({"message": "AGENT ID ALREADY REGISTERED"}), 400

    # Scramble the password before storing
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "loadout": {},
        "market": [] # Initialize empty market
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

# --- 2. NIGHT MARKET LOGIC ---
@app.route('/api/night-market/roll', methods=['POST'])
def roll_market():
    data = request.json
    username = data.get('username')

    # 1. Fetch all available skins from the DB
    all_skins = list(skins_collection.find({}, {"_id": 0}))
    
    if len(all_skins) < 6:
        return jsonify({"message": "INSUFFICIENT DATA IN VAULT"}), 500

    # 2. Pick 6 random skins
    selected_skins = random.sample(all_skins, 6)

    # 3. Assign random discounts
    market_data = []
    for skin in selected_skins:
        discount = random.randint(10, 45)
        skin['discount'] = discount
        market_data.append(skin)

    # 4. Save to user's document
    users_collection.update_one(
        {"username": username},
        {"$set": {"market": market_data}}
    )
    
    return jsonify({"market": market_data}), 200

# --- 3. FIX: ROUTE ORDER ---
# app.run must be the VERY LAST thing in your script.
if __name__ == '__main__':
    app.run(debug=True, port=5000)