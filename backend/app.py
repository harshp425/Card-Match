import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, 'backend/dataset/dataset.json')

app = Flask(__name__)
CORS(app)

# Assuming your JSON data is stored in a file named 'init.json'
with open(json_file_path, 'r') as file:
    data = json.load(file)

card_names = []
for entry in data:
    card_names.append(entry["card_name"])

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

@app.route("/recommend")
def recommend():
    """API endpoint to return credit card recommendations."""
    data = request.json
    user_query = data.get("query", "")
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    recommendations = get_recommendations(user_query)
    
    return jsonify({"recommendations": recommendations})


if 'DB_NAME' not in os.environ: #should this be if __name__ == "__main__" ?
    app.run(debug=True,host="0.0.0.0",port=5000)
