import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
"""
An API key is needed in .env file for this code
Column that has your species info in your excel file name should be "Species" and should contain species name such as Gavia stellata (Pontoppidan, 1763).
This code works for Mediterranean and Global assessments.
"""

def get_optimal(output):
    """
    Returns Mediterranean, Global or European or Asian description, our preference is Mediterranean first and Global second as we are a Mediterranean country
    in IUCN standarts. 
    Output is a dictionary
    """
    for item in output:
        if  "{'en': 'Mediterranean'}" in str(item):
            return item

    for item in output:
        if  "{'en': 'Global'}" in str(item):
            return item
        
def get_ids(item):
    """
    Returns the assessment id that is needed for the second api call in order to get red list category of a given species
    Output is a number
    """
    return  item["assessment_id"]

def get_names(string):
    """
    Returns genus name and species name
    """
    genus_name = string.split()[0]
    species_name = string.split()[1]
    print(genus_name, species_name)
    return genus_name, species_name

def get_assessment(response2):
    """
    A second call for the api that is needed for the Red List Category of a given species. 
    Returns the IUCN Red List Assessment of given species 
    Outputs: 
    {
    Extinct (EX)
    Extinct in the wild (EW)
    Critically endangered (CR)
    Endangered (EN) 
    Vulnerable (VU) 
    Near Threatened (NT)
    Lower Risk (LR) 
    Data Deficient (DD)
    Not Evaluated (NE)
    }
    """
    assessment_id = get_ids(response2)
    response2 = requests.get(f"https://api.iucnredlist.org/api/v4/assessment/{assessment_id}", headers=headers)
    red_list = json.loads(response2.text).get("red_list_category",{}).get("code",{})
    return print(red_list)

def get_species(genus_name, species_name):
    """
    Checks if species has assessment in IUCN and if it has takes the latest assessments
    Returns species assessment
    """
    response = requests.get(f"https://api.iucnredlist.org/api/v4/taxa/scientific_name?genus_name={genus_name}&species_name={species_name}", headers=headers)
    assessment = json.loads(response.text)
    if "assessments" not in assessment:
        print("Not evaluated")
        return
    assess = assessment["assessments"]
    output = [x for x in assess if x["latest"]==True] #arranges output file so that only latest assessments are taken into account
    return get_assessment(get_optimal(output))

api_key = os.getenv('IUCN_API_TOKEN')

headers = {
    "accept": "application/json",
    "Authorization": api_key,
}

df = pd.read_excel(input("Enter file path: "))
for index, i in df.iterrows():
    genus_name, species_name = get_names(i["Species"])
    get_species(genus_name, species_name)