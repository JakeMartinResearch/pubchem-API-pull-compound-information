import json
import csv
import os

def extract_mesh_names(node, names):
    """
    Recursively extracts the names from the MeSH Tree.
    """
    if node.get("Information", {}).get("Name"):
        name = node["Information"]["Name"]
        names.append(name)
    
    for child in node.get("Node", []):
        extract_mesh_names(child, names)

def get_processed_sids(output_csv_file):
    """
    Checks if the output CSV file exists and reads it to find out which SIDs have already been processed.
    Returns a set of SIDs that have been processed.
    """
    processed_sids = set()
    if os.path.exists(output_csv_file):
        with open(output_csv_file, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip the header
            for row in reader:
                if row:  # Check if the row is not empty
                    processed_sids.add(row[1])  # Assuming SID is the second column
    return processed_sids

def process_json_files(directory, output_csv_file):
    """
    Processes all JSON files in the specified directory and writes the output to a CSV file,
    skipping files for which the SID has already been processed.
    """
    processed_sids = get_processed_sids(output_csv_file)
    file_exists = os.path.exists(output_csv_file)

    with open(output_csv_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:  # If file doesn't exist, write the header
            writer.writerow(['Compound Name', 'SID', 'MeSH Names'])

        for filename in os.listdir(directory):
            if filename.endswith('_classification.json'):
                compound_name, sid = filename.split('_')[:2]
                
                if sid not in processed_sids:  # Skip if SID has already been processed
                    with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        for hierarchy in data.get('Hierarchies', {}).get('Hierarchy', []):
                            if hierarchy.get("SourceName") == "Medical Subject Headings (MeSH)" and hierarchy.get("Information", {}).get("Name") == "MeSH Tree":
                                mesh_names = []
                                extract_mesh_names(hierarchy, mesh_names)
                                writer.writerow([compound_name, sid, '; '.join(mesh_names)])

def remove_exact_duplicate_entries(input_csv_file, output_csv_file):
    seen = set()
    unique_rows = []

    with open(input_csv_file, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            identifier = f"{row['Compound Name']}_{row['SID']}_{row['MeSH Names']}"
            if identifier not in seen:
                seen.add(identifier)
                unique_rows.append(row)

    fieldnames = ['Compound Name', 'SID', 'MeSH Names']
    
    with open(output_csv_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in unique_rows:
            writer.writerow(row)

if __name__ == "__main__":
    directory = 'class-json-sid'  # Update this to your directory path
    temp_output_csv_file = 'mesh_tree_classifications_temp.csv'
    final_output_csv_file = 'mesh_tree_classifications.csv'
    
    process_json_files(directory, temp_output_csv_file)
    remove_exact_duplicate_entries(temp_output_csv_file, final_output_csv_file)
    os.remove(temp_output_csv_file)  # Clean up the temporary file
    
    print(f'Data has been processed and exact duplicates removed from {final_output_csv_file}.')
