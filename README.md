This serious of pyhtons scripts are used to pull compound infomartion from the PubChem database. 

## pubchem-pull-identifiers.py
This script take a CSV input (compound_list.csv) with compound names (compound_name), which it will search via the PubChem API using pubchempy to pull the PubChem CID, PubChem Name, (pubchem_name), PubChem CAS, PubChem Synonyms, and PubChem SIDs. These are outptued as a CSV file (compound_pubchem_identifiers.csv).

## pubchem-pull-compound-classifcation-json.py
This sciprt takes a CSV input (compound_pubchem_identifiers.csv) with compound names and assocated PubChem SIDs (i.e. the data genrated in pubchem-pull-identifiers.py), to search the classifcation metadata using the SIDs and pull the corresponding json structures. 

## pubchem-json-mesh-atc-extract.py
This script restructures json classfications from PubChem into a CSV output with as ';' sepreated list. 
