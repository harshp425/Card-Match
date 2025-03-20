import csv
import json

def csv_to_json(csv_file_path, json_file_path):
    # Create an empty list to store the rows as dictionaries
    data = []
    
    # Open and read the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        # Create a CSV reader object
        csv_reader = csv.DictReader(csv_file)
        
        # Convert each row to a dictionary and append to data list
        for row in csv_reader:
            data.append(row)
    
    # Write the data list to a JSON file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        # Ensure proper indentation for readability
        json.dump(data, json_file, indent=4)
    
    print(f"Successfully converted {csv_file_path} to {json_file_path}")

# Example usage
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(base_dir, "/Users/harshpatel/Downloads/cs4300/4300-Flask-Template-JSON/CreditCardCardRaw - Main (1).csv")  # Replace with your CSV file path
    json_file_path = os.path.join(base_dir, "/Users/harshpatel/Downloads/cs4300/4300-Flask-Template-JSON/backend/dataset/dataset.json")  # Replace with your desired JSON file path
    csv_to_json(csv_file_path, json_file_path)
