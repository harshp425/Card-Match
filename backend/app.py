import json
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))
# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, 'dataset/dataset.json')

app = Flask(__name__)
CORS(app)

# Load JSON data
with open(json_file_path, 'r') as file:
    data = json.load(file)

card_names = []
reviews = []
categories = []
annual_fees = []
foreign_transaction_fees = []  # Changed from bonus_offer_values

for entry in data:
    card_names.append(entry["name"])
    reviews.append(entry.get("our_take_value", ""))
    categories.append(entry.get("category", "N/A"))
    annual_fees.append(entry.get("annual_fee_value", "N/A"))
    foreign_transaction_fees.append(entry.get("foreign_transaction_fee_value", "N/A"))

# Vectorize text for cosine similarity
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(reviews)

def get_recommendations(user_input, offset=0, limit=3):
    """Compute cosine similarity between user input and stored credit card reviews."""
    user_vec = vectorizer.transform([user_input])
    cosine_similarities = cosine_similarity(user_vec, tfidf_matrix).flatten()
    sorted_indices = np.argsort(-cosine_similarities)  # Sort descending
    
    current_indices = sorted_indices[offset:offset+limit]
    
    top_matches = []
    for i in current_indices:
        # Scale cosine similarity to a percentage (0-100)
        similarity_score = float(cosine_similarities[i])
        
        # Convert to percentage without floor
        raw_percentage = similarity_score * 100
        match_percentage = int(min(raw_percentage, 99))
        
        # Include both the raw data and the calculated match percentage
        top_matches.append({
            "title": card_names[i],
            "category": categories[i],
            "annual_fee": annual_fees[i],
            "foreign_transaction_fee_value": foreign_transaction_fees[i],
            "similarity_score": similarity_score,
            "match_percentage": match_percentage
        })
    return top_matches

@app.route("/")
def home():
    return render_template('base2.html', title="Card Match - Credit Card Recommender")

@app.route("/old")
def old_ui():
    return render_template('base.html', title="Card Match - Credit Card Recommender")

@app.route("/new")
def new_ui():
    return render_template('base2.html', title="Card Match - Credit Card Recommender")

@app.route("/recommend", methods=["POST", "GET"])
def recommend():
    """API endpoint to return credit card recommendations."""
    print("got to recommend")
    if request.method == "POST":
        data = request.json
        user_query = data.get("query", "")
        offset = data.get("offset", 0)
        limit = data.get("limit", 3)
    else:
        user_query = request.args.get("title", "")
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 3))
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    user_vec = vectorizer.transform([user_query])
    cosine_similarities = cosine_similarity(user_vec, tfidf_matrix).flatten()
    total_potential_matches = min(len(cosine_similarities), 20)
    
    recommendations = get_recommendations(user_input=user_query, offset=offset, limit=limit)
    
    return jsonify({
        "recommendations": recommendations,
        "pagination": {
            "offset": offset,
            "limit": limit,
            "total": total_potential_matches,
            "has_more": (offset + limit) < total_potential_matches
        }
    })

if __name__ == "__main__":  # This is the correct way to run the app
    app.run(debug=True, host="0.0.0.0", port=5001)