import json
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, 'dataset/dataset.json')

app = Flask(__name__)
CORS(app)

# Assuming your JSON data is stored in a file named 'init.json'
with open(json_file_path, 'r') as file:
    data = json.load(file)

card_names = []
for entry in data:
    card_names.append(entry["name"])

reviews = []
for entry in data:
    reviews.append(entry.get("our_take_value", ""))

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
        top_matches.append((card_names[i], cosine_similarities[i]))

    return top_matches

@app.route("/")
def home():
    return render_template('base.html',title="sample html")


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
    
    recommendations = get_recommendations(user_query)
    
    # Format recommendations to match the expected frontend structure
    formatted_recommendations = []
    for card_name, similarity in recommendations:
        formatted_recommendations.append({
            "title": card_name,
            "descr": f"Similarity score: {similarity:.2f}",
            "imdb_rating": f"{similarity:.2f}"  # Using similarity as rating for display
        })
    
    return jsonify({"recommendations": formatted_recommendations})


if 'DB_NAME' not in os.environ: #should this be if __name__ == "__main__" ?
    app.run(debug=True,host="0.0.0.0",port=5000)

