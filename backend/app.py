# app.py

import json
import os
import re
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.decomposition import TruncatedSVD

# Set up Flask
app = Flask(__name__)
CORS(app)

# Load the dataset
current_directory = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(current_directory, 'dataset', 'dataset.json')
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Pre-extract fields for recommendation math
card_names = [entry["name"] for entry in data]
reviews = [entry.get("our_take_value", "") for entry in data]
categories = [entry.get("category", "") for entry in data]
annual_fees = [entry.get("annual_fee_value", "N/A") for entry in data]
foreign_transaction_fees = [entry.get("foreign_transaction_fee_value", "N/A") for entry in data]
min_credit_scores = [entry.get("credit_score_low", "N/A") for entry in data]
issuers = [entry.get("issuer", "") for entry in data]
user_reviews = ["     ".join(entry.get("user_reviews", [])) for entry in data]
bonus_offers = [entry.get("bonus_offer_value", "") for entry in data]
short_card_names = [entry.get("short_card_name", "") for entry in data]
pros_value = [entry.get("pros_value", "") for entry in data]


# Build TF-IDF + SVD matrices
informed_description = [
    f"{rev} {pros_value[i]} issuer: {issuers[i]} card name: {card_names[i]}/{short_card_names[i]} card name: {card_names[i]}/{short_card_names[i]} card name: {card_names[i]}/{short_card_names[i]} category: {categories[i]} category: {categories[i]}"
    for i, rev in enumerate(reviews)
]
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix_raw = vectorizer.fit_transform(informed_description)
svd = TruncatedSVD(n_components=130, random_state=42)
tfidf_matrix = svd.fit_transform(tfidf_matrix_raw)

user_review_vectorizer = TfidfVectorizer(stop_words="english")
user_review_matrix_raw = user_review_vectorizer.fit_transform(user_reviews)
user_svd = TruncatedSVD(n_components=130, random_state=42)
user_review_matrix = user_svd.fit_transform(user_review_matrix_raw)

def filter_by_credit_score(recommendations, credit_score):
    if not credit_score or credit_score == "all":
        return recommendations

    credit_score_minimums = {
        "excellent": 750,
        "good": 700,
        "fair": 650,
        "poor": 300
    }
    user_min_score = credit_score_minimums.get(credit_score, 0)
    filtered = []

    for rec in recommendations:
        title = rec["title"]
        idx = next((i for i,n in enumerate(card_names) if n == title), -1)
        if idx == -1:
            filtered.append(rec)
            continue

        card_req = min_credit_scores[idx]
        try:
            if card_req in (None, "N/A"):
                filtered.append(rec)
                continue
            if isinstance(card_req, str) and card_req.isdigit():
                card_req = int(card_req)
            if user_min_score >= card_req:
                filtered.append(rec)
        except:
            filtered.append(rec)

    return filtered

def filter_by_annual_fee(recommendations, annual_fee_preference):
    if not annual_fee_preference:
        return recommendations

    annual_fee_thresholds = {
        "no": 0,
        "up-to-100": 100,
        "up-to-250": 250,
        "up-to-500": 500,
        "up-to-700": 700
    }
    max_fee = annual_fee_thresholds.get(annual_fee_preference, float('inf'))
    filtered = []

    for rec in recommendations:
        title = rec["title"]
        idx = next((i for i,n in enumerate(card_names) if n == title), -1)
        if idx == -1:
            filtered.append(rec)
            continue

        fee_raw = annual_fees[idx]
        try:
            if fee_raw in (None, "N/A"):
                filtered.append(rec)
                continue

            fee_str = str(fee_raw).replace('$', '').strip()
            if fee_str.lower() in ("0", "none"):
                fee_value = 0
            else:
                m = re.search(r'\d+', fee_str)
                fee_value = int(m.group()) if m else 0

            if annual_fee_preference == "no":
                if fee_value == 0:
                    filtered.append(rec)
            elif fee_value <= max_fee:
                filtered.append(rec)
        except:
            filtered.append(rec)

    return filtered

def get_recommendations(user_input, filters=None, offset=0, limit=3):
    if filters is None:
        filters = {}

    # similarity on description
    desc_vec = svd.transform(vectorizer.transform([user_input]))
    review_vec = user_svd.transform(user_review_vectorizer.transform([user_input]))
    desc_sim = cosine_similarity(desc_vec, tfidf_matrix).flatten()
    review_sim = cosine_similarity(review_vec, user_review_matrix).flatten()
    final_sim = 0.7 * desc_sim + 0.3 * review_sim

    sorted_idx = np.argsort(-final_sim)
    matches = []
    for i in sorted_idx:
        sim = float(final_sim[i])
        pct = int(min(sim * 100, 99))
        top_raw_reviews = []
        for rev in data[i].get("user_reviews", []):
            try:
                rv = user_review_vectorizer.transform([rev])
                rv_svd = user_svd.transform(rv)
                score = float(cosine_similarity(review_vec, rv_svd).flatten()[0])
                top_raw_reviews.append((rev, score))
            except:
                continue
        top_raw_reviews.sort(key=lambda x: x[1], reverse=True)
        reviews_out = [{"text": r, "score": s} for r,s in top_raw_reviews[:3]]

        matches.append({
            "title":                     card_names[i],
            "category":                  categories[i],
            "annual_fee":                annual_fees[i],
            "foreign_transaction_fee_value": foreign_transaction_fees[i],
            # these two lines are new:
            "reward_rate_string_2018":   data[i].get("reward_rate_string_2018", ""),
            "intro_apr_check_value":     data[i].get("intro_apr_check_value", ""),

            "similarity_score":          sim,
            "match_percentage":          pct,
            "reviews":                   reviews_out,
            "bonus_offer_value":         bonus_offers[i],
            "image_url":                 data[i].get("image_url", "")
        })

    # apply filters
    if filters.get("creditScore"):
        matches = filter_by_credit_score(matches, filters["creditScore"])
    if filters.get("annualFee"):
        matches = filter_by_annual_fee(matches, filters["annualFee"])

    total = len(matches)
    return matches[offset:offset+limit], total

@app.route("/")
def home():
    return render_template('base2.html', title="Card Match - Credit Card Recommender")

@app.route("/filter-cards", methods=["POST"])
def filter_cards():
    credit_score = request.form.get('credit-score')
    # you could store that in session or pass to template
    return render_template('base2.html', title="Card Match - Credit Card Recommender")

@app.route("/recommend", methods=["POST"])
def recommend():
    data_in = request.get_json()
    query = data_in.get("query", "")
    filters = data_in.get("filters", {})
    offset = data_in.get("offset", 0)
    limit = data_in.get("limit", 3)

    if not query:
        return jsonify({"error": "No query provided"}), 400

    recs, total = get_recommendations(query, filters, offset, limit)
    return jsonify({
        "recommendations": recs,
        "pagination": {
            "offset": offset,
            "limit": limit,
            "total": total,
            "has_more": (offset + limit) < total
        }
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
