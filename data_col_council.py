# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:57:24 2025

@author: ShupingWang
"""


import pandas as pd

state_fips = pd.read_csv('data/national_state2020.txt', sep='|')  


import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

# Create a dictionary mapping FIPS codes to Fishery Management Council IDs
fips_to_council = {
    '01': 4,  # Alabama
    '02': 6,  # Alaska
    '04': 0,  # Arizona
    '05': 0,  # Arkansas
    '06': 5,  # California
    '08': 0,  # Colorado
    '09': 1,  # Connecticut
    '10': 2,  # Delaware
    '11': 0,  # District of Columbia
    '12': 3,  # Florida
    '13': 3,  # Georgia
    '15': 8,  # Hawaii
    '16': 0,  # Idaho
    '17': 0,  # Illinois
    '18': 0,  # Indiana
    '19': 0,  # Iowa
    '20': 0,  # Kansas
    '21': 0,  # Kentucky
    '22': 4,  # Louisiana
    '23': 1,  # Maine
    '24': 2,  # Maryland
    '25': 1,  # Massachusetts
    '26': 0,  # Michigan
    '27': 0,  # Minnesota
    '28': 4,  # Mississippi
    '29': 0,  # Missouri
    '30': 0,  # Montana
    '31': 0,  # Nebraska
    '32': 0,  # Nevada
    '33': 1,  # New Hampshire
    '34': 2,  # New Jersey
    '35': 0,  # New Mexico
    '36': 2,  # New York
    '37': 2,  # North Carolina
    '38': 0,  # North Dakota
    '39': 0,  # Ohio
    '40': 0,  # Oklahoma
    '41': 5,  # Oregon
    '42': 2,  # Pennsylvania
    '44': 1,  # Rhode Island
    '45': 3,  # South Carolina
    '46': 0,  # South Dakota
    '47': 0,  # Tennessee
    '48': 4,  # Texas
    '49': 0,  # Utah
    '50': 0,  # Vermont
    '51': 2,  # Virginia
    '53': 5,  # Washington
    '54': 0,  # West Virginia
    '55': 0,  # Wisconsin
    '56': 0,  # Wyoming
    '60': 8,  # American Samoa
    '66': 8,  # Guam
    '69': 8,  # Northern Mariana Islands
    '72': 7,  # Puerto Rico
    '74': 8,  # U.S. Minor Outlying Islands
    '78': 7   # U.S. Virgin Islands
}

# Create a dictionary to map council IDs to council names
council_names = {
    0: 'No Council',
    1: 'New England',
    2: 'Mid-Atlantic',
    3: 'South Atlantic',
    4: 'Gulf of Mexico',
    5: 'Pacific',
    6: 'North Pacific',
    7: 'Caribbean',
    8: 'Western Pacific'
}

# Function to map state FIPS to council names
def get_council_name(fips):
    if fips in fips_to_council:
        council_id = fips_to_council[fips]
        return council_names[council_id]
    return 'Unknown'

# Create a sample dataframe to test the mapping
def create_sample_dataframe():
    data = []
    for fips, council_id in fips_to_council.items():
        data.append({
            'STATEFP': fips,
            'council_id': council_id,
            'council_name': council_names[council_id]
        })
    return pd.DataFrame(data)

# Function to merge the council data with state shapefiles
def create_fishery_council_map(state_shapefile_path):
    # Read the state shapefile
    states = gpd.read_file(state_shapefile_path)
    
    # Ensure STATEFP is a string with leading zeros
    states['STATEFP'] = states['STATEFP'].astype(str).str.zfill(2)
    
    # Add council ID and name columns
    states['council_id'] = states['STATEFP'].map(fips_to_council)
    states['council_name'] = states['council_id'].map(council_names)
    
    # Create a map
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    states.plot(column='council_id', 
                categorical=True, 
                legend=True, 
                ax=ax, 
                cmap='tab10',
                legend_kwds={'title': 'Fishery Management Council'})
    
    # Add labels for council names in the legend
    handles, labels = ax.get_legend_handles_labels()
    new_labels = [f"{label} - {council_names[int(label)]}" for label in labels]
    ax.legend(handles, new_labels, title='Fishery Management Council', loc='lower right')
    
    ax.set_title('U.S. Fishery Management Councils by State', fontsize=16)
    ax.set_axis_off()
    
    plt.tight_layout()
    plt.savefig('fishery_management_councils_map.png', dpi=300)
    plt.show()
    
    return states

# Export mapping to CSV
def export_mapping():
    df = create_sample_dataframe()
    df.to_csv('fishery_council_mapping.csv', index=False)
    print("Mapping exported to 'fishery_council_mapping.csv'")

# Example usage:
# 1. Create and export the mapping table
export_mapping()

# 2. If you have a state shapefile, create a map
# Uncomment the following line and provide the path to your shapefile
states_with_councils = create_fishery_council_map('data/tl_2019_us_state.zip')

# For demonstration purposes, let's show how to use the mapping
sample_states = ['06', '12', '36', '53']  # California, Florida, New York, Washington
for state in sample_states:
    print(f"State FIPS {state} belongs to the {get_council_name(state)} Fishery Management Council")
