import requests
import json
import os
import csv

# Path to the input CSV file
input_csv_path = 'compound_pubchem_identifiers.csv'

def check_file_exists(sid, compound_name, folder_path):
    """Check if the file for a given SID and compound name already exists."""
    sanitized_name = "".join([c for c in compound_name if c.isalnum() or c in " _-"]).rstrip()
    file_name = f"{sanitized_name}_{sid}_classification.json"  # File name format
    file_path = os.path.join(folder_path, file_name)
    return os.path.exists(file_path), file_path

def save_sid_classification_json(sid, compound_name, folder_path):
    """Download classification JSON for a given SID and save to a text file."""
    base_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'
    response = requests.get(f'{base_url}/substance/sid/{sid}/classification/JSON')
    
    os.makedirs(folder_path, exist_ok=True)  # Ensure the directory exists
    exists, file_path = check_file_exists(sid, compound_name, folder_path)
    
    if exists:
        return False, f"{compound_name} searched by {sid} is already in the directory."
    
    if response.status_code == 200:
        data = response.json()
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True, f"JSON saved for SID {sid} of {compound_name}"
    else:
        return False, f"Failed to fetch classification JSON for SID {sid}"

folder_path = 'class-json-sid'  # Define the folder path for saving classification JSON files

# Read the CSV and process each row
with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    
    for row in reader:
        compound_name = row['compound_name']
        sids = row['pubchem_sids'].split('; ')
        
        for sid in sids:
            sid = sid.strip()
            if not sid.isdigit():
                print(f"Skipping {compound_name} due to non-numeric SID: {sid}")
                continue
            
            success, message = save_sid_classification_json(sid, compound_name, folder_path)
            print(message)
