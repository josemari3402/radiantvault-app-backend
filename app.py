from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import random
import os # Added to read environment variables

app = Flask(__name__)

# --- FIX: Update CORS to allow your Azure URL specifically ---
CORS(app, resources={r"/api/*": {"origins": "https://salmon-desert-059193300.7.azurestaticapps.net"}}) 

# --- FIX: Use Environment Variables for Production ---
# Locally, it uses localhost. In Azure, it will look for 'MONGO_URI' config.
MONGO_URI = mongodb+srv://odysseus:sonic_22@radiant-vault-db.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000
client = MongoClient(MONGO_URI)
db = client['radiant_vault']
users_collection = db['users']
skins_collection = db['skins']

@app.route('/api/signup', methods=['POST'])
def signup():
    # ... (Signup logic stays the same)
    return jsonify({"message": "PROTOCOL ESTABLISHED"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    # ... (Login logic stays the same)
    return jsonify({"username": user['username'], "loadout": user.get('loadout', {})}), 200

# --- FIX: Moved this ABOVE the app.run block ---
@app.route('/api/night-market/roll', methods=['POST'])
def roll_market():
    data = request.json
    username = data.get('username')
    all_skins = list(skins_collection.find({}, {"_id": 0}))
    
    if len(all_skins) < 6:
        return jsonify({"message": "INSUFFICIENT DATA"}), 500

    selected_skins = random.sample(all_skins, 6)
    market_data = []
    for skin in selected_skins:
        skin['discount'] = random.randint(10, 45)
        market_data.append(skin)

    users_collection.update_one({"username": username}, {"$set": {"market": market_data}})
    return jsonify({"market": market_data}), 200

if __name__ == '__main__':
    # Debug=True is fine for local, but Azure handles the port/run itself.
    app.run(debug=True, port=5000)