import csv
import requests
import re
import pubchempy as pcp

# Load compound names from a CSV file
input_csv_path = 'compound_list.csv'
output_csv_path = 'compound_pubchem_identifiers.csv'

def get_compound_name_from_cid(cid):
    """Retrieve compound name(s) for a given CID from PubChem."""
    base_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'
    # Use the /description endpoint to get compound names
    response = requests.get(f'{base_url}/compound/cid/{cid}/description/JSON')
    if response.status_code == 200:
        data = response.json()
        # Extract the title from the description, which typically contains the compound name
        name = data.get('InformationList', {}).get('Information', [])[0].get('Title', 'No name found')
        return name
    else:
        # Handle cases where the API call fails
        return 'No name found'

def get_cas_number_from_cid(cid):
    """Retrieve CAS number for a given CID from PubChem."""
    base_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'
    # Use the /synonyms endpoint to get CAS numbers
    response = requests.get(f'{base_url}/compound/cid/{cid}/synonyms/JSON')
    if response.status_code == 200:
        data = response.json()
        # Extract the synonyms list, which includes the CAS number
        synonyms = data.get('InformationList', {}).get('Information', [])[0].get('Synonym', [])
        # Search for a string that matches the format of a CAS number
        for synonym in synonyms:
            if "-" in synonym and len(synonym.split("-")) == 3:
                try:
                    int(synonym.split("-")[0])  # Simple check to see if the first part is a number
                    return synonym  # Assuming the first valid format found is the CAS number
                except ValueError:
                    continue
        return 'No CAS number found'
    else:
        # Handle cases where the API call fails
        return 'No CAS number found'


def get_sids_from_cid(cid):
    """Retrieve SIDs for a given CID from PubChem."""
    base_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'
    response = requests.get(f'{base_url}/compound/cid/{cid}/sids/JSON')
    if response.status_code == 200:
        data = response.json()
        sids = data.get('InformationList', {}).get('Information', [])[0].get('SID', [])
        return [str(sid) for sid in sids[:150]]
    return []


with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile, open(output_csv_path, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = ['compound_name', 
                  'pubchem_cid', 
                  'pubchem_name', 
                  'pubchem_cas', 
                  'pubchem_synonyms', 
                  'pubchem_sids']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        compound_name = row['compound_name']
        compounds = pcp.get_compounds(compound_name, 'name')
        if compounds:
            for compound in compounds:
                cids = compound.cid
                synonyms = '; '.join(compound.synonyms[:20]) if compound.synonyms else 'No synonyms found'
                pubchem_name = get_compound_name_from_cid(compound.cid)
                pubchem_CAS = get_cas_number_from_cid(compound.cid)
                sids = get_sids_from_cid(compound.cid)
                writer.writerow({
                    'compound_name': compound_name,
                    'pubchem_cid': compound.cid,
                    'pubchem_name' : pubchem_name,
                    'pubchem_cas' : pubchem_CAS,
                    'pubchem_synonyms': synonyms,
                    'pubchem_sids': '; '.join(sids)
                })
        else:
            writer.writerow({
                'compound_name': compound_name,
                'pubchem_cid': 'No pubchem compund',
                'pubchem_name' : 'NA',
                'pubchem_cas' : 'NA',
                'pubchem_synonyms': 'NA',
                'pubchem_sids': 'NA'
            })

print(f"Search completed and results saved to '{output_csv_path}'.")
