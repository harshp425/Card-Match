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
foreign_transaction_fees = []
min_credit_scores = []
issuer = []
user_reviews = []


for entry in data:
    card_names.append(entry["name"])
    reviews.append(entry.get("our_take_value", ""))
    categories.append(entry.get("category", ""))
    annual_fees.append(entry.get("annual_fee_value", "N/A"))
    foreign_transaction_fees.append(entry.get("foreign_transaction_fee_value", "N/A"))
    min_credit_scores.append(entry.get("credit_score_low", "N/A"))
    issuer.append(entry.get("issuer", ""))
    user_reviews.append("     ".join(entry.get("user_reviews", [])))

# Add the name of the issuer to the reviews to create an informed_description of the card against which we will
# perform cosine similarity 

informed_description = []
for i in range(len(reviews)):
    informed_description.append(reviews[i] + " issuer: " + issuer[i] + " category: " + categories[i])

# Vectorize text for cosine similarity
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(informed_description)

user_review_vectorizer = TfidfVectorizer(stop_words="english")
user_review_matrix = user_review_vectorizer.fit_transform(user_reviews)

def filter_by_credit_score(recommendations, credit_score):
    """
    Filter recommendations based on user's credit score.
    Include cards where the user's minimum credit score meets or exceeds the card's requirement.
    """
    if not credit_score or credit_score == "all":
        return recommendations
    
    # Define minimum credit score values based on dropdown options
    credit_score_minimums = {
        "excellent": 750,  # Excellent (750+)
        "good": 700,       # Good (700-749)
        "fair": 650,       # Fair (650-699)
        "poor": 300        # Poor (Below 650)
    }
    
    # Get the user's minimum credit score
    user_min_score = credit_score_minimums.get(credit_score, 0)
    
    filtered_recommendations = []
    
    for rec in recommendations:
        # Find the card in the original data
        card_title = rec["title"]
        card_index = -1
        for i, name in enumerate(card_names):
            if name == card_title:
                card_index = i
                break
        
        if card_index == -1:
            # If card not found, include it
            filtered_recommendations.append(rec)
            continue
        
        # Get card's minimum required score
        card_min_score = min_credit_scores[card_index]
        
        # Process the card's minimum score
        try:
            if card_min_score == "N/A" or card_min_score is None:
                # No specific requirement, include it
                filtered_recommendations.append(rec)
                continue
            
            # Convert to integer if it's a string
            if isinstance(card_min_score, str):
                if card_min_score.isdigit():
                    card_min_score = int(card_min_score)
                else:
                    # Not a valid number, include the card
                    filtered_recommendations.append(rec)
                    continue
            
            # Include the card if the user's credit score is sufficient
            if user_min_score >= card_min_score:
                filtered_recommendations.append(rec)
                
        except Exception as e:
            print(f"Error processing card {card_title}: {e}")
            filtered_recommendations.append(rec)
    
    return filtered_recommendations

def filter_by_annual_fee(recommendations, annual_fee_preference):
    """
    Filter recommendations based on user's annual fee preference.
    """
    if not annual_fee_preference:
        return recommendations
    
    # Define annual fee thresholds based on dropdown options
    annual_fee_thresholds = {
        "no": 0,            # No annual fee
        "up-to-100": 100,   # Up to $100
        "up-to-250": 250,   # Up to $250
        "up-to-500": 500    # Up to $500
    }
    
    # Get the maximum annual fee the user is willing to pay
    max_fee = annual_fee_thresholds.get(annual_fee_preference, float('inf'))
    
    filtered_recommendations = []
    
    for rec in recommendations:
        # Find the card in the original data
        card_title = rec["title"]
        card_index = -1
        for i, name in enumerate(card_names):
            if name == card_title:
                card_index = i
                break
        
        if card_index == -1:
            # If card not found, include it
            filtered_recommendations.append(rec)
            continue
        
        # Get card's annual fee
        annual_fee = annual_fees[card_index]
        
        # Process the annual fee
        try:
            if annual_fee == "N/A" or annual_fee is None:
                # If annual fee is not specified, include the card
                filtered_recommendations.append(rec)
                continue
            
            # Extract numeric value from fee string
            if isinstance(annual_fee, str):
                # Remove $ and any other non-numeric characters
                fee_value = annual_fee.replace('$', '').strip()
                if fee_value == "0" or fee_value.lower() == "none":
                    fee_value = 0
                else:
                    # Try to extract numeric value
                    import re
                    numeric_match = re.search(r'\d+', fee_value)
                    if numeric_match:
                        fee_value = int(numeric_match.group())
                    else:
                        # Couldn't extract a fee, assume it's free
                        fee_value = 0
            else:
                fee_value = annual_fee
            
            # Convert to a number if it's still a string
            if isinstance(fee_value, str) and fee_value.isdigit():
                fee_value = int(fee_value)
            elif not isinstance(fee_value, (int, float)):
                # If not a valid number, include the card
                filtered_recommendations.append(rec)
                continue
            
            # Check if card's annual fee is within user's threshold
            if annual_fee_preference == "no" and fee_value == 0:
                # For "no annual fee" preference, only include cards with $0 fee
                filtered_recommendations.append(rec)
            elif annual_fee_preference != "no" and fee_value <= max_fee:
                # For other preferences, include cards up to the max fee
                filtered_recommendations.append(rec)
                
        except Exception as e:
            print(f"Error processing annual fee for card {card_title}: {e}")
            # In case of errors, include the card
            filtered_recommendations.append(rec)
    
    return filtered_recommendations

def get_recommendations(user_input, filters=None, offset=0, limit=3):
    """
    Compute cosine similarity between user input and stored credit card reviews,
    then apply filters based on user preferences.
    """
    if filters is None:
        filters = {}
        
    # user_vec = vectorizer.transform([user_input])
    # cosine_similarities = cosine_similarity(user_vec, tfidf_matrix).flatten()
    # sorted_indices = np.argsort(-cosine_similarities)  # Sort descending

    # Transform user input for both vectorizers
    desc_vec = vectorizer.transform([user_input])
    review_vec = user_review_vectorizer.transform([user_input])

    # Compute cosine similarities separately
    desc_sim = cosine_similarity(desc_vec, tfidf_matrix).flatten()
    review_sim = cosine_similarity(review_vec, user_review_matrix).flatten()

    # Define weights
    w1 = 0.7  # weight for description match
    w2 = 0.3  # weight for review match

    # Compute final weighted similarity
    final_sim = w1 * desc_sim + w2 * review_sim

    # Sort by final score
    sorted_indices = np.argsort(-final_sim)

    
    # # First get all potential recommendations
    # all_matches = []
    # for i in sorted_indices:
    #     # Scale cosine similarity to a percentage (0-100)
    #     similarity_score = float(cosine_similarities[i])
        
    #     # Convert to percentage without floor
    #     raw_percentage = similarity_score * 100
    #     match_percentage = int(min(raw_percentage, 99))
        
    #     # Include both the raw data and the calculated match percentage
    #     all_matches.append({
    #         "title": card_names[i],
    #         "category": categories[i],
    #         "annual_fee": annual_fees[i],
    #         "foreign_transaction_fee_value": foreign_transaction_fees[i],
    #         "similarity_score": similarity_score,
    #         "match_percentage": match_percentage
    #     })
    all_matches = []
    for i in sorted_indices:
        similarity_score = float(final_sim[i])
        raw_percentage = similarity_score * 100
        match_percentage = int(min(raw_percentage, 99))

        all_matches.append({
            "title": card_names[i],
            "category": categories[i],
            "annual_fee": annual_fees[i],
            "foreign_transaction_fee_value": foreign_transaction_fees[i],
            "similarity_score": similarity_score,
            "match_percentage": match_percentage
        })
        
    filtered_matches = all_matches
    
    # Apply credit score filter if specified
    credit_score = filters.get('creditScore')
    if credit_score:
        filtered_matches = filter_by_credit_score(filtered_matches, credit_score)
    
    # Apply annual fee filter if specified
    annual_fee = filters.get('annualFee')
    if annual_fee:
        filtered_matches = filter_by_annual_fee(filtered_matches, annual_fee)
    
    # Apply pagination
    total_matches = len(filtered_matches)
    paginated_matches = filtered_matches[offset:offset+limit]
    
    return paginated_matches, total_matches

@app.route("/")
def home():
    return render_template('base2.html', title="Card Match - Credit Card Recommender")

@app.route("/old")
def old_ui():
    return render_template('base.html', title="Card Match - Credit Card Recommender")

@app.route("/new")
def new_ui():
    return render_template('base2.html', title="Card Match - Credit Card Recommender")

@app.route("/filter-cards", methods=["POST"])
def filter_cards():
    """Handle the form submission for filtering cards."""
    credit_score = request.form.get('credit-score')
    
    # Log it to verify
    print(f"Credit Score selected: {credit_score}")
    
    # For simplicity, we'll redirect to the main page after processing
    # In a real app, you might want to pass this value to a template or return JSON
    return render_template('base2.html', title="Card Match - Credit Card Recommender")

@app.route("/recommend", methods=["POST", "GET"])
def recommend():
    """API endpoint to return credit card recommendations."""
    print("got to recommend")
    if request.method == "POST":
        data = request.json
        user_query = data.get("query", "")
        filters = data.get("filters", {})
        offset = data.get("offset", 0)
        limit = data.get("limit", 3)
    else:
        user_query = request.args.get("title", "")
        filters = {}
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 3))
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    recommendations, total_matches = get_recommendations(
        user_input=user_query, 
        filters=filters,
        offset=offset, 
        limit=limit
    )
    
    return jsonify({
        "recommendations": recommendations,
        "pagination": {
            "offset": offset,
            "limit": limit,
            "total": total_matches,
            "has_more": (offset + limit) < total_matches
        }
    })

if __name__ == "__main__":  # This is the correct way to run the app
    app.run(debug=True, host="0.0.0.0", port=5001)