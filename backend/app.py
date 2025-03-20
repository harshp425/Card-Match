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
    foreign_transaction_fees.append(entry.get("foreign_transaction_fee_value", "N/A"))  # Changed field

# Vectorize text for cosine similarity
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(reviews)

def get_recommendations(user_input):
    """Compute cosine similarity between user input and stored credit card reviews."""
    user_vec = vectorizer.transform([user_input])
    cosine_similarities = cosine_similarity(user_vec, tfidf_matrix).flatten()
    sorted_indices = np.argsort(-cosine_similarities)  # Sort descending
    top_matches = []
    for i in sorted_indices[:3]:
        top_matches.append((card_names[i], categories[i], annual_fees[i], foreign_transaction_fees[i]))
    return top_matches

@app.route("/")
def home():
    return render_template('base.html', title="Card Match - Credit Card Recommender")

@app.route("/recommend", methods=["POST", "GET"])
def recommend():
    """API endpoint to return credit card recommendations."""
    print("got to recommend")
    # Handle both GET and POST requests
    if request.method == "POST":
        data = request.json
        user_query = data.get("query", "")
    else:  # GET request
        user_query = request.args.get("title", "")
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    recommendations = get_recommendations(user_input=user_query)
    
    # Format recommendations to match the expected frontend structure
    formatted_recommendations = []
    for card_name, category, annual_fee, foreign_transaction_fee in recommendations:
        formatted_recommendations.append({
            "title": card_name,
            "category": category,
            "annual_fee": annual_fee,
            "foreign_transaction_fee_value": foreign_transaction_fee  # Match the frontend template
        })
    
    return jsonify({"recommendations": formatted_recommendations})

if __name__ == "__main__":  # This is the correct way to run the app
    app.run(debug=True, host="0.0.0.0", port=5000)