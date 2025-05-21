# [Card Match](http://4300showcase.infosci.cornell.edu:5254/) 

Card Match is a web app that is designed to help users find the most relevant credit cards based on their preferences and spending habits. By combining text-based search, dimensionality reduction, and sentiment analysis, the app intelligently recommends cards that align with the user’s needs—whether they're looking for travel perks, cashback, student-friendly options, or premium benefits.

## Overview

This project combines natural language processing and machine learning techniques to build a personalized credit card recommendation engine. It aims to return results that are not only relevant to a user's query but also backed by real-world user sentiment. Below is a breakdown of how each major element contributes to the system:

- **TF-IDF (Term Frequency–Inverse Document Frequency)**
  - Used to convert both the user query and credit card descriptions into numerical vectors.
  - Helps quantify the importance of terms relative to all card descriptions.
  - Captures the lexical (exact word-based) similarity between the user's input and card text.

- **SVD (Singular Value Decomposition)**
  - Performs dimensionality reduction on the high-dimensional TF-IDF matrix.
  - Projects both cards and the user query into a lower-dimensional latent semantic space.
  - Helps capture deeper relationships between words and phrases (e.g., recognizing that “airline miles” and “travel rewards” are semantically related).
  - Reduces noise and sparsity, improving ranking performance and query generalization.

- **Cosine Similarity**
  - Measures similarity between the user query vector and each credit card vector in the latent space.
  - Cards are sorted in descending order of similarity to the query.
  - Allows the system to surface cards even if they don’t share exact keywords but are conceptually similar.

- **Sentiment Analysis**
  - Applied to user reviews of each credit card using a pretrained transformer model (e.g., RoBERTa-based).
  - Produces an aggregated sentiment score (e.g., weighted average of positive/neutral/negative sentiments).
  - Helps differentiate between cards that may be similar in features but vary in user satisfaction.
  - Cards with consistently negative feedback are ranked lower, even if their feature match is strong.

- **Feature-Based Filtering and Bonus Scoring**
  - Certain card attributes (e.g., “no foreign transaction fees,” “0% APR,” “good for students”) are parsed and weighted based on query intent.
  - If the query includes explicit feature preferences (e.g., “no annual fee”), cards with matching features receive a scoring boost.
  - Enhances personalization and ensures that cards meeting practical constraints are prioritized.

- **Final Scoring Formula**
  - The final card ranking is based on a composite score:
    ```
    final_score = α * semantic_similarity + β * sentiment_score + γ * feature_bonus
    ```
  - `α`, `β`, and `γ` are configurable weights that balance relevance, quality, and personalization.
  - This flexible structure allows experimentation and fine-tuning based on user feedback or business objectives.

- **Explainability Layer**
  - Each recommendation is presented with an explanation, including:
    - Why it matched the query (e.g., “matched on ‘cashback on groceries’”)
    - How well users rate the card (via sentiment score)
    - Any standout features (e.g., “no annual fee,” “travel protection”)
  - Improves transparency and user trust in the system's recommendations.

---

## Technologies & Libraries

### Backend
- **Python 3.9+**
- **Flask** – lightweight backend framework for routing and serving recommendations
- **scikit-learn** – used for TF-IDF vectorization and SVD (Singular Value Decomposition)
- **NLTK / spaCy** – for preprocessing, tokenization, and stopword removal
- **Pandas & NumPy** – for data handling and manipulation

### Sentiment Analysis
- **HuggingFace Transformers** – optionally used for sentiment scoring of reviews (e.g., `cardiffnlp/twitter-roberta-base-sentiment` or custom fine-tuned models)

### Frontend
- **HTML / CSS / Bootstrap** – simple UI for input and displaying ranked credit card recommendations
- **JavaScript** – for dynamic query suggestions and form handling

---

## Features

### 1. **User Query Processing**
Users input a short description of what they're looking for in a card (e.g., _"best for travel and no foreign fees"_). The backend processes this input using:

- **TF-IDF vectorization** to represent the query and each card’s description.
- **SVD** reduces the dimensionality of the TF-IDF matrix to capture deeper semantic similarity.

The query is then transformed into the same latent space and compared against all card vectors using cosine similarity.

---

### 2. **Card Ranking Mechanics**

Cards are ranked using a hybrid of:

- **Semantic similarity** between the user query and card descriptions/features.
- **Weighted sentiment scores** extracted from user reviews for each card.
  - For example, a card with high similarity but negative reviews may be ranked lower than a similar card with strong positive sentiment.
- **Bonus Boosts:** Certain features like “no annual fee,” “student friendly,” or “travel insurance” can optionally be given extra weight based on common user priorities.

### 3. **Interpretability**
Each recommendation comes with:

- A **similarity score** showing how well it matches the query
- A **sentiment score** aggregated from card reviews
- A brief **explanation**: e.g., “Matched for travel + no foreign transaction fees with strong user sentiment on rewards”

---

## Dataset

The app uses a curated dataset of credit cards with:
- Card descriptions & features
- Structured metadata (e.g., annual fee, type, issuer)
- User reviews (scraped or sourced via API)

All data is stored in `data/cards.csv` and `data/reviews.csv`.

---

## Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/harshp425/Card-Match.git
cd Card-Match
```
### 2. Install Dependecies
```bash
pip install -r requirements.txt
```
### 3. Run App
```bash
flask run
```
