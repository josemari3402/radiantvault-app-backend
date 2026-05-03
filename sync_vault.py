import requests
from pymongo import MongoClient

# Integrated your Azure Cosmos DB for MongoDB connection string
MONGO_URI = "mongodb+srv://odysseus:sonic_22@radiant-vault-db.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"

def run_sync():
    try:
        client = MongoClient(MONGO_URI)
        db = client['radiant_vault']
        skins_collection = db['skins']

        print("--- CONNECTING TO VALORANT API ---")
        response = requests.get('https://valorant-api.com/v1/weapons/skins')
        all_api_data = response.json()['data']

        print(f"FOUND {len(all_api_data)} TOTAL ASSETS.")

        # 1. Filter out 'Standard' and 'Favorite' skins
        raw_skins = [s for s in all_api_data if "Standard" not in s['displayName'] and "Favorite" not in s['displayName']]

        # 2. DATA CLEANING: Fix the "Gray X" / Missing Image issue
        processed_skins = []
        for skin in raw_skins:
            # Check if the main icon is missing
            if not skin.get('displayIcon') or skin.get('displayIcon') == "":
                # Reach into the chromas (variants) to find the default image[cite: 1]
                if skin.get('chromas') and len(skin['chromas']) > 0:
                    # Sovereign and Prime usually store the icon here
                    fallback_icon = skin['chromas'][0].get('fullRender') or skin['chromas'][0].get('displayIcon')
                    skin['displayIcon'] = fallback_icon
            
            processed_skins.append(skin)

        # 3. Clean the collection to avoid duplicates
        skins_collection.delete_many({})

        # 4. Insert the cleaned data into your database
        if processed_skins:
            skins_collection.insert_many(processed_skins)
            print(f"SUCCESS: {len(processed_skins)} CLEANED SKINS STORED IN RADIANT VAULT.")
        
    except Exception as e:
        print(f"CRITICAL FAILURE: {e}")

if __name__ == "__main__":
    run_sync()