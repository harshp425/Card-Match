#!/usr/bin/env python3
import json
import os
import re
import time
from pathlib import Path

"""
This script analyzes the credit card dataset and automatically adds
airline associations based on card names, descriptions, and other fields.
"""

print("Starting airline association script...")

# Define major airlines and their common variations
AIRLINES = {
    "delta": ["delta", "delta air", "skymiles"],
    "american": ["american", "american airlines", "aadvantage", "aa"],
    "united": ["united", "united airlines", "mileageplus"],
    "southwest": ["southwest", "southwest airlines", "rapid rewards"],
    "jetblue": ["jetblue", "jet blue", "trueblue"],
    "alaska": ["alaska", "alaska airlines", "alaska air"],
    "british airways": ["british airways", "british air", "avios"],
    "air france": ["air france", "flying blue"],
    "lufthansa": ["lufthansa", "miles & more"],
    "emirates": ["emirates", "emirates airlines", "skywards"],
    "hawaiian": ["hawaiian", "hawaiian airlines"],
    "frontier": ["frontier", "frontier airlines"],
    "spirit": ["spirit", "spirit airlines", "free spirit"],
    "virgin": ["virgin", "virgin atlantic", "virgin america"],
    "cathay pacific": ["cathay", "cathay pacific"],
    "singapore": ["singapore", "singapore airlines", "krisflyer"],
    "aeromexico": ["aeromexico", "aero mexico"],
    "air canada": ["air canada", "aeroplan"],
    "turkish": ["turkish", "turkish airlines", "miles&smiles"],
    "asiana": ["asiana", "asiana airlines"]
}

print(f"Loaded {len(AIRLINES)} airline references")

# Hotel chains for future use
HOTEL_CHAINS = {
    "marriott": ["marriott", "bonvoy", "westin", "sheraton", "ritz-carlton", "ritz carlton"],
    "hilton": ["hilton", "hilton honors", "conrad", "waldorf astoria"],
    "hyatt": ["hyatt", "world of hyatt", "grand hyatt", "park hyatt"],
    "ihg": ["ihg", "intercontinental", "holiday inn", "crowne plaza"],
    "wyndham": ["wyndham", "wyndham rewards", "days inn", "ramada", "super 8"],
    "choice": ["choice", "choice privileges", "comfort inn", "quality inn", "econo lodge"],
    "best western": ["best western", "best western rewards"],
    "radisson": ["radisson", "radisson rewards", "country inn", "park inn"]
}

print(f"Loaded {len(HOTEL_CHAINS)} hotel chain references")

# Define income tiers based on annual fee
def get_income_tier(annual_fee):
    if annual_fee in (None, "N/A", "-1", "$0", "None", "none", "0"):
        return "any"  # No annual fee cards are accessible to most income levels
    
    # Try to extract numeric value from fee
    fee_value = 0
    if isinstance(annual_fee, str):
        match = re.search(r'\$?(\d+)', annual_fee)
        if match:
            fee_value = int(match.group(1))
    elif isinstance(annual_fee, (int, float)):
        fee_value = annual_fee
    
    # Assign tier based on fee amount
    if fee_value == 0:
        return "any"
    elif fee_value <= 95:
        return "low"  # $1-95 annual fee
    elif fee_value <= 250:
        return "medium"  # $96-250 annual fee
    elif fee_value <= 550:
        return "high"  # $251-550 annual fee
    else:
        return "premium"  # $551+ annual fee

# Define travel value score based on card attributes
def calculate_travel_value(card_data):
    score = 5.0  # Start with neutral score
    
    # Category boosts
    category = card_data.get("category", "").lower()
    if "travel" in category:
        score += 2.0
    if "miles" in category:
        score += 1.5
    if "hotel" in category:
        score += 1.0
    
    # No foreign transaction fee is huge for travelers
    foreign_fee = card_data.get("foreign_transaction_fee_value", "").lower()
    if "0%" in foreign_fee or "none" in foreign_fee or "no foreign" in foreign_fee:
        score += 2.0
    
    # Points, miles, or general travel rewards
    if card_data.get("reward_rate_string_2018") and "miles" in card_data.get("reward_rate_string_2018", "").lower():
        score += 1.0
    
    # Travel benefits in description
    description = (
        card_data.get("pros_value", "") + " " +
        card_data.get("our_take_value", "") + " " +
        card_data.get("offer_details_value", "")
    ).lower()
    
    if "travel credit" in description or "airline credit" in description:
        score += 1.0
    if "priority pass" in description or "lounge access" in description:
        score += 1.5
    if "global entry" in description or "tsa precheck" in description:
        score += 0.5
    if "companion" in description and ("ticket" in description or "fare" in description):
        score += 1.0
    
    # Cap the score at 10
    return min(round(score, 1), 10.0)

def update_dataset():
    print("-" * 50)
    print("DATASET ENHANCEMENT PROCESS STARTING")
    print("-" * 50)
    
    start_time = time.time()
    dataset_path = Path(__file__).parent.parent / "dataset" / "dataset.json"
    # Use the same path for output to update the current dataset directly
    output_path = dataset_path
    
    print(f"Reading dataset from: {dataset_path}")
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Successfully loaded JSON data")
    except Exception as e:
        print(f"❌ Error reading dataset: {e}")
        return
    
    # Create a backup of the original dataset
    backup_path = Path(__file__).parent.parent / "dataset" / "dataset_backup.json"
    try:
        print(f"Creating backup at: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Backup created successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not create backup: {e}")
        response = input("Continue without backup? (y/n): ")
        if response.lower() != 'y':
            print("Aborting process.")
            return
    
    print(f"Processing {len(data)} cards...")
    cards_updated = 0
    cards_with_airlines = 0
    progress_interval = max(1, len(data) // 20)  # Show progress every 5%
    
    for i, card in enumerate(data):
        # Show progress every few cards
        if (i + 1) % progress_interval == 0 or i == 0 or i == len(data) - 1:
            percent_done = (i + 1) / len(data) * 100
            print(f"⏳ Processing card {i+1}/{len(data)} [{percent_done:.1f}%]")
        
        # Create search text from relevant fields
        search_text = (
            (card.get("name", "") + " " +
            card.get("short_card_name", "") + " " +
            card.get("trademark_card_name", "") + " " +
            card.get("category", "") + " " +
            card.get("bonus_offer_value", "") + " " +
            card.get("rewards_rate_value", "") + " " +
            card.get("our_take_value", "")).lower()
        )
        
        # Find airline associations
        associated_airlines = []
        for airline, keywords in AIRLINES.items():
            for keyword in keywords:
                if keyword in search_text:
                    associated_airlines.append(airline)
                    break  # Found one keyword for this airline
        
        # Remove duplicates and sort
        associated_airlines = sorted(list(set(associated_airlines)))
        
        # Calculate income tier
        income_tier = get_income_tier(card.get("annual_fee_value"))
        
        # Calculate travel value score
        travel_value = calculate_travel_value(card)
        
        # Track detailed information for a sample of cards
        if i < 5 or i % (len(data) // 10) == 0:  # First 5 cards and every 10%
            card_name = card.get("name", "Unknown Card")
            print(f"\n📊 CARD DETAIL: {card_name}")
            print(f"   - Income Tier: {income_tier}")
            print(f"   - Travel Value: {travel_value}")
            print(f"   - Airlines: {', '.join(associated_airlines) if associated_airlines else 'None'}")
        
        # Add new fields only if they don't exist or we want to update
        if "associated_airlines" not in card or associated_airlines:
            card["associated_airlines"] = associated_airlines
            cards_updated += 1
            if associated_airlines:
                cards_with_airlines += 1
        
        if "income_tier" not in card:
            card["income_tier"] = income_tier
        
        if "travel_value_score" not in card:
            card["travel_value_score"] = travel_value
    
    # Save updated dataset
    try:
        print("\n📝 Saving enhanced dataset back to the original file...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        elapsed_time = time.time() - start_time
        print(f"✅ Updated {cards_updated} cards total")
        print(f"✅ Found {cards_with_airlines} cards with airline associations")
        print(f"✅ Dataset updated successfully at: {output_path}")
        print(f"⏱️ Process completed in {elapsed_time:.2f} seconds")
    except Exception as e:
        print(f"❌ Error saving enhanced dataset: {e}")
        print(f"⚠️ If needed, you can restore from the backup at: {backup_path}")
    
    print("-" * 50)
    print("PROCESS COMPLETE")
    print("-" * 50)

if __name__ == "__main__":
    print("Script execution started")
    update_dataset()
    print("Script execution finished") 