import json
import pandas as pd

# Load the JSON file
with open("/Users/rpking/Documents/CS4300/4300-Flask-Template-JSON/backend/dataset/dataset.json", "r") as f:
    data = json.load(f)

# Load the CSV file
csv_data = pd.read_csv("/Users/rpking/Documents/CS4300/4300-Flask-Template-JSON/CreditCardCardRaw - Main (1).csv")  # replace with your actual file name

# Create a lookup dictionary from the CSV
csv_lookup = {
    row["name"]: {
        "credit_score_low": str(row["credit_score_low"]),
        "credit_score_high": str(row["credit_score_high"])
    }
    for _, row in csv_data.iterrows()
}

# Update the JSON data
for card in data:
    name = card.get("name")
    if name in csv_lookup:
        card["credit_score_low"] = csv_lookup[name]["credit_score_low"]
        card["credit_score_high"] = csv_lookup[name]["credit_score_high"]

# Save the updated JSON
with open("/Users/rpking/Documents/CS4300/4300-Flask-Template-JSON/backend/dataset/dataset.json", "w") as f:
    json.dump(data, f, indent=2)
